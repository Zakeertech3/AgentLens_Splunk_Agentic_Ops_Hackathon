# AgentLens Architecture

Render the diagram below at [mermaid.live](https://mermaid.live) or with the VS Code Mermaid extension, then save the PNG as `docs/architecture.png`.

```mermaid
graph TB
    subgraph Client["Python Application (User's Code)"]
        APP[Demo App: WanderBot<br/>CrewAI + LangGraph]
        SDK[AgentLens SDK<br/>agentlens.instrument]
    end

    subgraph OTel["OpenTelemetry Layer"]
        AUTO[OpenInference Auto-Instrumentors<br/>CrewAI, LangChain, OpenAI]
        TP[TracerProvider]
        BSP[BatchSpanProcessor]
        EXP[Custom HEC Exporter<br/>OTel Span to Splunk Event]
    end

    subgraph Splunk["Splunk Enterprise (localhost)"]
        HEC[HTTP Event Collector<br/>:8088]
        IDX[(Index: agentlens)]
        AITK[AI Toolkit]
        DASH[AgentLens Dashboard<br/>7 panels]
    end

    subgraph Models["Splunk ML Models (Layered Defense)"]
        TFIDF[TFIDF Vectorizer<br/>Feature Extraction]
        GB[GradientBoostingClassifier<br/>Layer 1: Prompt Injection]
        DF[DensityFunction<br/>Layer 2: Token Anomalies]
    end

    APP -->|imports| SDK
    SDK -->|configures| AUTO
    AUTO -->|emits spans| TP
    TP --> BSP
    BSP --> EXP
    EXP -->|HTTP POST| HEC
    HEC --> IDX
    IDX --> AITK
    AITK --> TFIDF
    AITK --> DF
    TFIDF --> GB
    GB --> DASH
    DF --> DASH

    style SDK fill:#4a9eff
    style EXP fill:#4a9eff
    style HEC fill:#7c4dff
    style IDX fill:#7c4dff
    style AITK fill:#7c4dff
    style TFIDF fill:#ff6b6b
    style GB fill:#ff6b6b
    style DF fill:#ff6b6b
```

## Data Flow

`agentlens.instrument()` registers three OpenInference instrumentors (CrewAI, LangChain, OpenAI) against a single `TracerProvider` backed by a `BatchSpanProcessor`. Every agent call, LLM invocation, and tool execution emits an OTel span; the exporter converts each span to a Splunk HEC JSON event and POSTs them in newline-delimited batches to port 8088. Events land in `index=agentlens` with sourcetype `agentlens:event`. Splunk AI Toolkit runs two ML detection layers against the index: Layer 1 is a TF-IDF vectorizer feeding a GradientBoostingClassifier trained on 550 labeled prompts (including embedded-injection patterns) that catches direct prompt injection attacks; Layer 2 is a DensityFunction trained on LLM token-usage distributions that catches anomalies like cost-runaway attacks the classifier misses. Results surface in a 7-panel Dashboard Studio view with single-value scorecards, timecharts, and a flagged-events table.
