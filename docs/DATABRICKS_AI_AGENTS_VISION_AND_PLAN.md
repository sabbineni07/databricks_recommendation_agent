# Databricks AI Agents: Vision, Use Cases, and Strategic Plan

This document presents the vision for AI-powered agents in Databricks data engineering, the value they deliver, how they connect, and the technical plan to deliver them.

---

## Part 1: Use Cases, Relationships, and Business Value

### Overview of AI Agent Use Cases

| # | Agent | Purpose | Status |
|---|-------|---------|--------|
| 1 | **Cluster Resource Analyzer & Recommender** | Optimize cluster configurations based on utilization patterns | ✅ Current |
| 2 | **Job Cluster Log Analyzer** | Analyze Spark plans and cluster logs for performance insights | Planned |
| 3 | **Job Failure RCA Agent** | Root cause analysis and recommendations for job failures | Planned |
| 4 | **Data Engineering Pipeline Agent** | Build pipelines from STTM mapping documentation | Planned |
| 5 | **Semantic Data Type Agent** | Generate and tag semantic data types from raw data | Planned |
| 6 | **Data Quality Checks Agent** | Auto-generate and run data quality checks | Planned |

---

### How the Agents Relate to Each Other

```
                    ┌─────────────────────────────────────────────────────────────┐
                    │                    DATA ENGINEERING LIFECYCLE                 │
                    └─────────────────────────────────────────────────────────────┘

    ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
    │  1. DESIGN   │────▶│  2. BUILD    │────▶│  3. RUN      │────▶│  4. MONITOR  │
    │   & PLAN     │     │   & DEVELOP  │     │   & EXECUTE  │     │   & OPTIMIZE │
    └──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
          │                      │                     │                     │
          │                      │                     │                     │
          ▼                      ▼                     ▼                     ▼
    ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
    │ Pipeline     │     │ Semantic     │     │ Log Analyzer │     │ Cluster      │
    │ Agent        │     │ Data Type    │     │              │     │ Recommender  │
    │ (STTM)       │     │ Agent        │     └──────┬───────┘     │              │
    └──────────────┘     └──────────────┘            │             └──────┬───────┘
          │                      │                   │                    │
          │                      │                   │                    │
          └──────────────────────┼───────────────────┼────────────────────┘
                                 │                   │
                                 ▼                   ▼
                          ┌──────────────┐    ┌──────────────┐
                          │ Data Quality │    │ Failure RCA  │
                          │ Agent        │    │ Agent        │
                          └──────────────┘    └──────────────┘
```

**Relationships:**

| Agent | Feeds Into | Receives From | Shared Context |
|-------|------------|---------------|----------------|
| **Cluster Recommender** | Log Analyzer (config context), Failure RCA | Job metrics, utilization data | Resource usage, cost |
| **Log Analyzer** | Failure RCA, Cluster Recommender | Cluster logs, Spark plans | Performance bottlenecks |
| **Failure RCA** | Cluster Recommender, Data Quality | Log Analyzer, failure events | Root causes, patterns |
| **Pipeline Agent** | Semantic Data Type, Data Quality | STTM docs, mapping specs | Pipeline logic, schemas |
| **Semantic Data Type** | Pipeline Agent, Data Quality | Raw data, schemas | Data classifications |
| **Data Quality Agent** | All agents (trusted data) | Semantic types, pipeline outputs | Quality rules, anomalies |

---

### Value Proposition by Agent

#### 1. Cluster Resource Utilization Analyzer & Recommendation Agent

**What it does:** Analyzes historical job metrics and recommends optimal cluster configurations (node type, workers, auto-termination).

**Why it matters:**
- **Cost savings:** 20–40% reduction in cluster spend by right-sizing.
- **Performance:** Fewer OOMs and throttling; better resource utilization.
- **Governance:** Consistent, data-driven sizing instead of guesswork.

**Value to leaders:** Direct, measurable cost reduction and more predictable cloud spend.

---

#### 2. Job Cluster Log Analyzer

**What it does:** Analyzes Spark logical/physical plans, stdout, stderr, and cluster logs to identify performance issues, skew, and bottlenecks.

**Why it matters:**
- **Observability:** Turn raw logs into structured insights.
- **Proactive tuning:** Spot issues before they cause failures.
- **Knowledge retention:** Preserve tribal knowledge in a searchable, AI-assisted form.

**Value to leaders:** Faster incident resolution and better engineering productivity.

---

#### 3. Job Failure RCA Agent

**What it does:** Performs root cause analysis on failed jobs and suggests remediation.

**Why it matters:**
- **MTTR reduction:** Cut diagnosis time from hours to minutes.
- **Learning loop:** Capture failure patterns and prevent recurrence.
- **SLA impact:** Fewer repeated failures and faster recovery.

**Value to leaders:** Improved reliability, SLAs, and reduced firefighting.

---

#### 4. Data Engineering Pipeline Agent

**What it does:** Builds ETL/ELT pipelines from STTM (Source-to-Target Mapping) documentation.

**Why it does:**
- **Faster delivery:** Translate specs into code with minimal manual coding.
- **Consistency:** Pipelines aligned with documented mappings.
- **Onboarding:** New engineers can deliver pipelines faster.

**Value to leaders:** Shorter time-to-value and higher throughput from data engineering.

---

#### 5. Semantic Data Type Agent

**What it does:** Infers and tags semantic data types (PII, currency, dates, entities) from raw data.

**Why it matters:**
- **Data governance:** Automatic classification for compliance and privacy.
- **Discovery:** Easier search and understanding of data assets.
- **Quality:** Better data quality rules and lineage.

**Value to leaders:** Stronger data governance and faster compliance.

---

#### 6. Data Quality Checks Agent

**What it does:** Generates and executes data quality checks (completeness, validity, consistency).

**Why it matters:**
- **Trust:** Higher confidence in downstream analytics and ML.
- **Automation:** Less manual work on checks and monitoring.
- **Prevention:** Catch issues early in the pipeline.

**Value to leaders:** Better data reliability and lower downstream impact.

---

### Cumulative Value for Leadership

| Benefit | Contributing Agents | Impact |
|---------|---------------------|--------|
| **Cost reduction** | Cluster Recommender | 20–40% cluster spend savings |
| **Faster delivery** | Pipeline Agent, Semantic Type | 30–50% faster pipeline development |
| **Higher reliability** | Failure RCA, Data Quality | Reduced MTTR, fewer incidents |
| **Better governance** | Semantic Type, Data Quality | Compliance, auditability |
| **Engineering productivity** | All agents | Less manual analysis, more automation |
| **Scale without linear headcount** | All agents | Do more with the same team |

---

### Why Build These Together

1. **Shared data and context:** Job metrics, logs, and metadata can be reused across agents.
2. **Consistent infrastructure:** One platform (Foundry/Azure OpenAI), one RAG/search layer.
3. **Compounding value:** Each agent improves the effectiveness of others.
4. **Unified experience:** One AI-assisted workspace for data engineering.

---

## Part 2: Technical Analysis, Recommendations, and Plan

This section summarizes the analysis performed on Azure AI options, model providers, and migration strategy.

---

### Option A vs Option B: Azure AI Integration

| Aspect | Option A: Foundry + Model Inference API | Option B: Azure OpenAI Resource |
|--------|----------------------------------------|---------------------------------|
| **Resource** | Foundry project (ai.azure.com) | Separate Azure OpenAI resource |
| **Endpoint** | `*.services.ai.azure.com` | `*.openai.azure.com` |
| **Package** | `langchain-azure-ai` | `langchain-openai` |
| **Models** | OpenAI + Cohere, Mistral, Llama, etc. | OpenAI only |
| **Maturity** | Newer, evolving | Stable, widely adopted |

**Current project status:** Uses Option B's client (`AzureChatOpenAI`) against a Foundry resource via compatibility. Not full Option A support.

**Recommendation:** Stay with Option B for now. Revisit migration to Option A in 6–12 months when packages and docs mature.

---

### Model Provider Recommendation

| Use Case | Recommended Provider | Rationale |
|----------|----------------------|-----------|
| Cluster recommendation | **OpenAI (GPT-4o)** | Strong reasoning, structured output |
| Job failure RCA | **OpenAI (GPT-4o)** | Analytical and explanatory strength |
| Log analyzer | **OpenAI (GPT-4o)** | Long context, technical understanding |
| Pipeline building | **OpenAI (GPT-4o)** | Doc understanding + code generation |
| Semantic tagging | **OpenAI (text-embedding-3-small)** | Embeddings, classification |
| Data quality checks | **OpenAI (GPT-4o)** | Reasoning + code generation |

**Overall:** OpenAI (GPT-4o + text-embedding-3-small) is the recommended primary model for all planned agents.

---

### Embeddings Support

| Option | Embeddings | text-embedding-3-small |
|--------|------------|------------------------|
| Option A (Foundry) | ✅ `AzureAIEmbeddingsModel` | ✅ Supported |
| Option B (Azure OpenAI) | ✅ `AzureOpenAIEmbeddings` | ✅ Supported |

Both options support embeddings; no change needed for semantic tagging or RAG.

---

### Dual Support (Option A + B via Flag)

**Recommendation:** Do **not** add a flag to support both options.

- Increases maintenance and testing.
- Adds dependencies on both packages.
- Little benefit for current use case.
- Migration to Option A later can be a clean one-time cutover.

---

### Migration Plan

| Phase | Action | Timeline |
|-------|--------|----------|
| **Now** | Stay on Option B, use Foundry resource via compatibility | Current |
| **Ongoing** | Monitor `langchain-azure-ai` maturity and docs | 6–12 months |
| **Later** | Evaluate migration to Option A when ecosystem is mature | When beneficial |
| **Future** | Consider Cohere (RAG) or Mistral (cost) for specific agents | As needed |

---

### Summary of Technical Decisions

| Decision | Choice |
|----------|--------|
| Primary integration | Option B (Azure OpenAI client) |
| LLM | GPT-4o |
| Embeddings | text-embedding-3-small |
| Dual support | No |
| Migration to Option A | Defer 6–12 months |
| Model provider | OpenAI for all current and planned agents |

---

*Last updated: February 2025*
