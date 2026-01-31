# Architecture Documentation

## Overview

The Databricks Recommendation Agent Framework is a modular, extensible system for building AI-powered recommendation agents.

## Directory Structure

```
databricks_recommendation_agent/
├── DE/                  # Data Engineering
│   ├── src/
│   │   ├── collectors/  # Data collection from Databricks
│   │   └── processors/  # Data processing and aggregation
│   └── tests/
│
├── AI/                  # AI Agents
│   ├── src/
│   │   ├── agents/      # LangGraph agents
│   │   ├── chains/      # LangChain chains
│   │   ├── services/    # Azure AI services
│   │   └── tools/       # LangChain tools
│   └── tests/
│
├── ML_DS/               # Machine Learning / Data Science (Phase 2)
│   ├── src/
│   └── tests/
│
├── API/                 # REST API
│   ├── src/
│   │   ├── routes/      # API endpoints
│   │   └── main.py      # FastAPI application
│   └── tests/
│
├── UI/                  # User Interface (Phase 2)
│   ├── src/
│   └── tests/
│
└── shared/              # Shared code
    ├── config/          # Configuration
    ├── models/          # Data models
    └── utils/           # Utilities
```

## Component Architecture

### Data Engineering (DE)

**Purpose**: Collect and process data from Databricks system tables.

**Components**:
- `DatabricksCollector`: Collects metrics from system tables
- `MetricsProcessor`: Aggregates and processes metrics

### AI Agents

**Purpose**: Generate recommendations using LangChain and LangGraph.

**Components**:
- `ClusterConfigAgent`: Main recommendation agent
- `PatternAnalysisChain`: Analyzes workload patterns
- `CostOptimizationChain`: Optimizes costs
- `ExplanationChain`: Generates explanations
- `AzureOpenAIService`: LLM and embeddings
- `AzureSearchService`: Vector search

### API

**Purpose**: REST API for accessing recommendations.

**Components**:
- FastAPI application
- Recommendation endpoints
- Health check endpoints

## Data Flow

```
1. DE collects data from Databricks
   ↓
2. Data is processed and aggregated
   ↓
3. AI Agent receives job metrics
   ↓
4. LangGraph workflow executes:
   - Collect data
   - Analyze patterns
   - Optimize costs
   - Validate performance
   - Assess risks
   - Generate recommendation
   - Generate explanation
   ↓
5. Recommendation returned via API
```

## Extensibility

### Adding New Agents

1. Create new agent class in `AI/src/agents/`
2. Define LangGraph workflow
3. Create necessary chains and tools
4. Add API endpoints in `API/src/routes/`

### Adding New Use Cases

1. Create new directory structure (e.g., `AI/src/agents/new_use_case/`)
2. Follow existing patterns
3. Extend shared models if needed
4. Add tests

## Technology Stack

- **LangChain**: LLM orchestration
- **LangGraph**: Multi-step agent workflows
- **Azure OpenAI**: LLM and embeddings
- **Azure AI Search**: Vector store
- **FastAPI**: REST API
- **Databricks SQL**: Data collection

