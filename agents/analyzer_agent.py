"""Analyzer Agent - analyzes threats and assesses risk."""

from typing import Any, Dict, List
from .base_agent import BaseAgent, AgentMessage


class AnalyzerAgent(BaseAgent):
    """Agent responsible for analyzing threats and assessing risk."""
    
    def __init__(self):
        super().__init__(name="AnalyzerAgent")
        
        self.risk_scores = {
            "critical": 4,
            "high": 3,
            "medium": 2,
            "low": 1,
        }
    
    def process(self, message: AgentMessage) -> AgentMessage:
        """Analyze findings from Scanner Agent."""
        content = message.content
        findings = content.get("findings", {})
        original_text = content.get("original_text", "")
        
        analysis = self._analyze_findings(findings)
        risk_level = self._calculate_risk_level(analysis)
        recommendations = self._generate_recommendations(analysis)
        
        return self.send(
            receiver="ReporterAgent",
            content={
                "original_text": original_text,
                "findings": findings,
                "analysis": analysis,
                "risk_level": risk_level,
                "recommendations": recommendations,
                "analysis_complete": True,
            }
        )
    
    def _analyze_findings(self, findings: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Analyze vulnerability findings."""
        analysis = {
            "total_vulnerabilities": 0,
            "by_severity": {"critical": 0, "high": 0, "medium": 0, "low": 0},
            "by_type": {},
            "attack_vectors": [],
        }
        
        for vuln_type, matches in findings.items():
            analysis["by_type"][vuln_type] = len(matches)
            analysis["total_vulnerabilities"] += len(matches)
            
            for match in matches:
                severity = match.get("severity", "low")
                analysis["by_severity"][severity] += 1
            
            if vuln_type == "prompt_injection":
                analysis["attack_vectors"].append("prompt_injection")
            elif vuln_type == "data_leakage":
                analysis["attack_vectors"].append("data_exfiltration")
            elif vuln_type == "toxicity":
                analysis["attack_vectors"].append("harmful_content")
        
        return analysis
    
    def _calculate_risk_level(self, analysis: Dict[str, Any]) -> str:
        """Calculate overall risk level."""
        by_severity = analysis["by_severity"]
        
        if by_severity["critical"] > 0:
            return "critical"
        elif by_severity["high"] > 0:
            return "high"
        elif by_severity["medium"] > 0:
            return "medium"
        else:
            return "low"
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate security recommendations."""
        recommendations = []
        
        if analysis["by_type"].get("prompt_injection", 0) > 0:
            recommendations.append("Implement input sanitization for prompt injection")
            recommendations.append("Add output filtering to prevent instruction leakage")
        
        if analysis["by_type"].get("data_leakage", 0) > 0:
            recommendations.append("Remove sensitive data from responses")
            recommendations.append("Implement PII detection and masking")
        
        if analysis["by_type"].get("toxicity", 0) > 0:
            recommendations.append("Add toxicity detection filter")
            recommendations.append("Implement content moderation")
        
        if analysis["by_type"].get("encoding_bypass", 0) > 0:
            recommendations.append("Detect and block encoding bypass attempts")
            recommendations.append("Normalize input before processing")
        
        if not recommendations:
            recommendations.append("No immediate actions required")
        
        return recommendations
