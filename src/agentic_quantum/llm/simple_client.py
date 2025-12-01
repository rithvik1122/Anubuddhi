"""
Simple LLM client for OpenRouter API integration.
"""

import os
import logging
from typing import Optional, List, Dict, Any
import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class SimpleLLM:
    """Simple LLM client that wraps OpenRouter API."""
    
    def __init__(self, 
                 api_key: Optional[str] = None,
                 model: str = "anthropic/claude-3.5-sonnet",
                 base_url: str = "https://openrouter.ai/api/v1/chat/completions"):
        """
        Initialize LLM client.
        
        Args:
            api_key: OpenRouter API key (or set OPENAI_API_KEY env var)
            model: Model to use
            base_url: API endpoint
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.base_url = base_url
        
        # Track token usage from last API call
        self.last_usage = {}
        
        if not self.api_key:
            logger.warning("No API key provided for LLM")
    
    async def apredict(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Async predict method for compatibility.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            
        Returns:
            LLM response text
        """
        return self.predict(prompt, system_prompt)
    
    def predict(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Synchronous prediction.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            
        Returns:
            LLM response text
        """
        if not self.api_key:
            logger.error("Cannot query LLM without API key")
            return "Error: No API key configured"
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 27000,  # Increased limit for complex quantum simulations (e.g., squeezed light OPO)
                "usage": {"include": True}  # Enable detailed usage and cost tracking
            }
            
            logger.info(f"Querying LLM with model: {self.model}")
            # No timeout - let complex designs take as long as needed
            # The API has its own timeout mechanisms
            response = requests.post(
                self.base_url,
                headers=headers,
                json=data,
                timeout=None  # No client-side timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract and print API usage/cost information from OpenRouter
                usage = result.get('usage', {})
                if usage:
                    prompt_tokens = usage.get('prompt_tokens', 0)
                    completion_tokens = usage.get('completion_tokens', 0)
                    total_tokens = usage.get('total_tokens', 0)
                    
                    # Print token usage
                    print(f"💰 API Usage: {prompt_tokens} prompt + {completion_tokens} completion = {total_tokens} tokens")
                    
                    # Get actual cost from OpenRouter API (in USD)
                    cost = usage.get('cost', 0.0) or 0.0
                    cost_details = usage.get('cost_details', {})
                    upstream_cost = cost_details.get('upstream_inference_cost', 0.0) or 0.0
                    total_cost = cost + upstream_cost
                    
                    if total_cost > 0:
                        print(f"💵 Actual Cost: ${total_cost:.6f} (OpenRouter: ${cost:.6f}, Provider: ${upstream_cost:.6f})")
                    else:
                        print("💵 Cost information not available from API")
                    
                    # Store usage for external tracking
                    self.last_usage = {
                        'prompt_tokens': prompt_tokens,
                        'completion_tokens': completion_tokens,
                        'total_tokens': total_tokens,
                        'cost': total_cost
                    }
                else:
                    self.last_usage = {}
                
                return result['choices'][0]['message']['content']
            else:
                logger.error(f"LLM API error: {response.status_code} - {response.text}")
                # Parse error message for better user feedback
                error_detail = ""
                try:
                    error_json = response.json()
                    error_detail = error_json.get('error', {}).get('message', '')
                except:
                    error_detail = response.text[:200]
                
                if response.status_code == 402:
                    return f"Error: Insufficient credits. Please add credits at https://openrouter.ai/credits"
                elif response.status_code == 429:
                    return f"Error: Rate limit exceeded. Please wait and try again."
                elif response.status_code == 401:
                    return f"Error: Invalid API key. Check your configuration."
                else:
                    return f"Error: API returned {response.status_code} - {error_detail}"
        
        except Exception as e:
            logger.error(f"LLM query failed: {e}")
            return f"Error: {str(e)}"
    
    def __call__(self, prompt: str) -> str:
        """Allow calling instance directly."""
        return self.predict(prompt)
