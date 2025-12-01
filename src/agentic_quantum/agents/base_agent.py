"""
Base agent classes and communication protocols for the agentic quantum system.
"""

import uuid
import time
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod
import asyncio
import logging

try:
    from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
    from langchain.llms.base import BaseLLM
    from langchain.chat_models.base import BaseChatModel
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    BaseMessage = HumanMessage = AIMessage = SystemMessage = None
    BaseLLM = BaseChatModel = None

logger = logging.getLogger(__name__)


class AgentRole(Enum):
    """Enumeration of agent roles in the system."""
    COORDINATOR = "coordinator"
    DESIGNER = "designer"
    ANALYZER = "analyzer"
    OPTIMIZER = "optimizer"
    KNOWLEDGE = "knowledge"


class MessageType(Enum):
    """Types of messages between agents."""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    QUERY = "query"
    RESULT = "result"
    ERROR = "error"


@dataclass
class AgentMessage:
    """Message passed between agents."""
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str = ""
    receiver_id: str = ""
    message_type: MessageType = MessageType.REQUEST
    content: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    conversation_id: str = ""
    priority: int = 0  # Higher number = higher priority
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "message_id": self.message_id,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "message_type": self.message_type.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "conversation_id": self.conversation_id,
            "priority": self.priority
        }


@dataclass
class AgentCapability:
    """Describes an agent's capability."""
    name: str
    description: str
    input_types: List[str]
    output_types: List[str]
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentState:
    """Current state of an agent."""
    status: str = "idle"  # idle, busy, error, offline
    current_task: Optional[str] = None
    last_activity: datetime = field(default_factory=datetime.now)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    resource_usage: Dict[str, float] = field(default_factory=dict)


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the agentic quantum system.
    
    Agents are autonomous entities that can:
    - Communicate with other agents via messages
    - Process requests and generate responses
    - Maintain internal state and memory
    - Learn and adapt over time
    - Interface with LLMs for intelligent reasoning
    """
    
    def __init__(self,
                 agent_id: str,
                 role: AgentRole,
                 name: str,
                 description: str,
                 llm: Optional[Union[BaseLLM, BaseChatModel]] = None,
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize a base agent.
        
        Args:
            agent_id: Unique identifier for the agent
            role: Role of the agent in the system
            name: Human-readable name
            description: Description of agent's purpose
            llm: Language model for intelligent reasoning
            config: Agent-specific configuration
        """
        self.agent_id = agent_id
        self.role = role
        self.name = name
        self.description = description
        self.llm = llm
        self.config = config or {}
        
        # Agent state
        self.state = AgentState()
        self.capabilities: List[AgentCapability] = []
        self.memory: Dict[str, Any] = {}
        self.message_history: List[AgentMessage] = []
        
        # Communication
        self.inbox: List[AgentMessage] = []
        self.outbox: List[AgentMessage] = []
        self.subscriptions: List[str] = []  # Topic subscriptions
        
        # Performance tracking
        self.start_time = datetime.now()
        self.total_messages_processed = 0
        self.total_errors = 0
        
        # Callback hooks
        self.on_message_received: Optional[Callable] = None
        self.on_message_sent: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        
        logger.info(f"Initialized agent: {self.name} ({self.agent_id})")
    
    @abstractmethod
    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """
        Process an incoming message and optionally return a response.
        
        Args:
            message: Incoming message to process
        
        Returns:
            Optional response message
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[AgentCapability]:
        """Return list of agent capabilities."""
        pass
    
    async def send_message(self, 
                          receiver_id: str,
                          message_type: MessageType,
                          content: Dict[str, Any],
                          conversation_id: str = "",
                          priority: int = 0) -> AgentMessage:
        """
        Send a message to another agent.
        
        Args:
            receiver_id: ID of receiving agent
            message_type: Type of message
            content: Message content
            conversation_id: Conversation identifier
            priority: Message priority
        
        Returns:
            The sent message
        """
        message = AgentMessage(
            sender_id=self.agent_id,
            receiver_id=receiver_id,
            message_type=message_type,
            content=content,
            conversation_id=conversation_id,
            priority=priority
        )
        
        self.outbox.append(message)
        self.message_history.append(message)
        
        if self.on_message_sent:
            self.on_message_sent(message)
        
        logger.debug(f"{self.name} sent message to {receiver_id}: {message_type.value}")
        return message
    
    async def receive_message(self, message: AgentMessage):
        """
        Receive and queue a message for processing.
        
        Args:
            message: Incoming message
        """
        self.inbox.append(message)
        self.message_history.append(message)
        
        if self.on_message_received:
            self.on_message_received(message)
        
        logger.debug(f"{self.name} received message from {message.sender_id}: {message.message_type.value}")
    
    async def process_inbox(self) -> List[AgentMessage]:
        """
        Process all messages in the inbox.
        
        Returns:
            List of response messages
        """
        responses = []
        
        # Sort by priority (higher first) and timestamp
        self.inbox.sort(key=lambda m: (-m.priority, m.timestamp))
        
        while self.inbox:
            message = self.inbox.pop(0)
            
            try:
                self.state.status = "busy"
                self.state.current_task = f"Processing {message.message_type.value}"
                self.state.last_activity = datetime.now()
                
                response = await self.process_message(message)
                if response:
                    responses.append(response)
                
                self.total_messages_processed += 1
                
            except Exception as e:
                self.total_errors += 1
                self.state.status = "error"
                
                error_message = await self.send_message(
                    receiver_id=message.sender_id,
                    message_type=MessageType.ERROR,
                    content={
                        "error": str(e),
                        "original_message_id": message.message_id
                    },
                    conversation_id=message.conversation_id
                )
                responses.append(error_message)
                
                if self.on_error:
                    self.on_error(e, message)
                
                logger.error(f"{self.name} error processing message: {e}")
            
            finally:
                self.state.status = "idle"
                self.state.current_task = None
        
        return responses
    
    async def query_llm(self, 
                       prompt: str, 
                       system_prompt: Optional[str] = None,
                       context: Optional[Dict[str, Any]] = None) -> str:
        """
        Query the agent's language model.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt for context
            context: Additional context information
        
        Returns:
            LLM response
        """
        if not self.llm:
            raise ValueError(f"No LLM configured for agent {self.name}")
        
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("LangChain is required for LLM integration")
        
        try:
            # Prepare messages
            messages = []
            
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            
            # Add context if provided
            if context:
                context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
                prompt = f"Context:\n{context_str}\n\nQuery:\n{prompt}"
            
            messages.append(HumanMessage(content=prompt))
            
            # Query LLM
            if hasattr(self.llm, 'predict_messages'):
                # Chat model
                response = await self.llm.apredict_messages(messages)
                return response.content
            else:
                # Regular LLM
                full_prompt = "\n\n".join([msg.content for msg in messages])
                response = await self.llm.apredict(full_prompt)
                return response
        
        except Exception as e:
            logger.error(f"{self.name} LLM query failed: {e}")
            raise
    
    def add_to_memory(self, key: str, value: Any, expire_after: Optional[float] = None):
        """
        Add information to agent memory.
        
        Args:
            key: Memory key
            value: Value to store
            expire_after: Expiration time in seconds (None for no expiration)
        """
        entry = {
            "value": value,
            "timestamp": datetime.now(),
            "expire_after": expire_after
        }
        self.memory[key] = entry
    
    def get_from_memory(self, key: str) -> Any:
        """
        Retrieve information from agent memory.
        
        Args:
            key: Memory key
        
        Returns:
            Stored value or None if not found/expired
        """
        if key not in self.memory:
            return None
        
        entry = self.memory[key]
        
        # Check expiration
        if entry["expire_after"]:
            elapsed = (datetime.now() - entry["timestamp"]).total_seconds()
            if elapsed > entry["expire_after"]:
                del self.memory[key]
                return None
        
        return entry["value"]
    
    def clear_expired_memory(self):
        """Remove expired entries from memory."""
        expired_keys = []
        now = datetime.now()
        
        for key, entry in self.memory.items():
            if entry["expire_after"]:
                elapsed = (now - entry["timestamp"]).total_seconds()
                if elapsed > entry["expire_after"]:
                    expired_keys.append(key)
        
        for key in expired_keys:
            del self.memory[key]
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """Get agent performance metrics."""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        metrics = {
            "uptime_seconds": uptime,
            "messages_processed": self.total_messages_processed,
            "errors": self.total_errors,
            "error_rate": self.total_errors / max(self.total_messages_processed, 1),
            "messages_per_second": self.total_messages_processed / max(uptime, 1),
            "inbox_size": len(self.inbox),
            "memory_entries": len(self.memory)
        }
        
        metrics.update(self.state.performance_metrics)
        return metrics
    
    def reset_metrics(self):
        """Reset performance metrics."""
        self.start_time = datetime.now()
        self.total_messages_processed = 0
        self.total_errors = 0
        self.state.performance_metrics.clear()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary representation."""
        return {
            "agent_id": self.agent_id,
            "role": self.role.value,
            "name": self.name,
            "description": self.description,
            "state": {
                "status": self.state.status,
                "current_task": self.state.current_task,
                "last_activity": self.state.last_activity.isoformat()
            },
            "capabilities": [cap.__dict__ for cap in self.capabilities],
            "performance_metrics": self.get_performance_metrics(),
            "memory_size": len(self.memory),
            "inbox_size": len(self.inbox)
        }
    
    def __str__(self) -> str:
        """String representation of the agent."""
        return f"{self.name} ({self.role.value}): {self.state.status}"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return (f"BaseAgent(id='{self.agent_id}', "
                f"role={self.role}, "
                f"name='{self.name}', "
                f"status='{self.state.status}')")


class AgentRegistry:
    """Registry for managing agents in the system."""
    
    def __init__(self):
        """Initialize the agent registry."""
        self.agents: Dict[str, BaseAgent] = {}
        self.role_mapping: Dict[AgentRole, List[str]] = {role: [] for role in AgentRole}
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent."""
        self.agents[agent.agent_id] = agent
        self.role_mapping[agent.role].append(agent.agent_id)
        logger.info(f"Registered agent: {agent.name}")
    
    def unregister_agent(self, agent_id: str):
        """Unregister an agent."""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            self.role_mapping[agent.role].remove(agent_id)
            del self.agents[agent_id]
            logger.info(f"Unregistered agent: {agent.name}")
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get agent by ID."""
        return self.agents.get(agent_id)
    
    def get_agents_by_role(self, role: AgentRole) -> List[BaseAgent]:
        """Get all agents with a specific role."""
        agent_ids = self.role_mapping.get(role, [])
        return [self.agents[aid] for aid in agent_ids if aid in self.agents]
    
    def get_all_agents(self) -> List[BaseAgent]:
        """Get all registered agents."""
        return list(self.agents.values())
    
    async def route_message(self, message: AgentMessage) -> bool:
        """
        Route a message to the appropriate agent.
        
        Args:
            message: Message to route
        
        Returns:
            True if successfully routed
        """
        target_agent = self.get_agent(message.receiver_id)
        if target_agent:
            await target_agent.receive_message(message)
            return True
        
        logger.warning(f"Failed to route message: agent {message.receiver_id} not found")
        return False
    
    async def broadcast_message(self, 
                              sender_id: str,
                              message_type: MessageType,
                              content: Dict[str, Any],
                              target_roles: Optional[List[AgentRole]] = None):
        """
        Broadcast a message to multiple agents.
        
        Args:
            sender_id: ID of sending agent
            message_type: Type of message
            content: Message content
            target_roles: Target roles (None for all agents)
        """
        if target_roles is None:
            target_agents = self.get_all_agents()
        else:
            target_agents = []
            for role in target_roles:
                target_agents.extend(self.get_agents_by_role(role))
        
        for agent in target_agents:
            if agent.agent_id != sender_id:  # Don't send to self
                message = AgentMessage(
                    sender_id=sender_id,
                    receiver_id=agent.agent_id,
                    message_type=message_type,
                    content=content
                )
                await agent.receive_message(message)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        total_agents = len(self.agents)
        active_agents = len([a for a in self.agents.values() if a.state.status != "offline"])
        
        role_counts = {}
        for role, agent_ids in self.role_mapping.items():
            role_counts[role.value] = len(agent_ids)
        
        return {
            "total_agents": total_agents,
            "active_agents": active_agents,
            "role_distribution": role_counts,
            "system_uptime": datetime.now().isoformat()
        }
