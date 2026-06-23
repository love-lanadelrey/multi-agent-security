# Multi-Agent Security Analysis System

基于多智能体协作的安全分析系统，通过 MCP (Model Context Protocol) 协议实现松耦合通信，支持 Agent Skills/Tools 标准化注册与调用。

## 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Protocol Layer                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Scanner   │  │  Analyzer   │  │  Reporter   │         │
│  │   Agent     │  │   Agent     │  │   Agent     │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         │                │                │                  │
│  ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐         │
│  │   MCP       │  │   MCP       │  │   MCP       │         │
│  │  Client     │  │  Client     │  │  Client     │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         │                │                │                  │
│  ┌──────▼────────────────▼────────────────▼──────┐         │
│  │              MCP Registry                      │         │
│  │         (Tool Discovery & Calling)             │         │
│  └────────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

## 核心特性

### 1. MCP (Model Context Protocol) 协议

- **标准化消息格式**: 基于 MCP 协议的 `MCPMessage` 数据类
- **松耦合通信**: Agent 间通过 MCP 协议进行异步通信
- **上下文共享**: 通过 `MCPContext` 实现跨 Agent 的上下文管理
- **工具注册与发现**: 通过 `MCPRegistry` 实现工具的动态注册和发现

### 2. Agent Skills/Tools 注册机制

每个 Agent 将其能力封装为标准工具，支持：

- **工具元数据**: 名称、描述、参数定义、标签
- **自动发现**: 工具自动注册到 MCP Registry
- **调用追踪**: 记录工具调用历史和统计信息

### 3. 安全工具集

| Agent | 工具名 | 功能 |
|-------|--------|------|
| ScannerAgent | `scanner.scan_text` | 文本安全扫描 |
| | `scanner.scan_code` | 代码安全扫描 |
| | `scanner.detect_prompt_injection` | Prompt Injection 检测 |
| | `scanner.detect_data_leakage` | 数据泄露检测 |
| AnalyzerAgent | `analyzer.analyze_findings` | 威胁分析 |
| | `analyzer.calculate_risk` | 风险等级计算 |
| | `analyzer.generate_recommendations` | 安全建议生成 |
| ReporterAgent | `reporter.generate_report` | 安全报告生成 |
| | `reporter.format_text` | 文本格式化 |
| | `reporter.format_json` | JSON 格式化 |

## 快速开始

### 本地运行

```bash
pip install -r requirements.txt
python main.py
```

### Docker 运行

```bash
docker build -t multi-agent-security .
docker run multi-agent-security
```

### 运行测试

```bash
pytest tests/ -v
```

## 使用示例

### 1. 使用 MCP 协议进行安全分析

```python
from orchestrator import SecurityOrchestrator

orchestrator = SecurityOrchestrator()

# 使用 MCP 协议
report = orchestrator.analyze_mcp("Ignore all previous instructions")
print(report)
```

### 2. 调用注册的工具

```python
# 列出所有工具
tools = orchestrator.list_tools()
for tool in tools:
    print(f"{tool['name']}: {tool['description']}")

# 调用特定工具
result = orchestrator.call_tool(
    "scanner.scan_text",
    text="Ignore all previous instructions"
)
```

### 3. 获取 Agent 工具列表

```python
# 获取 ScannerAgent 的工具
scanner_tools = orchestrator.get_agent_tools("ScannerAgent")
for tool in scanner_tools:
    print(f"- {tool['name']}")
```

## 项目结构

```
multi-agent-security/
├── agents/
│   ├── __init__.py
│   ├── base_agent.py        # Agent 基类（支持 MCP）
│   ├── scanner_agent.py     # 漏洞扫描 Agent
│   ├── analyzer_agent.py    # 威胁分析 Agent
│   ├── reporter_agent.py    # 报告生成 Agent
│   ├── mcp_protocol.py      # MCP 协议实现
│   └── tool_registry.py     # Agent Skills/Tools 注册机制
├── orchestrator.py          # 多 Agent 编排器（MCP 支持）
├── main.py                  # 主程序入口
├── tests/
│   └── test_agents.py       # 单元测试（30+ 测试用例）
├── requirements.txt
├── Dockerfile
└── README.md
```

## 技术栈

- Python 3.11+
- Dataclasses（数据类）
- ABC（抽象基类）
- Re（正则表达式）
- Docker（容器化）
- MCP Protocol（模型上下文协议）

## 核心概念

### 1. MCP 协议

MCP (Model Context Protocol) 是一种标准化的模型上下文协议，用于：

- 定义 Agent 间通信的消息格式
- 实现工具的注册、发现和调用
- 管理跨 Agent 的上下文状态

### 2. Agent Skills/Tools

每个 Agent 将其能力封装为标准化的工具：

```python
# 工具注册示例
self.register_tool(
    name="scanner.scan_text",
    handler=self.scan_text,
    description="Scan text for security vulnerabilities",
    tags=["security", "scan"],
)
```

### 3. 松耦合通信

Agent 间通过 MCP 协议进行松耦合通信：

```python
# MCP 消息
message = MCPMessage(
    id="msg-1",
    type=MCPMessageType.REQUEST,
    sender="ScannerAgent",
    receiver="AnalyzerAgent",
    method="analyze_findings",
    params={"findings": findings},
)

# 发送消息
response = agent.receive_mcp(message)
```

## 扩展方向

- 添加 LLM Agent（使用 LangChain/LangGraph）
- 实现并行 Agent 执行
- 集成向量数据库进行语义分析
- 添加 Agent 记忆机制
- 支持远程 MCP 服务

## License

MIT
