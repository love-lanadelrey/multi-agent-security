"""Reporter Agent - generates security reports."""

import json
from datetime import datetime
from typing import Any, Dict
from .base_agent import BaseAgent, AgentMessage


class ReporterAgent(BaseAgent):
    """Agent responsible for generating security reports."""
    
    def __init__(self):
        super().__init__(name="ReporterAgent")
    
    def process(self, message: AgentMessage) -> AgentMessage:
        """Generate security report from analysis."""
        content = message.content
        
        report = self._generate_report(content)
        
        return self.send(
            receiver="orchestrator",
            content={
                "report": report,
                "report_format": "json",
                "report_complete": True,
            }
        )
    
    def _generate_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate structured security report."""
        analysis = data.get("analysis", {})
        findings = data.get("findings", {})
        recommendations = data.get("recommendations", [])
        
        report = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "agent": "Multi-Agent Security System",
                "version": "1.0.0",
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
        """Format report as human-readable text."""
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
