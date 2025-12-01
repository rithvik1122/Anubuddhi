"""
Configuration management for the AgenticQuantum system.
"""

import os
from typing import Optional, Dict, Any
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config(BaseSettings):
    """Configuration settings for the AgenticQuantum system."""
    
    # LLM Configuration
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    ollama_base_url: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    llm_provider: str = Field(default="openai", env="LLM_PROVIDER")
    
    # Database Configuration
    database_url: str = Field(default="sqlite:///./quantum_knowledge.db", env="DATABASE_URL")
    vector_db_path: str = Field(default="./quantum_knowledge_db", env="VECTOR_DB_PATH")
    
    # Vector Database Configuration
    chroma_persist_directory: str = Field(default="./data/chroma_db", env="CHROMA_PERSIST_DIRECTORY")
    embedding_model: str = Field(default="all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    
    # System Configuration
    debug: bool = Field(default=False, env="DEBUG")
    max_workers: int = Field(default=4, env="MAX_WORKERS")
    task_timeout: int = Field(default=300, env="TASK_TIMEOUT")
    
    # Quantum Simulation Configuration
    max_hilbert_space_dim: int = Field(default=200, env="MAX_HILBERT_SPACE_DIM")
    default_truncation: int = Field(default=50, env="DEFAULT_TRUNCATION")
    quantum_backend: str = Field(default="qutip", env="QUANTUM_BACKEND")
    
    # Agent Configuration
    max_agent_iterations: int = Field(default=10, env="MAX_AGENT_ITERATIONS")
    agent_timeout: int = Field(default=300, env="AGENT_TIMEOUT")
    enable_parallel_agents: bool = Field(default=True, env="ENABLE_PARALLEL_AGENTS")
    
    # Optimization Configuration
    max_optimization_iterations: int = Field(default=100, env="MAX_OPTIMIZATION_ITERATIONS")
    population_size: int = Field(default=50, env="POPULATION_SIZE")
    genetic_algorithm_population: int = Field(default=50, env="GENETIC_ALGORITHM_POPULATION")
    genetic_algorithm_generations: int = Field(default=100, env="GENETIC_ALGORITHM_GENERATIONS")
    bayesian_optimization_iterations: int = Field(default=50, env="BAYESIAN_OPTIMIZATION_ITERATIONS")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="./logs/agentic_quantum.log", env="LOG_FILE")
    
    # Performance Configuration
    enable_caching: bool = Field(default=True, env="ENABLE_CACHING")
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")
    max_concurrent_simulations: int = Field(default=4, env="MAX_CONCURRENT_SIMULATIONS")
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8"
    }
    
    def validate_configuration(self) -> bool:
        """Validate that required configuration is present."""
        errors = []
        
        # Check that at least one LLM API key is provided
        if not any([self.openai_api_key, self.anthropic_api_key]):
            errors.append("At least one LLM API key must be provided (OpenAI or Anthropic)")
        
        # Check quantum backend
        if self.quantum_backend not in ["qutip", "qiskit"]:
            errors.append("Quantum backend must be 'qutip' or 'qiskit'")
        
        # Check reasonable values
        if self.max_hilbert_space_dim <= 0:
            errors.append("Maximum Hilbert space dimension must be positive")
        
        if self.default_truncation <= 0:
            errors.append("Default truncation must be positive")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return self.dict()
    
    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables."""
        return cls()


# Global configuration instance
config = Config.from_env()
