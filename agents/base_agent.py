"""Base agent class for all security agents.

支持 MCP (Model Context Protocol) 协议，实现松耦合通信。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List
from datetime import datetime

from .mcp_protocol import MCPMessage, MCPMessageType, MCPRegistry, MCPClient, MCPContext
from .tool_registry import AgentToolRegistry, ToolMetadata


@dataclass
class AgentMessage:
    """Message passed between agents (向后兼容)。"""
    sender: str
    receiver: str
    content: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)


class BaseAgent(ABC):
    """Base class for all security agents.
    
    支持 MCP 协议进行松耦合通信，同时保持向后兼容。
    """
    
    def __init__(self, name: str, mcp_registry: MCPRegistry = None, mcp_context: MCPContext = None):
        self.name = name
        self.memory: List[AgentMessage] = []
        self.is_active = True
        
        # MCP 支持
        self._mcp_registry = mcp_registry or MCPRegistry()
        self._mcp_context = mcp_context or MCPContext()
        self._mcp_client = MCPClient(name, self._mcp_registry, self._mcp_context)
        
        # 工具注册表
        self._tool_registry = AgentToolRegistry()
        
        # 注册默认工具
        self._register_default_tools()
    
    def _register_default_tools(self) -> None:
        """注册默认工具。"""
        self.register_tool(
            name=f"{self.name}.process",
            handler=self.process,
            description=f"Process message for {self.name}",
            tags=["core"],
        )
        self.register_tool(
            name=f"{self.name}.get_history",
            handler=self.get_history,
            description=f"Get message history for {self.name}",
            tags=["utility"],
        )
    
    def register_tool(
        self,
        name: str,
        handler,
        description: str,
        parameters=None,
        tags: List[str] = None,
    ) -> None:
        """注册工具到工具注册表和 MCP Registry。"""
        # 注册到本地工具注册表
        self._tool_registry.register(
            name=name,
            handler=handler,
            description=description,
            parameters=parameters,
            agent_name=self.name,
            tags=tags,
        )
        
        # 注册到 MCP Registry
        from .mcp_protocol import MCPTool
        mcp_tool = MCPTool(
            name=name,
            description=description,
            parameters={},
            handler=handler,
            tags=tags or [],
        )
        self._mcp_registry.register_tool(mcp_tool, self.name)
    
    def call_tool(self, tool_name: str, **kwargs) -> Any:
        """调用已注册的工具。"""
        return self._tool_registry.call(tool_name, **kwargs)
    
    def list_tools(self) -> List[ToolMetadata]:
        """列出所有已注册的工具。"""
        return self._tool_registry.list_tools()
    
    def get_tool_stats(self) -> Dict[str, Any]:
        """获取工具调用统计。"""
        return self._tool_registry.get_stats()
    
    @abstractmethod
    def process(self, message: AgentMessage) -> AgentMessage:
        """Process incoming message and return response."""
        pass
    
    def receive(self, message: AgentMessage) -> AgentMessage:
        """Receive message from another agent (向后兼容)。"""
        self.memory.append(message)
        return self.process(message)
    
    def receive_mcp(self, message: MCPMessage) -> MCPMessage:
        """Receive MCP message from another agent。"""
        self._mcp_context.add_message(message)
        
        agent_message = AgentMessage(
            sender=message.sender,
            receiver=message.receiver,
            content=message.params or {},
        )
        self.memory.append(agent_message)
        
        result = self.process(agent_message)
        
        return MCPMessage(
            id=f"{self.name}-response-{message.id}",
            type=MCPMessageType.RESPONSE,
            sender=self.name,
            receiver=message.sender,
            result=result.content,
            context={"original_message_id": message.id},
        )
    
    def send(self, receiver: str, content: Dict[str, Any]) -> AgentMessage:
        """Create outgoing message (向后兼容)。"""
        return AgentMessage(
            sender=self.name,
            receiver=receiver,
            content=content
        )
    
    def send_mcp(self, receiver: str, method: str, params: Dict[str, Any]) -> MCPMessage:
        """Create MCP message。"""
        return self._mcp_client.send_message(receiver, method, params)
    
    def get_history(self) -> List[AgentMessage]:
        """Get message history。"""
        return self.memory.copy()
    
    def get_mcp_history(self) -> List[MCPMessage]:
        """Get MCP message history。"""
        return self._mcp_context.get_history()
