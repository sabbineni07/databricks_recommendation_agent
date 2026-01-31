# Development Guide

## Setup

1. **Clone and navigate to project**
   ```bash
   cd /Users/sabbineni/projects/databricks_recommendation_agent
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

## Running Tests

```bash
# Run all tests
pytest

# Run specific module
pytest DE/tests/
pytest AI/tests/
pytest API/tests/

# Run with coverage
pytest --cov=DE/src --cov=AI/src --cov=API/src
```

## Running the API

```bash
cd API
uvicorn src.main:app --reload
```

API will be available at `http://localhost:8000`

## Development Workflow

1. **Make changes** in respective modules (DE, AI, API)
2. **Write tests** for new functionality
3. **Run tests** to verify
4. **Update documentation** as needed

## Code Style

- Follow PEP 8
- Use type hints
- Document functions and classes
- Keep functions focused and small

## Adding New Features

1. Create feature branch
2. Implement feature with tests
3. Update documentation
4. Submit for review

