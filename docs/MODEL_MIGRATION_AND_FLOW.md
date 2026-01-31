# Model Migration Plan & End-to-End Flow

## Table of Contents
1. [Current Model Analysis](#current-model-analysis)
2. [Model Migration Plan](#model-migration-plan)
3. [Cost Comparison](#cost-comparison)
4. [Token Usage Analysis](#token-usage-analysis)
5. [End-to-End Flow Diagram](#end-to-end-flow-diagram)
6. [Migration Steps](#migration-steps)

---

## Current Model Analysis

### Current Models

| Model | Type | Usage | Current Deployment |
|-------|------|-------|-------------------|
| **gpt-4-turbo** | Chat/LLM | Pattern Analysis, Cost Optimization, Explanations | `gpt-4-turbo` |
| **text-embedding-ada-002** | Embeddings | Azure AI Search (indexing & similarity search) | `text-embedding-ada-002` |

### Current Model Usage in Code Flow

#### gpt-4-turbo (Chat Model)
- **PatternAnalysisChain** (`AI/src/chains/pattern_analysis_chain.py:15`)
  - Analyzes job metrics to identify workload patterns
  - Input: Aggregated job metrics dictionary
  - Output: Text analysis of workload characteristics
  
- **CostOptimizationChain** (`AI/src/chains/cost_optimization_chain.py:16`)
  - Generates structured JSON recommendations
  - Input: Current config, job metrics, budget constraints, **pattern_analysis** (from PatternAnalysisChain)
  - Output: JSON with node family, vCPUs, workers, etc.
  - **Note:** Now receives pattern_analysis to improve recommendation accuracy
  
- **ExplanationChain** (`AI/src/chains/explanation_chain.py:15`)
  - Generates detailed explanations
  - Input: Recommendation, metrics, analysis, risk assessment
  - Output: Comprehensive text explanation

#### text-embedding-ada-002 (Embeddings)
- **AzureSearchService.index_recommendation()** (`AI/src/services/azure_search_service.py:37`)
  - Creates embeddings from recommendation text for indexing
  
- **AzureSearchService.search_similar()** (`AI/src/services/azure_search_service.py:67`)
  - Creates query embeddings for similarity search

---

## Model Migration Plan

### Recommended Models

| Current | Recommended | Reason |
|---------|-------------|--------|
| `gpt-4-turbo` | `gpt-4o` | Better cost/performance, faster, newer |
| `text-embedding-ada-002` | `text-embedding-3-small` | Better performance, similar cost, newer |

### Alternative Options

#### For LLM (Chat Model)

1. **gpt-4o** (Recommended)
   - ✅ Faster than gpt-4-turbo
   - ✅ Lower cost (~50% cheaper)
   - ✅ Better performance on structured outputs
   - ✅ Same or better reasoning capabilities
   - ⚠️ Newer model (may need testing)

2. **gpt-4o-mini** (Cost-Optimized)
   - ✅ Much cheaper (~80% cheaper than gpt-4-turbo)
   - ✅ Fast
   - ⚠️ Less capable for complex reasoning
   - 💡 Good for simpler tasks or cost-sensitive scenarios

3. **gpt-3.5-turbo** (Budget Option)
   - ✅ Very cheap
   - ⚠️ Less capable for complex technical analysis
   - ⚠️ May struggle with structured JSON output
   - ❌ Not recommended for this use case

#### For Embeddings

1. **text-embedding-3-small** (Recommended)
   - ✅ Better performance than ada-002
   - ✅ Similar cost (~$0.02 per 1M tokens)
   - ✅ Same dimensions (1536) - no index migration needed
   - ✅ Newer model with better accuracy

2. **text-embedding-3-large** (Performance Option)
   - ✅ Best performance
   - ✅ Higher dimensions (3072) - better accuracy
   - ⚠️ Higher cost (~$0.13 per 1M tokens)
   - ⚠️ Requires index migration (dimension change)

---

## Cost Comparison

### Pricing (as of 2024, approximate)

#### Chat Models (per 1M tokens)

| Model | Input Cost | Output Cost | Total (avg request) |
|-------|-----------|-------------|-------------------|
| **gpt-4-turbo** | $10.00 | $30.00 | ~$0.15-0.30 per request |
| **gpt-4o** | $5.00 | $15.00 | ~$0.08-0.15 per request |
| **gpt-4o-mini** | $0.15 | $0.60 | ~$0.002-0.005 per request |
| **gpt-3.5-turbo** | $0.50 | $1.50 | ~$0.01-0.02 per request |

#### Embeddings (per 1M tokens)

| Model | Cost | Dimensions |
|-------|------|------------|
| **text-embedding-ada-002** | $0.10 | 1536 |
| **text-embedding-3-small** | $0.02 | 1536 |
| **text-embedding-3-large** | $0.13 | 3072 |

### Estimated Monthly Costs

**Assumptions:**
- 1,000 recommendations per month
- Average: 2,000 input tokens, 500 output tokens per LLM call
- 3 LLM calls per recommendation (pattern, cost, explanation)
- 1 embedding call per recommendation (indexing)

#### Current Setup (gpt-4-turbo + ada-002)
```
LLM Costs:
  - Input: 1,000 × 3 × 2,000 = 6M tokens × $10 = $60
  - Output: 1,000 × 3 × 500 = 1.5M tokens × $30 = $45
  - Total LLM: $105/month

Embedding Costs:
  - 1,000 × 1,000 tokens = 1M tokens × $0.10 = $0.10
  - Total Embedding: $0.10/month

Total: ~$105/month
```

#### Recommended Setup (gpt-4o + text-embedding-3-small)
```
LLM Costs:
  - Input: 6M tokens × $5 = $30
  - Output: 1.5M tokens × $15 = $22.50
  - Total LLM: $52.50/month

Embedding Costs:
  - 1M tokens × $0.02 = $0.02
  - Total Embedding: $0.02/month

Total: ~$52.50/month
Savings: ~50% reduction
```

#### Cost-Optimized Setup (gpt-4o-mini + text-embedding-3-small)
```
LLM Costs:
  - Input: 6M tokens × $0.15 = $0.90
  - Output: 1.5M tokens × $0.60 = $0.90
  - Total LLM: $1.80/month

Embedding Costs:
  - 1M tokens × $0.02 = $0.02
  - Total Embedding: $0.02/month

Total: ~$1.82/month
Savings: ~98% reduction
```

### Cost Savings Summary

| Configuration | Monthly Cost | Savings vs Current |
|--------------|--------------|-------------------|
| Current (gpt-4-turbo + ada-002) | $105 | - |
| Recommended (gpt-4o + text-embedding-3-small) | $52.50 | **50%** |
| Cost-Optimized (gpt-4o-mini + text-embedding-3-small) | $1.82 | **98%** |

---

## Token Usage Analysis

### Per-Request Token Breakdown

This section provides detailed token usage analysis for each LLM chain in the recommendation generation flow.

#### PatternAnalysisChain Token Usage

**Input Tokens:**
- System prompt: ~150 tokens
  ```
  "You are an expert at analyzing Databricks workload patterns.
   Analyze the provided job metrics and identify:
   1. Workload type (ETL, JSON Processing, Complex Aggregations, etc.)
   2. Resource utilization patterns
   3. Performance characteristics
   4. Optimization opportunities
   
   Be specific and data-driven in your analysis."
  ```
- Job metrics (aggregated dict): ~200-400 tokens
  ```python
  {
    'avg_duration_seconds': 3680.0,
    'avg_cost_usd': 12.78,
    'avg_cpu_utilization': 46.18,
    'avg_memory_utilization': 63.1,
    'peak_cpu_utilization': 81.5,
    'peak_memory_utilization': 92.3,
    'p95_nodes_consumed': 6.74,
    'p99_nodes_consumed': 8.98,
    'total_runs': 5,
    'current_node_type': 'Standard_E8s_v3',
    'current_min_workers': 1,
    'current_max_workers': 16
  }
  ```
- Human prompt wrapper: ~20 tokens

**Total Input:** ~370-570 tokens

**Output Tokens:**
- Pattern analysis text: ~300-600 tokens
  ```
  "Based on the job metrics provided, this workload shows:
  1. Workload Type: ETL processing with moderate complexity
  2. Resource Utilization: CPU utilization averages 45-48%, Memory utilization 60-65%
  3. Performance Characteristics: Consistent execution times around 3600-3900 seconds
  4. Optimization Opportunities: Current configuration appears well-suited, but could benefit from right-sizing based on actual node consumption patterns."
  ```

**Total per PatternAnalysisChain:** ~670-1170 tokens

---

#### CostOptimizationChain Token Usage

**Input Tokens (Before Pattern Analysis Integration):**
- System prompt: ~150 tokens
- `current_config` (dict): ~50 tokens
  ```python
  {'node_type': 'Standard_E8s_v3', 'min_workers': 1, 'max_workers': 16}
  ```
- `job_metrics` (aggregated dict): ~200-400 tokens
- `budget_constraints` (dict): ~30 tokens
  ```python
  {'monthly_budget': 10000, 'current_spend': 0}
  ```
- Human prompt wrapper: ~30 tokens

**Previous Total Input:** ~460-660 tokens

**Input Tokens (After Pattern Analysis Integration):**
- System prompt: ~150 tokens
- `current_config` (dict): ~50 tokens
- `job_metrics` (aggregated dict): ~200-400 tokens
- `budget_constraints` (dict): ~30 tokens
- `pattern_analysis` (text from PatternAnalysisChain): ~300-600 tokens
- Enhanced human prompt: ~50 tokens
  ```
  "Use the pattern analysis insights to inform your recommendation, especially for:
   - Workload type classification (helps select node family D/E/F)
   - Resource utilization patterns (helps determine worker configuration)
   - Performance characteristics (helps set min/max workers and auto-termination)"
  ```

**New Total Input:** ~780-1280 tokens
**Token Increase:** +320-620 tokens (+50-100% increase)

**Output Tokens:**
- JSON recommendation: ~150-250 tokens
  ```json
  {
    "node_family": "E",
    "vcpus": 4,
    "min_workers": 2,
    "max_workers": 8,
    "auto_termination_minutes": 30,
    "rationale": "Based on utilization patterns showing average 4-5 nodes consumed, recommending E4s_v3 with 2-8 workers for better cost efficiency"
  }
  ```

**Total per CostOptimizationChain:**
- Before: ~610-910 tokens
- After: ~930-1530 tokens
- Increase: +320-620 tokens (+52-68% increase)

---

#### ExplanationChain Token Usage

**Input Tokens:**
- System prompt: ~200 tokens
- `recommendation` (dict): ~200-300 tokens
  ```python
  {
    'node_family': 'E',
    'vcpus': 4,
    'min_workers': 2,
    'max_workers': 8,
    'current_cost': 1210.98,
    'recommended_cost': 630.72,
    'savings_usd': 580.26,
    'savings_pct': 47.92,
    'risk_level': 'HIGH',
    'confidence_score': 0.85
  }
  ```
- `job_metrics` (aggregated dict): ~200-400 tokens
- `pattern_analysis` (text): ~300-600 tokens
- `risk_assessment` (dict): ~100-150 tokens
  ```python
  {
    'risk_level': 'HIGH',
    'risk_score': 0.9,
    'mitigations': ['Monitor initial runs closely', 'Maintain rollback capability', 'Gradual rollout recommended']
  }
  ```
- Human prompt wrapper: ~40 tokens

**Total Input:** ~840-1690 tokens

**Output Tokens:**
- Detailed explanation text: ~400-800 tokens
  ```
  "This recommendation is based on analysis of historical job execution metrics.
   The current cluster configuration shows:
   - Average node consumption: 4-5 nodes
   - Peak utilization: CPU 78-81%, Memory 89-92%
   - The recommended configuration maintains performance while reducing costs
   through better resource alignment..."
  ```

**Total per ExplanationChain:** ~1240-2490 tokens

---

### Complete Request Token Summary

| Chain | Input Tokens | Output Tokens | Total Tokens |
|-------|--------------|---------------|--------------|
| **PatternAnalysisChain** | 370-570 | 300-600 | 670-1170 |
| **CostOptimizationChain** (with pattern_analysis) | 780-1280 | 150-250 | 930-1530 |
| **ExplanationChain** | 840-1690 | 400-800 | 1240-2490 |
| **Total per Request** | 1990-3540 | 850-1650 | **2840-5190** |

### Cost Analysis per Request (gpt-4o pricing)

| Component | Input Cost | Output Cost | Total Cost |
|-----------|-----------|-------------|------------|
| PatternAnalysisChain | $0.010-0.019 | $0.005-0.009 | $0.015-0.028 |
| CostOptimizationChain | $0.004-0.006 | $0.002-0.004 | $0.006-0.010 |
| ExplanationChain | $0.004-0.008 | $0.006-0.012 | $0.010-0.020 |
| **Total per Request** | $0.018-0.033 | $0.013-0.025 | **$0.031-0.058** |

### Impact of Pattern Analysis Integration

**CostOptimizationChain Token Impact:**
- **Before integration:** 460-660 input tokens
- **After integration:** 780-1280 input tokens
- **Increase:** +320-620 tokens (+50-100%)
- **Cost increase:** +$0.002-0.003 per request

**Benefits:**
- ✅ Better workload type classification for node family selection
- ✅ More informed worker configuration based on performance patterns
- ✅ Context-aware recommendations using pre-analyzed insights
- ✅ Reduced cognitive load on CostOptimizationChain LLM

**Trade-offs:**
- ⚠️ Higher token usage (+50-100% for CostOptimizationChain)
- ⚠️ Slight cost increase (~$0.002-0.003 per request)
- ⚠️ Potential for error propagation if PatternAnalysisChain misclassifies

**Recommendation:** The token cost increase is minimal (~$2-3/month per 1,000 requests) and the potential accuracy improvement, especially for workload classification, justifies the additional tokens.

---

## End-to-End Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           API REQUEST ENTRY POINT                            │
│                    POST /api/recommendations/generate                        │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FastAPI Route Handler                               │
│              API/src/routes/recommendations.py:generate_recommendation()     │
│                                                                              │
│  Input: {job_id, start_date, end_date}                                      │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ClusterConfigAgent.generate_recommendation()              │
│              AI/src/agents/cluster_config_agent.py:218                      │
│                                                                              │
│  Creates initial state:                                                     │
│  {job_id, start_date, end_date, job_metrics, resource_utilization, ...}   │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LangGraph Workflow Execution                         │
│                    StateGraph (RecommendationState)                          │
│                                                                              │
│  Entry Point: "collect_data"                                                 │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
        ┌───────────────────────┐   ┌───────────────────────┐
        │   NODE: collect_data  │   │  (Parallel execution)  │
        │  cluster_config_agent │   │                        │
        │      .py:49           │   │                        │
        └───────────┬───────────┘   └────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐
│  Tool:            │  │  Tool:            │  │  Tool:            │
│  get_job_metrics  │  │  get_resource_    │  │  get_cost_        │
│  (databricks_     │  │  utilization      │  │  analysis         │
│   tools.py:23)    │  │  (databricks_     │  │  (databricks_     │
│                   │  │   tools.py:59)    │  │   tools.py:88)    │
└─────────┬─────────┘  └─────────┬─────────┘  └─────────┬─────────┘
          │                      │                      │
          └──────────┬───────────┴──────────┬──────────┘
                     │                       │
                     ▼                       ▼
        ┌────────────────────────────────────────────┐
        │  _get_collector() - Selects collector      │
        │  (databricks_tools.py:12)                  │
        │                                            │
        │  IF use_local_data:                         │
        │    → LocalDataCollector                    │
        │  ELSE:                                      │
        │    → DatabricksCollector                   │
        └────────────┬───────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌──────────────────┐    ┌──────────────────────┐
│ LocalDataCollector│    │ DatabricksCollector  │
│ (local_data_      │    │ (databricks_         │
│  collector.py)    │    │  collector.py)       │
│                   │    │                      │
│ Reads CSV file    │    │ Queries Databricks   │
│ Filters by date   │    │ system tables        │
│ & job_id          │    │ Returns JobMetrics   │
└─────────┬─────────┘    └──────────┬───────────┘
          │                         │
          └────────────┬────────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │  Returns: List[JobMetrics]   │
        │  (Multiple records for job)  │
        └──────────────┬───────────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │  MetricsProcessor            │
        │  aggregate_by_job()          │
        │  (metrics_processor.py:13)   │
        │                              │
        │  Aggregates multiple runs:   │
        │  - Averages (duration, CPU) │
        │  - Peaks (max CPU, memory)   │
        │  - Percentiles (p95, p99)    │
        │  - Count (total_runs)        │
        └──────────────┬───────────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │  State updated with:        │
        │  - job_metrics (aggregated)   │
        │  - resource_utilization      │
        │  - cost_analysis              │
        └──────────────┬───────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    NODE: analyze_patterns                                    │
│              cluster_config_agent.py:74                                      │
│                                                                              │
│  Calls: PatternAnalysisChain.analyze()                                      │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 ▼
        ┌──────────────────────────────────────┐
        │  PatternAnalysisChain                  │
        │  (pattern_analysis_chain.py:10)       │
        │                                        │
        │  Uses: AzureOpenAIService.get_llm()   │
        │  Model: gpt-4-turbo (or gpt-4o)       │
        │                                        │
        │  Prompt: Analyze job metrics for      │
        │  workload patterns, resource usage,   │
        │  performance characteristics           │
        └──────────────┬─────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │  LLM Response (Text)         │
        │  Pattern analysis string     │
        └──────────────┬───────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    NODE: optimize_costs                                      │
│              cluster_config_agent.py:80                                     │
│                                                                              │
│  Calls: CostOptimizationChain.optimize()                                    │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 ▼
        ┌──────────────────────────────────────┐
        │  CostOptimizationChain                │
        │  (cost_optimization_chain.py:11)     │
        │                                        │
        │  Uses: AzureOpenAIService.get_llm()   │
        │  Model: gpt-4-turbo (or gpt-4o)       │
        │                                        │
        │  Input: current_config, job_metrics,  │
        │  budget_constraints,                  │
        │  pattern_analysis (from previous)     │
        │                                        │
        │  Prompt: Generate JSON recommendation │
        │  with node_family, vcpus, workers,    │
        │  min/max workers, auto-termination.   │
        │  Uses pattern_analysis for workload   │
        │  type classification and insights.    │
        └──────────────┬─────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │  LLM Response (JSON)         │
        │  Parsed to dict:              │
        │  {node_family, vcpus,         │
        │   min_workers, max_workers,   │
        │   auto_termination_minutes,   │
        │   rationale}                  │
        └──────────────┬───────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    NODE: validate_performance                                │
│              cluster_config_agent.py:102                                      │
│                                                                              │
│  Calls: validate_performance tool                                            │
│  (validation_tools.py:7)                                                     │
│                                                                              │
│  Validates: Recommended config meets        │
│  performance requirements (80% capacity)    │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 ▼
        ┌──────────────────────────────┐
        │  Returns:                    │
        │  {meets_peak_requirements,   │
        │   current_capacity,           │
        │   recommended_capacity,       │
        │   reduction_pct,              │
        │   risk_level,                │
        │   estimated_impact}           │
        └──────────────┬───────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    NODE: assess_risks                                        │
│              cluster_config_agent.py:127                                     │
│                                                                              │
│  Calls: assess_risks tool                                                   │
│  (validation_tools.py:49)                                                   │
│                                                                              │
│  Calculates: Risk score based on config     │
│  change magnitude, performance validation   │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 ▼
        ┌──────────────────────────────┐
        │  Returns:                    │
        │  {risk_level,                 │
        │   risk_score,                 │
        │   mitigations}                │
        └──────────────┬───────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    NODE: generate_recommendation                             │
│              cluster_config_agent.py:143                                     │
│                                                                              │
│  Calls cost calculation tools:                                              │
│  - calculate_cluster_cost (current)          │
│  - calculate_cluster_cost (recommended)     │
│  - calculate_cost_savings                    │
│  (cost_calculator_tools.py)                  │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
        ┌──────────────────────┐   ┌──────────────────────┐
        │ calculate_cluster_   │   │ calculate_cost_      │
        │ cost tool            │   │ savings tool         │
        │                      │   │                      │
        │ Uses NODE_PRICING    │   │ Calculates:          │
        │ dict to compute      │   │ - savings_usd        │
        │ monthly cost         │   │ - savings_pct        │
        │                      │   │ - annual_savings     │
        └──────────┬───────────┘   └──────────┬───────────┘
                   │                          │
                   └──────────┬───────────────┘
                              │
                              ▼
        ┌──────────────────────────────┐
        │  Final Recommendation Dict:  │
        │  {node_family, vcpus,        │
        │   min_workers, max_workers,  │
        │   current_cost,              │
        │   recommended_cost,          │
        │   savings_usd,               │
        │   savings_pct,               │
        │   risk_level,                │
        │   confidence_score}          │
        └──────────────┬───────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    NODE: generate_explanation                                 │
│              cluster_config_agent.py:182                                     │
│                                                                              │
│  Calls: ExplanationChain.explain()                                          │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 ▼
        ┌──────────────────────────────────────┐
        │  ExplanationChain                    │
        │  (explanation_chain.py:10)          │
        │                                        │
        │  Uses: AzureOpenAIService.get_llm()   │
        │  Model: gpt-4-turbo (or gpt-4o)       │
        │                                        │
        │  Prompt: Generate detailed           │
        │  explanation with rationale,         │
        │  evidence, comparison, impact,       │
        │  risks, alternatives                 │
        └──────────────┬─────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │  LLM Response (Text)         │
        │  Detailed explanation        │
        └──────────────┬───────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LangGraph END                                        │
│                    Final State Complete                                      │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 ▼
        ┌──────────────────────────────┐
        │  Return Final Response:      │
        │  {                            │
        │    recommendation: {...},     │
        │    explanation: "...",        │
        │    pattern_analysis: "...",   │
        │    risk_assessment: {...}     │
        │  }                            │
        └──────────────┬───────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FastAPI Response                                          │
│              RecommendationResponse (Pydantic Model)                        │
│                                                                              │
│  Returns JSON to client                                                     │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                    OPTIONAL: Azure AI Search Indexing                       │
│              (Not part of main flow, but available)                          │
│                                                                              │
│  AzureSearchService.index_recommendation()                                  │
│  - Uses: AzureOpenAIService.get_embeddings()                                │
│  - Model: text-embedding-ada-002 (or text-embedding-3-small)               │
│  - Creates embedding from recommendation text                               │
│  - Stores in Azure AI Search for similarity search                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key Components Summary

| Component | Type | Purpose | Model Used |
|-----------|------|---------|------------|
| **PatternAnalysisChain** | LangChain Chain | Analyze workload patterns | gpt-4-turbo/gpt-4o |
| **CostOptimizationChain** | LangChain Chain | Generate recommendations | gpt-4-turbo/gpt-4o |
| **ExplanationChain** | LangChain Chain | Generate explanations | gpt-4-turbo/gpt-4o |
| **get_job_metrics** | LangChain Tool | Collect job metrics | N/A (data collection) |
| **get_resource_utilization** | LangChain Tool | Collect resource data | N/A (data collection) |
| **get_cost_analysis** | LangChain Tool | Collect cost data | N/A (data collection) |
| **validate_performance** | LangChain Tool | Validate performance | N/A (rule-based) |
| **assess_risks** | LangChain Tool | Assess risks | N/A (rule-based) |
| **calculate_cluster_cost** | LangChain Tool | Calculate costs | N/A (rule-based) |
| **calculate_cost_savings** | LangChain Tool | Calculate savings | N/A (rule-based) |
| **AzureSearchService** | Service | Index/search recommendations | text-embedding-ada-002/text-embedding-3-small |

---

## Migration Steps

### Phase 1: Update Settings (Low Risk)

1. **Update `shared/config/settings.py`**
   ```python
   azure_openai_deployment_name: str = "gpt-4o"  # Changed from "gpt-4-turbo"
   azure_openai_embedding_deployment: str = "text-embedding-3-small"  # Changed from "text-embedding-ada-002"
   ```

2. **Deploy new model deployments in Azure OpenAI**
   - Create `gpt-4o` deployment
   - Create `text-embedding-3-small` deployment
   - Ensure same region and resource group

3. **Test with sample requests**
   - Run test script with new models
   - Verify JSON output quality from CostOptimizationChain
   - Check explanation quality

### Phase 2: Update Temperature (Optional)

Consider lowering temperature for more deterministic outputs:

```python
# In azure_openai_service.py:29
temperature=0.3,  # Changed from 0.7 for more deterministic recommendations
```

### Phase 3: Monitor and Optimize

1. **Monitor costs**
   - Track token usage
   - Compare actual costs vs estimates
   - Adjust if needed

2. **Performance testing**
   - Compare response times
   - Validate recommendation quality
   - Check for any regressions

3. **A/B Testing (Optional)**
   - Run both models in parallel
   - Compare outputs
   - Gradually shift traffic

### Phase 4: Embedding Index Migration (If using text-embedding-3-large)

If migrating to `text-embedding-3-large` (3072 dimensions):

1. **Create new Azure AI Search index**
   - Update embedding field dimension to 3072
   - Re-index all existing recommendations

2. **Update code**
   - No code changes needed (dimension handled by model)

3. **Dual-write period**
   - Write to both indexes during transition
   - Gradually migrate queries

---

## Recommendations

### Immediate Actions

1. ✅ **Migrate to gpt-4o** - Better cost/performance, minimal risk
2. ✅ **Migrate to text-embedding-3-small** - Better performance, same cost, no migration needed
3. ⚠️ **Consider temperature adjustment** - Lower to 0.3-0.5 for more deterministic outputs

### Future Considerations

1. **Cost Optimization**
   - Consider gpt-4o-mini for non-critical chains (e.g., explanations)
   - Use gpt-4o for critical chains (cost optimization)

2. **Performance Optimization**
   - Cache pattern analysis results for similar workloads
   - Batch embedding generation for indexing

3. **Model Updates**
   - Monitor for newer model releases
   - Consider fine-tuning for domain-specific recommendations

---

## Notes

- All model deployments must be created in Azure OpenAI Studio before updating settings
- Ensure API version compatibility (`2024-02-15-preview` supports these models)
- Test thoroughly in development environment before production deployment
- Monitor token usage and costs after migration
- Keep old deployments active during transition period for rollback capability

