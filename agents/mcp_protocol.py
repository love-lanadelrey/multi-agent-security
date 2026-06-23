"""MCP (Model Context Protocol) - 模型上下文协议实现。

基于 MCP 标准实现多智能体间的松耦合通信，支持：
- 标准化的消息格式
- 工具/技能注册与发现
- 上下文共享与管理
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class MCPMessageType(Enum):
    """MCP 消息类型。"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"


@dataclass
class MCPTool:
    """MCP 工具定义。"""
    name: str
    description: str
    parameters: Dict[str, Any]
    handler: Callable
    tags: List[str] = field(default_factory=list)


@dataclass
class MCPMessage:
    """MCP 标准消息格式。"""
    id: str
    type: MCPMessageType
    sender: str
    receiver: str
    method: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式。"""
        return {
            "id": self.id,
            "type": self.type.value,
            "sender": self.sender,
            "receiver": self.receiver,
            "method": self.method,
            "params": self.params,
            "result": self.result,
            "error": self.error,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context,
        }


class MCPContext:
    """MCP 上下文管理器。"""
    
    def __init__(self):
        self._context: Dict[str, Any] = {}
        self._history: List[MCPMessage] = []
    
    def set(self, key: str, value: Any) -> None:
        """设置上下文变量。"""
        self._context[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取上下文变量。"""
        return self._context.get(key, default)
    
    def delete(self, key: str) -> None:
        """删除上下文变量。"""
        self._context.pop(key, None)
    
    def clear(self) -> None:
        """清空上下文。"""
        self._context.clear()
    
    def add_message(self, message: MCPMessage) -> None:
        """添加消息到历史记录。"""
        self._history.append(message)
    
    def get_history(self) -> List[MCPMessage]:
        """获取消息历史。"""
        return self._history.copy()
    
    def get_context_snapshot(self) -> Dict[str, Any]:
        """获取上下文快照。"""
        return self._context.copy()


class MCPRegistry:
    """MCP 工具注册表。"""
    
    def __init__(self):
        self._tools: Dict[str, MCPTool] = {}
        self._agents: Dict[str, List[str]] = {}
    
    def register_tool(self, tool: MCPTool, agent_name: str) -> None:
        """注册工具。"""
        self._tools[tool.name] = tool
        if agent_name not in self._agents:
            self._agents[agent_name] = []
        self._agents[agent_name].append(tool.name)
    
    def unregister_tool(self, tool_name: str) -> None:
        """注销工具。"""
        if tool_name in self._tools:
            del self._tools[tool_name]
            for agent_name, tools in self._agents.items():
                if tool_name in tools:
                    tools.remove(tool_name)
    
    def get_tool(self, tool_name: str) -> Optional[MCPTool]:
        """获取工具。"""
        return self._tools.get(tool_name)
    
    def list_tools(self) -> List[MCPTool]:
        """列出所有工具。"""
        return list(self._tools.values())
    
    def list_agent_tools(self, agent_name: str) -> List[MCPTool]:
        """列出Agent的工具。"""
        tool_names = self._agents.get(agent_name, [])
        return [self._tools[name] for name in tool_names if name in self._tools]
    
    def call_tool(self, tool_name: str, **kwargs) -> Any:
        """调用工具。"""
        tool = self._tools.get(tool_name)
        if tool is None:
            raise ValueError(f"Tool not found: {tool_name}")
        return tool.handler(**kwargs)


class MCPClient:
    """MCP 客户端 - 用于Agent间通信。"""
    
    def __init__(self, agent_name: str, registry: MCPRegistry, context: MCPContext):
        self.agent_name = agent_name
        self.registry = registry
        self.context = context
        self._message_id = 0
    
    def _generate_id(self) -> str:
        """生成消息ID。"""
        self._message_id += 1
        return f"{self.agent_name}-{self._message_id}"
    
    def call_tool(self, tool_name: str, **kwargs) -> Any:
        """调用远程工具。"""
        tool = self.registry.get_tool(tool_name)
        if tool is None:
            raise ValueError(f"Tool not found: {tool_name}")
        
        message = MCPMessage(
            id=self._generate_id(),
            type=MCPMessageType.TOOL_CALL,
            sender=self.agent_name,
            receiver="registry",
            method="call_tool",
            params={"tool_name": tool_name, "kwargs": kwargs},
        )
        self.context.add_message(message)
        
        try:
            result = self.registry.call_tool(tool_name, **kwargs)
            response = MCPMessage(
                id=self._generate_id(),
                type=MCPMessageType.TOOL_RESULT,
                sender="registry",
                receiver=self.agent_name,
                result=result,
            )
            self.context.add_message(response)
            return result
        except Exception as e:
            error_msg = str(e)
            response = MCPMessage(
                id=self._generate_id(),
                type=MCPMessageType.TOOL_RESULT,
                sender="registry",
                receiver=self.agent_name,
                error=error_msg,
            )
            self.context.add_message(response)
            raise
    
    def send_message(self, receiver: str, method: str, params: Dict[str, Any]) -> MCPMessage:
        """发送消息。"""
        message = MCPMessage(
            id=self._generate_id(),
            type=MCPMessageType.REQUEST,
            sender=self.agent_name,
            receiver=receiver,
            method=method,
            params=params,
        )
        self.context.add_message(message)
        return message
