"""Scanner Agent - scans content for security vulnerabilities."""

import re
from typing import Any, Dict, List
from .base_agent import BaseAgent, AgentMessage


class ScannerAgent(BaseAgent):
    """Agent responsible for scanning content for security issues."""
    
    def __init__(self):
        super().__init__(name="ScannerAgent")
        
        self.vulnerability_patterns = {
            "prompt_injection": [
                r"ignore\s+(all\s+)?previous\s+instructions",
                r"you\s+are\s+now\s+(DAN|a\s+hacker)",
                r"system\s*:\s*you\s+are",
                r"disregard\s+(all\s+)?prior",
                r"forget\s+(all\s+)?instructions",
            ],
            "data_leakage": [
                r"(api[_-]?key|secret|password|token)\s*[:=]\s*\S+",
                r"sk-[a-zA-Z0-9]{10,}",
                r"AKIA[A-Z0-9]{16}",
                r"\b\d{3}[-.\s]?\d{2}[-.\s]?\d{4}\b",
            ],
            "toxicity": [
                r"\b(kill|murder|assault|weapon|bomb)\b",
                r"\b(hack|crack|bypass|exploit)\b",
                r"\b(illegal|malware|phishing)\b",
            ],
            "encoding_bypass": [
                r"base64\s*[:=]",
                r"rot13",
                r"hex\s*[:=]",
                r"\\x[0-9a-f]{2}",
            ],
        }
    
    def process(self, message: AgentMessage) -> AgentMessage:
        """Scan content for vulnerabilities."""
        content = message.content
        text = content.get("text", "")
        
        findings = self._scan_text(text)
        
        return self.send(
            receiver="AnalyzerAgent",
            content={
                "original_text": text,
                "findings": findings,
                "vulnerability_count": sum(len(v) for v in findings.values()),
                "scan_complete": True,
            }
        )
    
    def _scan_text(self, text: str) -> Dict[str, List[Dict]]:
        """Scan text for vulnerability patterns."""
        findings = {}
        
        for vuln_type, patterns in self.vulnerability_patterns.items():
            matches = []
            for pattern in patterns:
                found = re.findall(pattern, text, re.IGNORECASE)
                if found:
                    matches.extend(found)
            
            if matches:
                findings[vuln_type] = [
                    {"pattern": m, "severity": self._get_severity(vuln_type)}
                    for m in matches[:3]
                ]
        
        return findings
    
    def _get_severity(self, vuln_type: str) -> str:
        """Get severity level for vulnerability type."""
        severity_map = {
            "prompt_injection": "critical",
            "data_leakage": "critical",
            "toxicity": "high",
            "encoding_bypass": "medium",
        }
        return severity_map.get(vuln_type, "low")
    
    def scan_code(self, code: str) -> Dict[str, Any]:
        """Scan code for security issues."""
        issues = []
        
        dangerous_functions = [
            r"eval\s*\(",
            r"exec\s*\(",
            r"os\.system\s*\(",
            r"subprocess\.call\s*\(.*shell\s*=\s*True",
            r"__import__\s*\(",
        ]
        
        for pattern in dangerous_functions:
            if re.search(pattern, code):
                issues.append({
                    "type": "dangerous_function",
                    "pattern": pattern,
                    "severity": "high"
                })
        
        return {
            "code": code,
            "issues": issues,
            "issue_count": len(issues)
        }
