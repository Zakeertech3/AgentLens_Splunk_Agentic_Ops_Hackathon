AgentLens Splunk App v0.1.0

An LLM observability app for Splunk Enterprise that detects prompt injection,
hallucinations, cost runaway, and anomalous agent behavior using Splunk AI Toolkit.

REQUIREMENTS
- Splunk Enterprise 9.x or later
- Splunk AI Toolkit (formerly MLTK) installed
- Python for Scientific Computing installed
- AgentLens SDK sending events to index=agentlens

SETUP
1. Install this app via Manage Apps or by dropping agentlens_app/ into $SPLUNK_HOME/etc/apps/
2. Upload splunk_searches/training_data.csv as a lookup named agentlens_training_data.csv
3. Run the saved search "AgentLens - Train Prompt Injection Classifier"
4. Run the saved search "AgentLens - Train Anomaly Detector"
5. Enable the saved search "AgentLens - Alert Drift Detection" for real-time alerting
6. Open the AgentLens Dashboard

DASHBOARD PANELS
- Live Agent Activity: real-time event timeline
- Prompt Injection Alerts: table of high-confidence injection detections
- Hallucination Score: anomaly trend over time
- Token Cost Forecast: 24h projection with confidence bands
- Per-agent scorecards: counts, injections, anomalies, token totals
- Top Tools Called: bar chart of tool invocation frequency

PYTHON SDK
See https://github.com/Zakeertech3/agentlens for the Python SDK documentation.
