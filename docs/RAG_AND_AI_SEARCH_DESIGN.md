# RAG and Azure AI Search Design

## Overview

This document outlines the design for integrating Retrieval Augmented Generation (RAG) with Azure AI Search to enhance recommendation quality by leveraging historical job metrics and recommendations.

## Problem Statement

### Current State
- LLM makes recommendations based only on current job metrics
- No learning from historical patterns or successful recommendations
- No context about what worked for similar jobs in the past
- Cold start problem: no recommendations exist yet

### Goals
- Leverage historical job metrics for pattern matching
- Learn from successful recommendations over time
- Improve recommendation accuracy through RAG
- Handle new use cases and suboptimal current configurations

## Key Design Decisions

### 1. Two-Phase Indexing Strategy

#### Phase 1: Index Raw Job Metrics (Immediate)
**Purpose**: Pattern matching and workload similarity search

**What to Index**:
- Utilization patterns (CPU, memory, node consumption)
- Workload characteristics (type, duration, task count)
- Performance metrics (duration, parallelism)

**What NOT to Index as Recommendations**:
- Current configurations (may be suboptimal)
- Treat as "what was used" not "what should be used"

**Metadata**:
```python
{
    "is_recommendation": False,
    "config_quality": "unknown",
    "document_type": "job_metrics"
}
```

#### Phase 2: Index Recommendations (As Generated)
**Purpose**: Learn from optimized recommendations

**What to Index**:
- Recommendation rationale and explanation
- Recommended configuration
- Pattern analysis that led to recommendation
- Outcomes (when available): actual savings, performance impact

**Metadata**:
```python
{
    "is_recommendation": True,
    "config_quality": "pending",  # Initially pending, updated after validation
    "document_type": "recommendation"
}
```

**Quality States**:
- `"pending"`: Just generated, not yet validated in production
- `"optimal"`: Validated in production, worked as expected
- `"suboptimal"`: Validated but didn't meet expectations
- `"failed"`: Caused issues in production

### 2. Safe RAG Usage Pattern

**Critical Principle**: Use RAG for pattern matching, not direct copying

**Safe Approach**:
1. Search for similar **workload patterns** (not configurations)
2. Extract **utilization patterns** from similar jobs
3. LLM **analyzes and optimizes** based on patterns
4. LLM does **NOT copy** historical configurations

**Unsafe Approach** (Avoid):
- Directly copying historical configurations
- Treating historical configs as recommendations
- Using suboptimal configs as examples

### 3. Enhanced LLM Prompts

**Key Instructions in Prompts**:
- "These are utilization patterns, not recommendations"
- "Historical configurations may be suboptimal"
- "Optimize based on actual needs, not copy historical configs"
- "Consider cost optimization opportunities"

## Architecture

### Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Historical Data                           │
├─────────────────────────────────────────────────────────────┤
│  Raw Job Metrics (CSV/Databricks)                            │
│  - Utilization patterns                                     │
│  - Workload characteristics                                 │
│  - Current configs (for reference only)                    │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              Azure AI Search Index                          │
├─────────────────────────────────────────────────────────────┤
│  Index 1: Job Metrics                                       │
│  - Embeddings from utilization patterns                     │
│  - Metadata: is_recommendation=False                        │
│                                                              │
│  Index 2: Recommendations (as generated)                   │
│  - Embeddings from rationale + explanation                  │
│  - Metadata: is_recommendation=True                         │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              RAG-Enhanced LLM Chains                         │
├─────────────────────────────────────────────────────────────┤
│  Step 2: Pattern Analysis                                   │
│  ├─ Search similar workload patterns                        │
│  ├─ Extract utilization metrics                             │
│  └─ LLM analyzes patterns (not configs)                     │
│                                                              │
│  Step 3: Cost Optimization                                  │
│  ├─ Search similar successful recommendations               │
│  ├─ Extract proven patterns                                 │
│  └─ LLM optimizes based on patterns + recommendations       │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              New Recommendation                             │
├─────────────────────────────────────────────────────────────┤
│  - Generated with RAG context                               │
│  - Indexed for future RAG queries                           │
│  - Linked to job metrics                                    │
└─────────────────────────────────────────────────────────────┘
```

## Implementation Details

### 1. AzureSearchService Enhancements

#### New Method: `index_job_metrics()`
```python
def index_job_metrics(self, metrics: JobMetrics) -> bool:
    """Index raw job metrics for pattern matching.
    
    Indexes utilization patterns and workload characteristics.
    Does NOT treat current config as recommendation.
    """
```

**Indexed Content**:
- Utilization patterns (CPU, memory, nodes)
- Workload type and characteristics
- Performance metrics
- Current config (marked as reference only)

#### Enhanced Method: `search_similar_jobs()`
```python
def search_similar_jobs(
    self, 
    job_metrics: dict, 
    top_k: int = 5,
    filter_recommendations: bool = False
) -> List[Dict]:
    """Search for similar jobs based on utilization patterns.
    
    Args:
        job_metrics: Current job metrics
        top_k: Number of results
        filter_recommendations: If True, only return jobs with recommendations
    """
```

### 2. Enhanced Pattern Analysis Chain

**Before RAG**:
```python
Input: Current job metrics
Output: Pattern analysis
```

**With RAG**:
```python
Input: Current job metrics
  ↓
Search: Similar workload patterns
  ↓
Retrieve: Top 5 similar jobs (utilization patterns only)
  ↓
LLM Input: Current metrics + similar patterns
  ↓
LLM Instructions: "Analyze patterns, not copy configs"
  ↓
Output: Enhanced pattern analysis with historical context
```

### 3. Enhanced Cost Optimization Chain

**Before RAG**:
```python
Input: Pattern analysis + job metrics
Output: Recommendation
```

**With RAG**:
```python
Input: Pattern analysis + job metrics
  ↓
Search: Similar successful recommendations (if available)
  ↓
Search: Similar job patterns (for context)
  ↓
LLM Input: 
  - Current metrics
  - Pattern analysis
  - Similar workload patterns (for context)
  - Similar successful recommendations (if available)
  ↓
LLM Instructions: 
  - "Optimize based on utilization patterns"
  - "Historical configs are reference only"
  - "Consider proven recommendations"
  ↓
Output: Optimized recommendation
```

### 4. Automatic Indexing

#### After Recommendation Generation
```python
# In cluster_config_agent.py after generate_recommendation()

# 1. Index recommendation
search_service.index_recommendation(recommendation_doc)

# 2. Link recommendation to job metrics (optional)
search_service.link_recommendation_to_job(
    recommendation_id=request_id,
    job_id=job_id
)
```

#### Batch Indexing Script
```python
# scripts/index_historical_metrics.py
# Index all historical job metrics from CSV/database
```

## Safety Mechanisms

### 1. Metadata Filtering

```python
# Only use high-quality examples
if filter_quality:
    results = [r for r in results 
               if r.get('config_quality') == 'optimal' 
               or r.get('is_recommendation') == True]
```

### 2. Prompt Engineering

**Critical Instructions**:
- "Historical configurations may be suboptimal"
- "Optimize based on utilization patterns, not copy configs"
- "These are patterns for analysis, not recommendations to copy"

### 3. Two-Tier Search

1. **Pattern Search**: Find similar utilization patterns
2. **Recommendation Search**: Find similar successful recommendations (higher priority)

### 4. Quality Indicators and Updates

**Initial State**: Recommendations are indexed with `config_quality: "pending"`

**Update Mechanism**: After production validation, quality is updated using Azure AI Search's `merge` action:
- `"optimal"`: Recommendation worked well in production
- `"suboptimal"`: Recommendation didn't meet expectations
- `"failed"`: Recommendation caused issues

**Filtering**: RAG searches default to only using `config_quality: "optimal"` recommendations to avoid learning from bad examples.

**Update Method**:
```python
update_recommendation_quality(
    recommendation_id: str,
    config_quality: str,  # "optimal", "suboptimal", or "failed"
    feedback_data: Optional[dict] = None
)
```

This uses Azure AI Search's `merge` action to update only the quality field without regenerating embeddings.

## Benefits

### Immediate Benefits (Raw Metrics Indexing)
- ✅ Pattern matching for similar workloads
- ✅ Workload type classification
- ✅ Utilization pattern analysis
- ✅ Works without existing recommendations

### Long-term Benefits (Recommendation Indexing)
- ✅ Learn from successful recommendations
- ✅ Avoid patterns that failed
- ✅ Higher confidence from proven cases
- ✅ Continuous improvement

### Combined Benefits
- ✅ Better workload classification
- ✅ More accurate recommendations
- ✅ Lower risk (validated patterns)
- ✅ Handles new use cases
- ✅ Addresses suboptimal current configs

## Implementation Checklist

### Phase 1: Infrastructure
- [x] AzureSearchService exists
- [x] Add `index_job_metrics()` method
- [x] Add `search_similar_jobs()` method
- [x] Add `link_recommendation_to_job()` method
- [x] Add `update_recommendation_quality()` method
- [ ] Update index schema for job metrics (requires Azure portal setup)

### Phase 2: Enhanced Chains
- [x] Update PatternAnalysisChain to use RAG
- [x] Update CostOptimizationChain to use RAG
- [x] Add safe prompt instructions
- [x] Add quality filtering in searches
- [ ] Test with mock data

### Phase 3: Integration
- [x] Add indexing after recommendation generation
- [x] Create batch indexing script
- [x] Add error handling and fallbacks
- [x] Initial quality set to "pending"
- [ ] Test end-to-end flow

### Phase 4: Quality Management
- [x] Add quality indicators (pending/optimal/suboptimal/failed)
- [x] Implement update_recommendation_quality() method
- [x] Implement filtering by quality in search methods
- [ ] Add feedback loop (collect production validation results)
- [ ] Add API endpoint for quality updates
- [ ] Monitor and improve

## Usage Examples

### Indexing Job Metrics
```python
from AI.src.services.azure_search_service import AzureSearchService
from shared.models.job_metrics import JobMetrics

search_service = AzureSearchService()

# Index a job metric
metrics = JobMetrics(...)
search_service.index_job_metrics(metrics)
```

### Using RAG in Pattern Analysis
```python
# Automatically happens in PatternAnalysisChain
# Searches for similar jobs and includes context
pattern_analysis = pattern_chain.analyze(job_metrics)
```

### Using RAG in Cost Optimization
```python
# Automatically happens in CostOptimizationChain
# Searches for similar recommendations and patterns
# Only uses optimal recommendations by default
recommendation = cost_chain.optimize(
    current_config, 
    job_metrics, 
    budget_constraints,
    pattern_analysis
)
```

### Updating Recommendation Quality
```python
from AI.src.services.azure_search_service import AzureSearchService

search_service = AzureSearchService()

# After production validation, update quality
search_service.update_recommendation_quality(
    recommendation_id="rec-123",
    config_quality="optimal",  # or "suboptimal" or "failed"
    feedback_data={
        "actual_savings_usd": 150.50,
        "expected_savings_usd": 200.00,
        "performance_impact": "positive",
        "validated_at": "2024-01-20T10:00:00Z"
    }
)
```

## Quality Update Workflow

### Initial Indexing
1. Recommendation generated → Indexed with `config_quality: "pending"`
2. Recommendation is available for RAG but marked as unvalidated

### Production Validation
1. Recommendation is implemented in production
2. Actual performance metrics are collected
3. Compare expected vs actual:
   - Cost savings realized?
   - Performance maintained/improved?
   - Any issues encountered?

### Quality Update
1. Call `update_recommendation_quality()` with validation results
2. Azure AI Search updates only the `config_quality` field (using `merge` action)
3. Optionally add feedback data (actual savings, performance impact, etc.)
4. Embedding is NOT regenerated (content unchanged)

### RAG Filtering
- Default: Only use `config_quality: "optimal"` recommendations
- Experimental: Can include `"pending"` for new patterns
- Avoid: Never use `"suboptimal"` or `"failed"` in RAG

### Example Update Flow
```python
# 1. Initial indexing (automatic after generation)
search_service.index_recommendation({
    "recommendation_id": "rec-123",
    "config_quality": "pending",  # Initial state
    ...
})

# 2. After production validation (manual or automated)
search_service.update_recommendation_quality(
    recommendation_id="rec-123",
    config_quality="optimal",  # or "suboptimal" or "failed"
    feedback_data={
        "actual_savings_usd": 150.50,
        "expected_savings_usd": 200.00,
        "performance_impact": "positive",
        "validated_at": "2024-01-20T10:00:00Z",
        "validated_by": "production_monitoring"
    }
)

# 3. RAG searches automatically filter by quality
similar_recs = search_service.search_similar(
    query="...",
    filter_quality=True  # Only returns optimal recommendations
)
```

## Azure AI Search Update Capabilities

### Document Updates
Azure AI Search supports updating existing documents using indexing actions:

1. **`upload`** (default): Replaces entire document if ID matches
2. **`merge`**: Updates only specified fields (partial update)
3. **`mergeOrUpload`**: Merges if exists, uploads if doesn't exist
4. **`delete`**: Removes document

### Quality Updates Use `merge` Action
- Efficient: Only updates `config_quality` field
- No embedding regeneration needed (content unchanged)
- Document ID must match original recommendation ID
- Can add feedback metadata without changing searchable content

## Future Enhancements

1. **Automated Feedback Collection**: Integrate with production monitoring to automatically update quality
2. **Quality Scoring**: Automatically score config quality based on utilization vs capacity
3. **A/B Testing**: Compare recommendations with/without RAG
4. **Multi-Index Strategy**: Separate indexes for different workload types
5. **Hybrid Search**: Combine vector search with keyword filtering
6. **Quality Analytics**: Track quality trends over time
7. **Automatic Cleanup**: Archive or remove failed recommendations after analysis period

## Risks and Mitigations

### Risk 1: Learning from Bad Examples
**Mitigation**: 
- Clear metadata marking configs as "reference only"
- Enhanced prompts emphasizing optimization
- Prioritize recommendations over raw configs
- **Quality-based filtering**: Only use `config_quality: "optimal"` in RAG searches
- **Initial pending state**: New recommendations start as "pending" until validated
- **Update mechanism**: Quality can be updated after production validation

### Risk 2: Over-reliance on Historical Data
**Mitigation**:
- LLM still does primary reasoning
- RAG provides context, not answers
- Validation and risk assessment steps remain

### Risk 3: Cold Start Problem
**Mitigation**:
- Start with raw metrics indexing
- System works without recommendations
- Gradually improve as recommendations accumulate

## Conclusion

This design enables safe and effective use of RAG by:
1. Indexing raw metrics for pattern matching (not copying)
2. Indexing recommendations with initial "pending" quality state
3. Using enhanced prompts to ensure optimization, not copying
4. Updating quality after production validation
5. Filtering RAG searches to only use proven ("optimal") recommendations

The system will improve continuously as more recommendations are generated, validated, and their quality is updated based on production feedback. This prevents bad recommendations from polluting the knowledge base while allowing the system to learn from successful patterns.

