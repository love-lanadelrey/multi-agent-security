"""Base agent class for all security agents."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List
from datetime import datetime


@dataclass
class AgentMessage:
    """Message passed between agents."""
    sender: str
    receiver: str
    content: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)


class BaseAgent(ABC):
    """Base class for all security agents."""
    
    def __init__(self, name: str):
        self.name = name
        self.memory: List[AgentMessage] = []
        self.is_active = True
    
    @abstractmethod
    def process(self, message: AgentMessage) -> AgentMessage:
        """Process incoming message and return response."""
        pass
    
    def receive(self, message: AgentMessage) -> AgentMessage:
        """Receive message from another agent."""
        self.memory.append(message)
        return self.process(message)
    
    def send(self, receiver: str, content: Dict[str, Any]) -> AgentMessage:
        """Create outgoing message."""
        return AgentMessage(
            sender=self.name,
            receiver=receiver,
            content=content
        )
    
    def get_history(self) -> List[AgentMessage]:
        """Get message history."""
        return self.memory.copy()
