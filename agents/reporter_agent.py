"""Reporter Agent - generates security reports.

注册为 MCP 工具，支持其他 Agent 调用。
"""

import json
from datetime import datetime
from typing import Any, Dict
from .base_agent import BaseAgent, AgentMessage


class ReporterAgent(BaseAgent):
    """Agent responsible for generating security reports."""
    
    def __init__(self, mcp_registry=None, mcp_context=None):
        super().__init__(name="ReporterAgent", mcp_registry=mcp_registry, mcp_context=mcp_context)
        
        # 注册报告工具
        self._register_report_tools()
    
    def _register_report_tools(self) -> None:
        """注册报告生成相关工具。"""
        self.register_tool(
            name="reporter.generate_report",
            handler=self.generate_report,
            description="Generate structured security report from analysis results",
            tags=["security", "report"],
        )
        self.register_tool(
            name="reporter.format_text",
            handler=self.format_text_report,
            description="Format security report as human-readable text",
            tags=["report", "format"],
        )
        self.register_tool(
            name="reporter.format_json",
            handler=self.format_json_report,
            description="Format security report as JSON",
            tags=["report", "format", "json"],
        )
    
    def process(self, message: AgentMessage) -> AgentMessage:
        """Generate security report from analysis."""
        content = message.content
        
        report = self.generate_report(content)
        
        return self.send(
            receiver="orchestrator",
            content={
                "report": report,
                "report_format": "json",
                "report_complete": True,
            }
        )
    
    def generate_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate structured security report. (MCP Tool)"""
        analysis = data.get("analysis", {})
        findings = data.get("findings", {})
        recommendations = data.get("recommendations", [])
        
        report = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "agent": "Multi-Agent Security System",
                "version": "2.0.0",
            },
            "summary": {
                "total_vulnerabilities": analysis.get("total_vulnerabilities", 0),
                "risk_level": data.get("risk_level", "unknown"),
                "attack_vectors": analysis.get("attack_vectors", []),
            },
            "findings": findings,
            "analysis": {
                "by_severity": analysis.get("by_severity", {}),
                "by_type": analysis.get("by_type", {}),
            },
            "recommendations": recommendations,
            "raw_text": data.get("original_text", "")[:500],
        }
        
        return report
    
    def format_text_report(self, report: Dict[str, Any]) -> str:
        """Format report as human-readable text. (MCP Tool)"""
        lines = [
            "=" * 60,
            "SECURITY ANALYSIS REPORT",
            "=" * 60,
            f"\nTimestamp: {report['metadata']['timestamp']}",
            f"Agent: {report['metadata']['agent']}",
            f"\n--- SUMMARY ---",
            f"Total Vulnerabilities: {report['summary']['total_vulnerabilities']}",
            f"Risk Level: {report['summary']['risk_level'].upper()}",
            f"Attack Vectors: {', '.join(report['summary']['attack_vectors']) or 'None'}",
            f"\n--- FINDINGS ---",
        ]
        
        for vuln_type, matches in report.get("findings", {}).items():
            lines.append(f"\n{vuln_type.upper()}:")
            for match in matches:
                lines.append(f"  - Severity: {match['severity']}")
                lines.append(f"    Pattern: {match['pattern']}")
        
        lines.append(f"\n--- RECOMMENDATIONS ---")
        for i, rec in enumerate(report.get("recommendations", []), 1):
            lines.append(f"{i}. {rec}")
        
        lines.append("\n" + "=" * 60)
        
        return "\n".join(lines)
    
    def format_json_report(self, report: Dict[str, Any]) -> str:
        """Format report as JSON string. (MCP Tool)"""
        return json.dumps(report, indent=2, ensure_ascii=False)
