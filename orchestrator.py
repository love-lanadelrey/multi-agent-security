"""Orchestrator - coordinates multiple agents for security analysis.

支持 MCP 协议，实现松耦合的多智能体编排。
"""

from typing import Any, Dict, List
from agents.scanner_agent import ScannerAgent
from agents.analyzer_agent import AnalyzerAgent
from agents.reporter_agent import ReporterAgent
from agents.base_agent import AgentMessage
from agents.mcp_protocol import MCPRegistry, MCPContext, MCPMessage, MCPMessageType


class SecurityOrchestrator:
    """Orchestrates multiple agents for comprehensive security analysis.
    
    支持 MCP 协议进行松耦合通信。
    """
    
    def __init__(self):
        # MCP 组件
        self._mcp_registry = MCPRegistry()
        self._mcp_context = MCPContext()
        
        # 初始化 Agent
        self.scanner = ScannerAgent(
            mcp_registry=self._mcp_registry,
            mcp_context=self._mcp_context,
        )
        self.analyzer = AnalyzerAgent(
            mcp_registry=self._mcp_registry,
            mcp_context=self._mcp_context,
        )
        self.reporter = ReporterAgent(
            mcp_registry=self._mcp_registry,
            mcp_context=self._mcp_context,
        )
        
        self.agents = {
            "ScannerAgent": self.scanner,
            "AnalyzerAgent": self.analyzer,
            "ReporterAgent": self.reporter,
        }
        
        self.pipeline = ["ScannerAgent", "AnalyzerAgent", "ReporterAgent"]
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """Run full security analysis pipeline (向后兼容)。"""
        initial_message = AgentMessage(
            sender="orchestrator",
            receiver="ScannerAgent",
            content={"text": text}
        )
        
        current_message = initial_message
        
        for agent_name in self.pipeline:
            agent = self.agents[agent_name]
            current_message = agent.receive(current_message)
        
        return current_message.content.get("report", {})
    
    def analyze_mcp(self, text: str) -> Dict[str, Any]:
        """Run full security analysis pipeline using MCP protocol。"""
        initial_message = MCPMessage(
            id="orchestrator-init",
            type=MCPMessageType.REQUEST,
            sender="orchestrator",
            receiver="ScannerAgent",
            method="scan_text",
            params={"text": text},
            context={"pipeline_stage": "scan"},
        )
        
        current_message = initial_message
        
        for agent_name in self.pipeline:
            agent = self.agents[agent_name]
            current_message = agent.receive_mcp(current_message)
        
        # 提取报告内容
        result = current_message.result or {}
        if "report" in result:
            return result["report"]
        return result
    
    def call_tool(self, tool_name: str, **kwargs) -> Any:
        """调用已注册的 MCP 工具。"""
        return self._mcp_registry.call_tool(tool_name, **kwargs)
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """列出所有已注册的 MCP 工具。"""
        tools = self._mcp_registry.list_tools()
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "tags": tool.tags,
            }
            for tool in tools
        ]
    
    def get_agent_tools(self, agent_name: str) -> List[Dict[str, Any]]:
        """获取指定 Agent 的工具列表。"""
        tools = self._mcp_registry.list_agent_tools(agent_name)
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "tags": tool.tags,
            }
            for tool in tools
        ]
    
    def analyze_code(self, code: str) -> Dict[str, Any]:
        """Analyze code for security issues (向后兼容)。"""
        scan_result = self.scanner.scan_code(code)
        
        return {
            "code": code,
            "issues": scan_result["issues"],
            "issue_count": scan_result["issue_count"],
            "risk_level": "high" if scan_result["issue_count"] > 0 else "low",
        }
    
    def get_agent_stats(self) -> Dict[str, Any]:
        """Get statistics for all agents (向后兼容)。"""
        stats = {}
        for name, agent in self.agents.items():
            stats[name] = {
                "messages_processed": len(agent.get_history()),
                "is_active": agent.is_active,
                "tool_stats": agent.get_tool_stats(),
            }
        return stats
    
    def get_mcp_stats(self) -> Dict[str, Any]:
        """获取 MCP 协议统计信息。"""
        return {
            "total_tools": len(self._mcp_registry.list_tools()),
            "total_messages": len(self._mcp_context.get_history()),
            "agents": list(self.agents.keys()),
        }
