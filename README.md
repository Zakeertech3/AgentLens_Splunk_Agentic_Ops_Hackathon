# AgentLens

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org)
[![Splunk](https://img.shields.io/badge/Splunk-Enterprise%209.x-black)](https://www.splunk.com)

**One-line observability for LLM agents. Catch prompt injection, hallucinations, and cost runaway before they reach production.**

AgentLens is an open-source Python SDK that auto-instruments [CrewAI](https://github.com/joaomdmoura/crewAI) and [LangGraph](https://github.com/langchain-ai/langgraph) agents with a single line of code, streaming structured telemetry to Splunk via HEC. A companion Splunk app uses classical ML (Splunk AI Toolkit) to detect adversarial inputs and anomalous agent behavior in real time.

---

## The Problem

Teams building with LLM agents fly blind. The standard observability stack (Splunk, Datadog, New Relic) was designed for traditional applications, not for non-deterministic agentic systems. Three pain points compound this gap:

1. **Prompt injection is invisible.** When a user input causes an agent to ignore its instructions, there is no log line that says "hijacked." It looks like a normal LLM call.

2. **Anomalies hide in plain text.** A 1500-token agent loop that burns through your API budget looks identical to a 500-token healthy call from the outside — both return 200 OK.

3. **Multi-framework chaos.** Teams use CrewAI, LangGraph, OpenAI Agents SDK, and Anthropic SDK in the same codebase. Each has its own trace format. None of them speak to your existing SIEM.

AgentLens closes the gap by sitting between the agent runtime and Splunk. One pip install. One line of code. Every agent call becomes a structured event your SOC or SRE team can query, alert on, and reason about.

---

---

## Live Dashboard

After running the WanderBot demo with all five attack scenarios, the AgentLens dashboard surfaces both detection layers working on real data:

<img width="1791" height="908" alt="Image" src="https://github.com/user-attachments/assets/a5aef6f5-5ef2-490b-9752-f4e22df0f061" />

**Layer 1 (top-left, Prompt Injection Alerts):** TF-IDF + GradientBoostingClassifier flags 50 prompts containing embedded injection patterns across 499 total events.

**Layer 2 (top-right, Anomaly Score Over Time):** DensityFunction trained on token-usage distribution catches statistical outliers the classifier misses — specifically the cost-runaway attack that produced 1500+ token responses.

<img width="1766" height="916" alt="Image" src="https://github.com/user-attachments/assets/322f0033-9a2d-4f9d-b43a-5a21272836de" />

**Defense-in-depth scoreboard:** 499 total events monitored, 50 injections detected by Layer 1, 2 anomalies caught by Layer 2 (including the cost-runaway agent loop that consumed 29,357 tokens). The Top Agent Flows chart shows ten distinct CrewAI execution nodes, giving SRE teams visibility into agent reasoning paths.

The dashboard updates in real-time as new events arrive via Splunk HEC. No restart, no config changes — install the AgentLens Splunk app and the panels populate from `index=agentlens`.


## Architecture

<img width="4438" height="8192" alt="Image" src="https://github.com/user-attachments/assets/296dbc80-7475-4b4f-a394-a71667c91999" />

```
Python App (CrewAI / LangGraph)
        |
   agentlens.instrument()
        |
   OpenInference Auto-Instrumentors
   (CrewAI, LangChain, OpenAI)
        |
   TracerProvider + BatchSpanProcessor
        |
   SplunkHECSpanExporter
        |
   HTTP POST --> Splunk HEC :8088
        |
   index=agentlens
        |
   Splunk AI Toolkit
        |
   TFIDF -> GradientBoostingClassifier   (Layer 1: prompt injection)
   DensityFunction                       (Layer 2: token anomalies)
        |
   AgentLens Dashboard (7 panels)
```

See [docs/architecture.md](docs/architecture.md) for the full Mermaid diagram.

---

## Features

- **One-line instrumentation** — `agentlens.instrument()` patches CrewAI, LangChain, and OpenAI automatically via OpenInference
- **Splunk HEC exporter** — every span becomes a structured JSON event in `index=agentlens` with no schema changes required
- **Prompt injection detection (Layer 1)** — TF-IDF + GradientBoostingClassifier trained on 550 labeled prompts including realistic embedded-injection patterns from CrewAI task wrappers; flags every LLM call in real time
- **Token anomaly detection (Layer 2)** — DensityFunction trained on LLM token-usage distributions catches statistical outliers like cost runaway that pattern-matching misses
- **Token usage trend** — area chart of tokens consumed per 15-minute window with estimated USD cost
- **Live dashboard** — seven-panel dark-themed Splunk dashboard with timeline, alerts table, anomaly trend, token trend, scorecards, and agent flow chart
- **WanderBot demo** — a CrewAI travel booking agent with five intentional vulnerabilities that AgentLens catches live

---

## Quick Start (5 minutes)

### 1. Install

```bash
git clone https://github.com/Zakeertech3/AgentLens_Splunk_Agentic_Ops_Hackathon.git
cd agentlens
uv pip install -e .
```

### 2. Configure

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

```
SPLUNK_HEC_URL=http://localhost:8088/services/collector
SPLUNK_HEC_TOKEN=your-hec-token-here
SPLUNK_INDEX=agentlens
SPLUNK_SOURCETYPE=agentlens:event
GROQ_API_KEY=your-groq-key-here
GROQ_MODEL=llama-3.3-70b-versatile
```

### 3. Instrument

```python
import agentlens
agentlens.instrument(service_name="my-agent")

# Any CrewAI or LangGraph code below is now fully traced
from crewai import Agent, Task, Crew
...
```

### 4. Verify

```bash
python scripts/verify_hec.py verify
```

This sends a test span to Splunk and prints a status table. Open `http://localhost:8000` and search `index=agentlens` to confirm.

---

## WanderBot Demo

WanderBot is a CrewAI travel booking assistant with three agents (researcher, booking specialist, customer communications) and five intentionally injected vulnerabilities.

### Run the happy path

```powershell
python -m demo.wanderbot.main book --origin HYD --destination NRT --date 2026-06-15 --name "Test User" --email test@example.com
```

### Run attack scenarios

```powershell
python demo\wanderbot\attacks.py prompt-injection
python demo\wanderbot\attacks.py hallucination
python demo\wanderbot\attacks.py cost-runaway
python demo\wanderbot\attacks.py data-exfiltration
python demo\wanderbot\attacks.py system-prompt-leak
```

### Run the LangGraph variant

```powershell
python demo\wanderbot\langgraph_variant.py
```

See [docs/attacks.md](docs/attacks.md) for a detailed walkthrough of each attack and what AgentLens catches.

---

## Splunk Setup

For detailed step-by-step instructions, see [docs/splunk-setup.md](docs/splunk-setup.md).

1. Install Splunk Enterprise 9.x and apply a Developer License.
2. Install **Splunk AI Toolkit** and **Python for Scientific Computing for Windows 64-bit** from Splunkbase. On Windows, first enable long paths via Registry: set `HKLM\SYSTEM\CurrentControlSet\Control\FileSystem\LongPathsEnabled` to `1` (DWORD) and restart Windows. Without this, the Python for Scientific Computing add-on fails to extract.
3. Enable HEC: Settings → Data inputs → HTTP Event Collector → Global Settings → turn on. Create a token named `agentlens-token` with index `agentlens` and sourcetype `agentlens:event`. Copy the token value into `.env`.
4. Create index `agentlens`: Settings → Indexes → New Index. Leave all defaults.
5. Upload the training lookup: Settings → Lookups → Lookup table files → Add new. Upload `splunk_searches/training_data.csv`, name it `agentlens_training_data.csv`, destination app `search`.
6. In Search & Reporting, run the two training SPL files from `splunk_searches/` in order: `01_train_prompt_injection_classifier.spl` then `02_train_anomaly_detector.spl`. These save the ML models that power the dashboard. The other two SPL files (`03_forecast_token_cost.spl` and `04_alert_drift_detection.spl`) are reference queries used by the dashboard panels and saved searches.
7. Set Global permissions on the trained models so the dashboard can read them: Settings → Lookups → Lookup table files (filter by App: Search & Reporting). For each of `__mlspl_agentlens_tfidf_vectorizer.mlmodel`, `__mlspl_agentlens_prompt_injection_classifier.mlmodel`, and `__mlspl_agentlens_density_tokens.mlmodel`, click Permissions → set sharing to All apps (system), Read for Everyone, Write for admin. Do the same for `agentlens_training_data.csv`.
8. Install the app: Apps → Manage Apps → Install app from file → upload `agentlens_app.spl`. Restart if prompted. The AgentLens Dashboard appears in the nav bar.

---

## Splunk ML Searches

| File | Purpose |
|------|---------|
| `splunk_searches/01_train_prompt_injection_classifier.spl` | Train TF-IDF vectorizer and GradientBoosting classifier on 550 labeled prompts |
| `splunk_searches/02_train_anomaly_detector.spl` | Train DensityFunction on LLM token-usage distribution |
| `splunk_searches/03_forecast_token_cost.spl` | Plain 24-hour token usage and cost trend (used by dashboard) |
| `splunk_searches/04_alert_drift_detection.spl` | 5-minute drift detection across both ML layers (used by saved search alert) |

Copy-paste each into Splunk Search and Reporting after training data is uploaded.

---

## Package the Splunk App

```powershell
python scripts\package_splunk_app.py package
```

This produces `agentlens_app.spl` in the project root, ready to install via Splunk's Manage Apps interface.

---

## Seed Training Data

```powershell
python scripts\seed_training_data.py
```

Generates `splunk_searches/training_data.csv` with 550 labeled prompts: 270 benign travel queries (including some wrapped in CrewAI Task format) and 280 malicious prompts across six injection categories including embedded-injection patterns that match realistic agent contexts. The CSV is tracked in git so judges can reproduce the demo without re-running this script.

---

## Project Structure

```
agentlens/
├── src/agentlens/          # Python SDK
│   ├── __init__.py         # public API: instrument, shutdown
│   ├── config.py           # pydantic_settings config singleton
│   ├── exporter.py         # SplunkHECSpanExporter
│   ├── instrumentor.py     # TracerProvider + OpenInference wiring
│   ├── conventions.py      # OpenInference attribute mapping
│   └── version.py
├── demo/wanderbot/         # WanderBot CrewAI demo
│   ├── main.py             # typer CLI: book, info
│   ├── attacks.py          # typer CLI: 5 attack scenarios
│   ├── langgraph_variant.py
│   ├── agents.py
│   ├── tasks.py
│   ├── tools.py
│   └── data/flights.json
├── scripts/
│   ├── verify_hec.py       # Phase 1 smoke test
│   ├── seed_training_data.py
│   └── package_splunk_app.py
├── splunk_searches/        # Copy-paste SPL into Splunk
│   ├── training_data.csv
│   ├── 01_train_prompt_injection_classifier.spl
│   ├── 02_train_anomaly_detector.spl
│   ├── 03_forecast_token_cost.spl
│   └── 04_alert_drift_detection.spl
├── splunk_app/agentlens_app/   # Installable Splunk app
│   ├── default/
│   │   ├── app.conf
│   │   ├── savedsearches.conf
│   │   ├── props.conf
│   │   ├── transforms.conf
│   │   └── data/ui/views/agentlens_dashboard.xml
│   └── metadata/default.meta
├── docs/
│   ├── architecture.md
│   ├── attacks.md
│   └── splunk-setup.md
├── pyproject.toml
├── LICENSE
└── .env.example
```

---

## Configuration Reference

All config is loaded from `.env` via `pydantic_settings`:

| Variable | Default | Description |
|----------|---------|-------------|
| `SPLUNK_HEC_URL` | `http://localhost:8088/services/collector` | HEC endpoint |
| `SPLUNK_HEC_TOKEN` | (required) | HEC token from Splunk |
| `SPLUNK_INDEX` | `agentlens` | Target index |
| `SPLUNK_SOURCETYPE` | `agentlens:event` | Sourcetype |
| `SERVICE_NAME` | `agentlens` | Default service name for spans |
| `DEBUG` | `false` | Enable verbose exporter logging |
| `GROQ_API_KEY` | (required for demo) | Groq API key |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Groq model name |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Agent frameworks | CrewAI 1.x, LangGraph |
| Auto-instrumentation | OpenInference (CrewAI, LangChain, OpenAI instrumentors) |
| Telemetry | OpenTelemetry SDK (TracerProvider, BatchSpanProcessor) |
| Transport | httpx, Splunk HEC |
| ML | Splunk AI Toolkit (TFIDF + GradientBoostingClassifier for prompt injection, DensityFunction for token anomalies) |
| Config | pydantic-settings |
| CLI | Typer + Rich |
| LLM (demo) | Groq (llama-3.3-70b-versatile) via OpenAI-compatible endpoint |

---

## Roadmap

AgentLens v0.1.0 ships the foundational layers. The following are planned for future releases and were intentionally descoped from the hackathon submission to keep the demo focused and reliable:

### v0.2.0 — Forecasting & Predictive Alerts
- StateSpaceForecast integration for 24-hour token cost projection with 95% confidence intervals
- LocalOutlierFactor as a third detection layer for multi-dimensional behavior outliers
- Per-agent cost budgets with automatic throttling when forecast exceeds threshold

### v0.3.0 — MCP Server Integration
- Autonomous alert agent powered by Splunk MCP Server
- Self-tuning detection thresholds based on observed traffic patterns
- Auto-generated incident reports from grouped alerts

### v0.4.0 — Expanded Framework Support
- OpenAI Agents SDK auto-instrumentation
- Anthropic Claude SDK auto-instrumentation
- AutoGen and Pydantic AI support
- Standalone instrumentation for raw LLM API calls without an agent framework

### v0.5.0 — Hallucination Detection
- LLM-as-judge pattern using Splunk-hosted gpt-oss-20b for response verification
- Citation grounding checks against tool outputs
- Confidence scoring per response

### v1.0.0 — Production Hardening
- Async HEC exporter for high-throughput environments
- Retry queue with exponential backoff
- Persistent buffer for offline-then-online scenarios
- Comprehensive test suite with mocked Splunk
- PyPI publication and Splunkbase certification

---

## License

MIT. See [LICENSE](LICENSE).
