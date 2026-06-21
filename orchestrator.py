"""Orchestrator - coordinates multiple agents for security analysis."""

from typing import Any, Dict, List
from agents.scanner_agent import ScannerAgent
from agents.analyzer_agent import AnalyzerAgent
from agents.reporter_agent import ReporterAgent
from agents.base_agent import AgentMessage


class SecurityOrchestrator:
    """Orchestrates multiple agents for comprehensive security analysis."""
    
    def __init__(self):
        self.scanner = ScannerAgent()
        self.analyzer = AnalyzerAgent()
        self.reporter = ReporterAgent()
        
        self.agents = {
            "ScannerAgent": self.scanner,
            "AnalyzerAgent": self.analyzer,
            "ReporterAgent": self.reporter,
        }
        
        self.pipeline = ["ScannerAgent", "AnalyzerAgent", "ReporterAgent"]
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """Run full security analysis pipeline."""
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
    
    def analyze_code(self, code: str) -> Dict[str, Any]:
        """Analyze code for security issues."""
        scan_result = self.scanner.scan_code(code)
        
        return {
            "code": code,
            "issues": scan_result["issues"],
            "issue_count": scan_result["issue_count"],
            "risk_level": "high" if scan_result["issue_count"] > 0 else "low",
        }
    
    def get_agent_stats(self) -> Dict[str, Any]:
        """Get statistics for all agents."""
        stats = {}
        for name, agent in self.agents.items():
            stats[name] = {
                "messages_processed": len(agent.get_history()),
                "is_active": agent.is_active,
            }
        return stats
