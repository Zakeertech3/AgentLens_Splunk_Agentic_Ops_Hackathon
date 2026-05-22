# Splunk Setup Guide

Tested on Splunk Enterprise 9.x on Windows with Developer License.

## Prerequisites

1. Splunk Enterprise 9.x running on localhost:8000
2. Developer License applied (request at https://dev.splunk.com)
3. Windows long paths enabled: set registry key `HKLM\SYSTEM\CurrentControlSet\Control\FileSystem\LongPathsEnabled = 1`, then restart Splunk

## Step 1: Install Required Splunk Apps

Apps > Find more apps:

1. Splunk AI Toolkit (formerly MLTK)
2. Python for Scientific Computing for Windows 64-bit

Restart Splunk after each install.

## Step 2: Enable HTTP Event Collector

1. Settings > Data inputs > HTTP Event Collector > Global Settings
2. All Tokens: Enabled, uncheck Enable SSL, port 8088
3. New Token: name `agentlens-token`, sourcetype `agentlens:event`, index `agentlens`
4. Copy the token value into `.env` as `SPLUNK_HEC_TOKEN`

## Step 3: Upload Training Data

1. Settings > Lookups > Lookup table files > New Lookup Table File
2. Destination app: search
3. Upload: `splunk_searches/training_data.csv`
4. Destination filename: `agentlens_training_data.csv`
5. After save: set permissions to Global (Read: Everyone, Write: admin)

## Step 4: Train the Models

In Search and Reporting, run each file content in order. Time range: All time.

1. `splunk_searches/01_train_prompt_injection_classifier.spl` — saves `agentlens_tfidf_vectorizer` and `agentlens_prompt_injection_classifier`
2. `splunk_searches/02_train_anomaly_detector.spl` — saves `agentlens_density_tokens`

After training, set Global permissions on all three model files in Settings > Lookups > Lookup table files:

- `__mlspl_agentlens_tfidf_vectorizer.mlmodel`
- `__mlspl_agentlens_prompt_injection_classifier.mlmodel`
- `__mlspl_agentlens_density_tokens.mlmodel`

This step is required. Models saved in the Search app context are not visible to the AgentLens app without Global sharing.

## Step 5: Install the AgentLens App

```powershell
python scripts\package_splunk_app.py package
```

Apps > Manage Apps > Install app from file > upload `agentlens_app.spl`. Restart when prompted.

## Step 6: Configure the Python Client

```powershell
copy .env.example .env
```

Fill in `SPLUNK_HEC_TOKEN` and `GROQ_API_KEY`. Then:

```powershell
uv pip install -e .
python scripts\verify_hec.py verify
```

## Step 7: Generate Demo Data

```powershell
python -m demo.wanderbot.main book --origin HYD --destination NRT --date 2026-06-15 --name "Test User" --email test@example.com

python demo\wanderbot\attacks.py prompt-injection
python demo\wanderbot\attacks.py hallucination
python demo\wanderbot\attacks.py cost-runaway
python demo\wanderbot\attacks.py data-exfiltration
python demo\wanderbot\attacks.py system-prompt-leak
```

## Step 8: Open the Dashboard

Apps > AgentLens. The LLM Observability dashboard populates within 30 seconds of demo data arriving.
