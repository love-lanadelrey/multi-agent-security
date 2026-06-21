# Multi-Agent Security Analysis System

基于多智能体协作的安全分析系统，通过Agent间协作完成漏洞扫描、威胁分析与报告生成。

## 架构设计

```
┌─────────────────┐
│   Orchestrator  │  编排器：协调多个Agent
└────────┬────────┘
         │
    ┌────▼────┐
    │ Scanner │  扫描Agent：识别漏洞模式
    │  Agent  │
    └────┬────┘
         │
    ┌────▼────┐
    │Analyzer │  分析Agent：评估威胁等级
    │  Agent  │
    └────┬────┘
         │
    ┌────▼────┐
    │Reporter │  报告Agent：生成安全报告
    │  Agent  │
    └─────────┘
```

## Agent职责

| Agent | 职责 | 输入 | 输出 |
|-------|------|------|------|
| ScannerAgent | 漏洞扫描 | 文本 | 漏洞发现 |
| AnalyzerAgent | 威胁分析 | 漏洞发现 | 风险评估 |
| ReporterAgent | 报告生成 | 风险评估 | 安全报告 |

## 支持的检测类型

- Prompt Injection（提示词注入）
- Data Leakage（数据泄露）
- Toxicity（有毒内容）
- Encoding Bypass（编码绕过）
- Dangerous Code（危险代码）

## 快速开始

### 本地运行

```bash
pip install -r requirements.txt
python main.py
```

### Docker运行

```bash
docker build -t multi-agent-security .
docker run multi-agent-security
```

### 运行测试

```bash
pytest tests/ -v
```

## 项目结构

```
multi-agent-security/
├── agents/
│   ├── __init__.py
│   ├── base_agent.py        # Agent基类
│   ├── scanner_agent.py     # 漏洞扫描Agent
│   ├── analyzer_agent.py    # 威胁分析Agent
│   └── reporter_agent.py    # 报告生成Agent
├── orchestrator.py          # 多Agent编排器
├── main.py                  # 主程序入口
├── tests/
│   └── test_agents.py       # 单元测试
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

## 核心概念

### 1. Agent间通信

Agent通过`AgentMessage`进行通信，每个Agent接收消息、处理消息、返回响应。

### 2. Pipeline模式

多个Agent按顺序组成Pipeline：Scanner → Analyzer → Reporter

### 3. 单一职责

每个Agent只负责一个特定任务，便于测试和维护。

## 扩展方向

- 添加LLM Agent（使用LangChain/LangGraph）
- 添加更多检测规则
- 实现并行Agent执行
- 添加Agent记忆机制
- 集成向量数据库进行语义分析

## License

MIT
