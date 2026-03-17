# AI Investment Advisor

A CrewAI project that behaves like a multi analyst research desk. Specialized agents ingest live market data, parse current news sentiment, quantify risk, and publish a transparent Buy / Hold / Avoid recommendation for any equity ticker. Optional automations deliver the report via WhatsApp, making the stack production ready out of the box.

## Table of Contents

1. [Key Capabilities](#key-capabilities)
2. [Architecture at a Glance](#architecture-at-a-glance)
3. [Agent Roster](#agent-roster)
4. [Data Sources & External Services](#data-sources--external-services)
5. [Project Structure](#project-structure)
6. [Execution Flow](#execution-flow)

## Key Capabilities

- **CrewAI-first architecture** – each task is mapped to an expert agent with clearly scoped prompts, tools, and JSON interfaces.
- **Zero-cost default stack** – yfinance, NewsAPI free tier, and an Ollama-hosted `llama3.1` result in $0 inference cost. Swap in OpenAI or Anthropic by changing a single factory function.
- **Deterministic risk controls** – a rule-based Risk Analyzer Tool standardizes low / medium / high labels for compliance-ready reporting.
- **WhatsApp distribution** – optional Twilio integration formats the CrewAI output into a sharable mobile report.
- **Trainable loop** – kick off reinforcement-style training iterations with a one-liner to continuously improve instructions or models.

## Architecture at a Glance

The system orchestrates four sequential CrewAI agents. Each agent produces structured JSON and never leaves its remit; downstream agents only consume upstream payloads. This JSON-only contract keeps reasoning explainable, cheap, and easy to plug into dashboards or alerting pipelines.

- **Crew definition** lives in [`InvestmentAdvisorCrew`](src/investment_advisor/crew.py).
- **Agent prompts** reside in [`config/agents.yaml`](src/investment_advisor/config/agents.yaml).
- **Task descriptions and expected schemas** are defined in [`config/tasks.yaml`](src/investment_advisor/config/tasks.yaml).

## Agent Roster

| Agent | Responsibility | Tools |
| --- | --- | --- |
| **MarketDataAgent** | Pulls yfinance quotes, short-term trend, volatility, and a 10-day close history. | `MarketDataTool` |
| **NewsSentimentAgent** | Hits NewsAPI for the ticker, counts sentiment, and surfaces representative headlines. | `NewsSentimentTool` |
| **RiskAnalyzerAgent** | Merges market + sentiment JSON, invokes the deterministic risk engine. | `RiskAnalyzerTool` |
| **RecommendationAgent** | Consumes every upstream payload and emits a Buy / Hold / Avoid JSON block. | LLM (no extra tool) |

## Data Sources & External Services

- **yfinance** – live quotes, daily deltas, volatility, and price history.
- **NewsAPI** – latest ticker-specific headlines and metadata for sentiment analysis.
- **LLM provider** – defaults to a local `llama3.1` served via Ollama; edit `build_llm()` inside `crew.py` to point at OpenAI, Anthropic, etc.
- **Twilio WhatsApp API** – optional delivery path for client-facing summaries.

## Outputs

![i1](https://github.com/Reshmagvs/Interdisciplinary_Project/blob/main/project.png)
![i2](https://github.com/Reshmagvs/Interdisciplinary_Project/blob/main/p22.png)
![i3](https://github.com/Reshmagvs/Interdisciplinary_Project/blob/main/pp3.jpeg)

## Project Structure

```text
ai-investment-advisor/
├── pyproject.toml          # Project metadata and entrypoints
├── src/
│   └── investment_advisor/
│       ├── main.py         # CLI + WhatsApp delivery hook
│       ├── crew.py         # CrewAI orchestration
│       ├── config/
│       │   ├── agents.yaml
│       │   └── tasks.yaml
│       ├── tools/          # Market data, news, risk analyzers
│       └── services/       # WhatsApp formatter & sender
└── README.md
```
## Execution Flow

1. **MarketDataTask** – fetches yfinance metrics and returns numeric JSON only.
2. **NewsSentimentTask** – calls NewsAPI, buckets article sentiment, and lists representative headlines.
3. **RiskAnalysisTask** – feeds the combined JSON into `RiskAnalyzerTool`, producing a deterministic risk label.
4. **RecommendationTask** – references every prior payload, cites metrics, and outputs the final contract.

The JSON-only hand-off keeps the pipeline explainable, debuggable, and inexpensive (one LLM call per agent).
