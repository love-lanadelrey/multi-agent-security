"""Scanner Agent - scans content for security vulnerabilities.

注册为 MCP 工具，支持其他 Agent 调用。
"""

import re
from typing import Any, Dict, List
from .base_agent import BaseAgent, AgentMessage


class ScannerAgent(BaseAgent):
    """Agent responsible for scanning content for security issues."""
    
    def __init__(self, mcp_registry=None, mcp_context=None):
        super().__init__(name="ScannerAgent", mcp_registry=mcp_registry, mcp_context=mcp_context)
        
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
        
        # 注册安全扫描工具
        self._register_security_tools()
    
    def _register_security_tools(self) -> None:
        """注册安全扫描相关工具。"""
        self.register_tool(
            name="scanner.scan_text",
            handler=self.scan_text,
            description="Scan text for security vulnerabilities (Prompt Injection, Data Leakage, Toxicity, Encoding Bypass)",
            tags=["security", "scan"],
        )
        self.register_tool(
            name="scanner.scan_code",
            handler=self.scan_code,
            description="Scan code for dangerous functions and security issues",
            tags=["security", "code"],
        )
        self.register_tool(
            name="scanner.detect_prompt_injection",
            handler=self.detect_prompt_injection,
            description="Detect prompt injection attacks in text",
            tags=["security", "prompt_injection"],
        )
        self.register_tool(
            name="scanner.detect_data_leakage",
            handler=self.detect_data_leakage,
            description="Detect data leakage patterns (API keys, passwords, etc.)",
            tags=["security", "data_leakage"],
        )
    
    def process(self, message: AgentMessage) -> AgentMessage:
        """Scan content for vulnerabilities."""
        content = message.content
        text = content.get("text", "")
        
        findings = self.scan_text(text)
        
        return self.send(
            receiver="AnalyzerAgent",
            content={
                "original_text": text,
                "findings": findings,
                "vulnerability_count": sum(len(v) for v in findings.values()),
                "scan_complete": True,
            }
        )
    
    def scan_text(self, text: str) -> Dict[str, List[Dict]]:
        """Scan text for vulnerability patterns. (MCP Tool)"""
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
    
    def detect_prompt_injection(self, text: str) -> Dict[str, Any]:
        """Detect prompt injection attacks. (MCP Tool)"""
        patterns = self.vulnerability_patterns["prompt_injection"]
        matches = []
        
        for pattern in patterns:
            found = re.findall(pattern, text, re.IGNORECASE)
            if found:
                matches.extend(found)
        
        return {
            "detected": len(matches) > 0,
            "matches": matches,
            "severity": "critical" if matches else "none",
        }
    
    def detect_data_leakage(self, text: str) -> Dict[str, Any]:
        """Detect data leakage patterns. (MCP Tool)"""
        patterns = self.vulnerability_patterns["data_leakage"]
        matches = []
        
        for pattern in patterns:
            found = re.findall(pattern, text, re.IGNORECASE)
            if found:
                matches.extend(found)
        
        return {
            "detected": len(matches) > 0,
            "matches": matches,
            "severity": "critical" if matches else "none",
        }
    
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
        """Scan code for security issues. (MCP Tool)"""
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
