# AI Investment Advisor

An end-to-end CrewAI project that behaves like a multi-analyst research desk. Specialized agents ingest live market data, parse current news sentiment, quantify risk, and publish a transparent Buy / Hold / Avoid recommendation for any equity ticker. Optional automations deliver the report via WhatsApp, making the stack production-ready out of the box.

## Table of Contents

1. [Key Capabilities](#key-capabilities)
2. [Architecture at a Glance](#architecture-at-a-glance)
3. [Agent Roster](#agent-roster)
4. [Data Sources & External Services](#data-sources--external-services)
5. [Project Structure](#project-structure)
6. [Setup](#setup)
7. [Running the Advisor](#running-the-advisor)
8. [Training Mode](#training-mode)
9. [Output Contract](#output-contract)
10. [Execution Flow](#execution-flow)
11. [Extending & Integrations](#extending--integrations)
12. [License](#license)

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

## Setup

1. **Prerequisites**
   - Python 3.12 (or 3.13) with `uv` or `poetry` installed.
   - Optional: [Ollama](https://ollama.com/) running `llama3.1` locally.

2. **Environment variables**
   ```bash
   cp .env.example .env
   ```
   Then populate the following keys:

   | Variable | Required? | Purpose |
   | --- | --- | --- |
   | `NEWSAPI_KEY` | ✅ | News sentiment agent API key |
   | `OPENAI_API_KEY` | Optional | Only needed if you switch the LLM provider away from Ollama |
   | `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_WHATSAPP_FROM`, `TWILIO_WHATSAPP_TO` | Optional | Enable WhatsApp delivery |

3. **Install dependencies**
   ```bash
   uv pip install -r pyproject.toml
   # or
   poetry install --no-root
   ```

## Running the Advisor

The project ships with console scripts defined in `pyproject.toml`.

```bash
# Default ticker (AMZN)
uv run investment_advisor

# Equivalent if you prefer the module path
uv run python -m investment_advisor.main
```

Customize the ticker or query prompt by editing the `inputs` dictionary inside [`src/investment_advisor/main.py`](src/investment_advisor/main.py). The result is printed to stdout and, if Twilio variables are set, automatically formatted + delivered to WhatsApp.

## Training Mode

Kick off reinforcement/training iterations to refine the crew’s behavior:

```bash
uv run train 5   # runs 5 training iterations with the sample inputs
```

The training loop shares the same input schema and will raise descriptive errors if an iteration fails.

## Output Contract

Every successful run emits a single JSON object:

```json
{
  "stock": "AMZN",
  "price": "181.32",
  "trend": "Bullish",
  "sentiment": "Dominant sentiment: positive (5/8 articles)",
  "risk": "Medium",
  "summary": "Price +0.9% d/d to 181.32; 5-day SMA 179.84; volatility 0.221; headlines skew bullish after cloud contract wins.",
  "recommendation": "BUY - Market momentum and upbeat news outweigh moderate volatility."
}
```

Use this schema to wire the advisor into downstream dashboards, alert systems, or brokerage workflows.

## Execution Flow

1. **MarketDataTask** – fetches yfinance metrics and returns numeric JSON only.
2. **NewsSentimentTask** – calls NewsAPI, buckets article sentiment, and lists representative headlines.
3. **RiskAnalysisTask** – feeds the combined JSON into `RiskAnalyzerTool`, producing a deterministic risk label.
4. **RecommendationTask** – references every prior payload, cites metrics, and outputs the final contract.

The JSON-only hand-off keeps the pipeline explainable, debuggable, and inexpensive (one LLM call per agent).

## Extending & Integrations

- **Swap LLMs** – edit `build_llm()` in `crew.py` to point to OpenAI, Anthropic, or Azure OpenAI without touching task logic.
- **Add delivery channels** – reuse `services/whatsapp_sender.py` as a template for Slack, email, or SMS integrations.
- **New analytics** – drop additional tools into the `tools/` directory and reference them from `agents.yaml` to expand the research surface area.

## License

MIT
