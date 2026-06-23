"""Agent Skills/Tools 注册机制。

实现标准化的工具注册、发现和调用机制，支持：
- 工具元数据定义
- 自动工具发现
- 参数验证
- 工具调用追踪
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
import inspect


@dataclass
class ToolParameter:
    """工具参数定义。"""
    name: str
    type: str
    description: str
    required: bool = True
    default: Any = None


@dataclass
class ToolMetadata:
    """工具元数据。"""
    name: str
    description: str
    agent_name: str
    parameters: List[ToolParameter]
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    call_count: int = 0
    last_called: Optional[datetime] = None


@dataclass
class ToolCallRecord:
    """工具调用记录。"""
    tool_name: str
    agent_name: str
    params: Dict[str, Any]
    result: Any
    success: bool
    timestamp: datetime = field(default_factory=datetime.now)
    duration_ms: float = 0.0


class AgentToolRegistry:
    """Agent 工具注册表。"""
    
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._metadata: Dict[str, ToolMetadata] = {}
        self._call_history: List[ToolCallRecord] = []
    
    def register(
        self,
        name: str,
        handler: Callable,
        description: str,
        parameters: Optional[List[ToolParameter]] = None,
        agent_name: str = "unknown",
        tags: Optional[List[str]] = None,
    ) -> None:
        """注册工具。"""
        if parameters is None:
            parameters = self._extract_parameters(handler)
        
        self._tools[name] = handler
        self._metadata[name] = ToolMetadata(
            name=name,
            description=description,
            agent_name=agent_name,
            parameters=parameters,
            tags=tags or [],
        )
    
    def unregister(self, name: str) -> None:
        """注销工具。"""
        self._tools.pop(name, None)
        self._metadata.pop(name, None)
    
    def get_handler(self, name: str) -> Optional[Callable]:
        """获取工具处理器。"""
        return self._tools.get(name)
    
    def get_metadata(self, name: str) -> Optional[ToolMetadata]:
        """获取工具元数据。"""
        return self._metadata.get(name)
    
    def list_tools(self) -> List[ToolMetadata]:
        """列出所有工具。"""
        return list(self._metadata.values())
    
    def list_agent_tools(self, agent_name: str) -> List[ToolMetadata]:
        """列出指定Agent的工具。"""
        return [
            meta for meta in self._metadata.values()
            if meta.agent_name == agent_name
        ]
    
    def list_by_tag(self, tag: str) -> List[ToolMetadata]:
        """按标签筛选工具。"""
        return [
            meta for meta in self._metadata.values()
            if tag in meta.tags
        ]
    
    def call(self, name: str, **kwargs) -> Any:
        """调用工具。"""
        handler = self._tools.get(name)
        if handler is None:
            raise ValueError(f"Tool not found: {name}")
        
        metadata = self._metadata.get(name)
        start_time = datetime.now()
        
        try:
            result = handler(**kwargs)
            duration = (datetime.now() - start_time).total_seconds() * 1000
            
            if metadata:
                metadata.call_count += 1
                metadata.last_called = datetime.now()
            
            record = ToolCallRecord(
                tool_name=name,
                agent_name=metadata.agent_name if metadata else "unknown",
                params=kwargs,
                result=result,
                success=True,
                duration_ms=duration,
            )
            self._call_history.append(record)
            
            return result
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            record = ToolCallRecord(
                tool_name=name,
                agent_name=metadata.agent_name if metadata else "unknown",
                params=kwargs,
                result=None,
                success=False,
                duration_ms=duration,
            )
            self._call_history.append(record)
            raise
    
    def get_call_history(self) -> List[ToolCallRecord]:
        """获取调用历史。"""
        return self._call_history.copy()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息。"""
        stats = {
            "total_tools": len(self._tools),
            "total_calls": len(self._call_history),
            "successful_calls": sum(1 for r in self._call_history if r.success),
            "failed_calls": sum(1 for r in self._call_history if not r.success),
            "tools_by_agent": {},
        }
        
        for meta in self._metadata.values():
            agent = meta.agent_name
            if agent not in stats["tools_by_agent"]:
                stats["tools_by_agent"][agent] = 0
            stats["tools_by_agent"][agent] += 1
        
        return stats
    
    def _extract_parameters(self, handler: Callable) -> List[ToolParameter]:
        """从函数签名提取参数。"""
        parameters = []
        sig = inspect.signature(handler)
        
        for name, param in sig.parameters.items():
            param_type = "any"
            if param.annotation != inspect.Parameter.empty:
                param_type = str(param.annotation)
            
            required = param.default == inspect.Parameter.empty
            default = None if required else param.default
            
            parameters.append(ToolParameter(
                name=name,
                type=param_type,
                description=f"Parameter: {name}",
                required=required,
                default=default,
            ))
        
        return parameters


def tool(
    name: str,
    description: str,
    parameters: Optional[List[ToolParameter]] = None,
    tags: Optional[List[str]] = None,
):
    """工具装饰器。"""
    def decorator(func: Callable) -> Callable:
        func._tool_metadata = {
            "name": name,
            "description": description,
            "parameters": parameters,
            "tags": tags or [],
        }
        return func
    return decorator
