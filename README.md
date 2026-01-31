# Databricks Recommendation Agent Framework

A modular, extensible framework for building AI-powered recommendation agents for Databricks cluster configurations and other use cases.

## Architecture

```
databricks_recommendation_agent/
├── DE/              # Data Engineering - Data collection and processing
├── AI/               # AI Agents - LangChain/LangGraph agents
├── ML_DS/            # Machine Learning / Data Science - Models and analysis
├── API/              # REST API - FastAPI backend
└── UI/               # User Interface - Frontend (Phase 2)
```

## Current Implementation Status

✅ **DE (Data Engineering)**: Data collection from Databricks system tables  
✅ **API**: FastAPI REST endpoints  
✅ **AI Agent**: Cluster configuration recommendation agent using Azure AI Foundry, LangChain, and LangGraph  
⏳ **ML/DS**: Coming in Phase 2  
⏳ **UI**: Coming in Phase 2  

## Features

- **Modular Framework**: Easy to add new agents and use cases
- **Azure AI Foundry Integration**: OpenAI, AI Search, Prompt Flow
- **LangChain & LangGraph**: Multi-step agent workflows
- **Vector Store**: Semantic search over recommendations
- **Test-Driven**: Comprehensive test coverage
- **Extensible**: Framework supports multiple agent types

## Quick Start

### Prerequisites

- Python 3.11+
- Azure subscription with AI Foundry access
- Databricks workspace access

### Setup

```bash
# Clone and navigate
cd /Users/sabbineni/projects/databricks_recommendation_agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Azure and Databricks credentials

# Run tests
pytest

# Start API server
cd API
uvicorn main:app --reload
```

## Project Structure

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architecture documentation.

## Development Guide

See [DEVELOPMENT.md](docs/DEVELOPMENT.md) for development guidelines.

## License

MIT

