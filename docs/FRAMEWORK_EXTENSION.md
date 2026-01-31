# Framework Extension Guide

## Overview

This framework is designed to be easily extended with new agents and use cases. This guide explains how to add new functionality.

## Adding a New Agent

### Step 1: Create Agent Class

Create a new file in `AI/src/agents/`:

```python
# AI/src/agents/new_agent.py
from langgraph.graph import StateGraph, END
from typing import TypedDict, Dict
from shared.utils.logging import get_logger

logger = get_logger(__name__)

class NewAgentState(TypedDict):
    """State for new agent."""
    input_data: Dict
    processed_data: Dict
    result: Dict

class NewAgent:
    """New agent implementation."""
    
    def __init__(self):
        self.graph = self._create_graph()
    
    def _create_graph(self) -> StateGraph:
        workflow = StateGraph(NewAgentState)
        
        # Add nodes
        workflow.add_node("process", self._process_node)
        workflow.add_node("generate", self._generate_node)
        
        # Define edges
        workflow.set_entry_point("process")
        workflow.add_edge("process", "generate")
        workflow.add_edge("generate", END)
        
        return workflow.compile()
    
    async def _process_node(self, state: NewAgentState) -> NewAgentState:
        # Process logic
        return state
    
    async def _generate_node(self, state: NewAgentState) -> NewAgentState:
        # Generation logic
        return state
    
    async def run(self, input_data: Dict) -> Dict:
        """Run the agent."""
        initial_state: NewAgentState = {
            "input_data": input_data,
            "processed_data": {},
            "result": {}
        }
        final_state = await self.graph.ainvoke(initial_state)
        return final_state["result"]
```

### Step 2: Create Tools (if needed)

Create tools in `AI/src/tools/`:

```python
# AI/src/tools/new_tools.py
from langchain.tools import tool

@tool
def new_tool_function(param: str) -> dict:
    """Tool description."""
    # Implementation
    return {}
```

### Step 3: Create Chains (if needed)

Create chains in `AI/src/chains/`:

```python
# AI/src/chains/new_chain.py
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from AI.src.services.azure_openai_service import AzureOpenAIService

class NewChain:
    def __init__(self):
        self.llm = AzureOpenAIService().get_llm()
        # Define prompt and chain
```

### Step 4: Add API Endpoints

Create endpoints in `API/src/routes/`:

```python
# API/src/routes/new_agent.py
from fastapi import APIRouter
from AI.src.agents.new_agent import NewAgent

router = APIRouter()

@router.post("/new-endpoint")
async def new_endpoint(request: dict):
    agent = NewAgent()
    result = await agent.run(request)
    return result
```

### Step 5: Register Routes

Add to `API/src/main.py`:

```python
from API.src.routes import new_agent

app.include_router(new_agent.router, prefix="/api/new-agent", tags=["new-agent"])
```

## Adding a New Use Case

### Example: Adding a Performance Optimization Agent

1. **Create agent**: `AI/src/agents/performance_agent.py`
2. **Create tools**: `AI/src/tools/performance_tools.py`
3. **Create chains**: `AI/src/chains/performance_chain.py`
4. **Add API routes**: `API/src/routes/performance.py`
5. **Add tests**: `AI/tests/test_performance_agent.py`

## Framework Patterns

### State Management

All agents use TypedDict for state:

```python
class AgentState(TypedDict):
    field1: str
    field2: Dict
```

### Logging

Use structured logging:

```python
from shared.utils.logging import get_logger

logger = get_logger(__name__)
logger.info("event_name", key=value)
```

### Error Handling

Wrap operations in try-except:

```python
try:
    result = operation()
except Exception as e:
    logger.error("operation_error", error=str(e))
    raise
```

## Best Practices

1. **Modularity**: Keep components focused and independent
2. **Reusability**: Use shared modules where possible
3. **Testing**: Write tests for all new functionality
4. **Documentation**: Document new agents and use cases
5. **Type Hints**: Use type hints throughout
6. **Error Handling**: Handle errors gracefully

## Example: Complete New Agent

See `AI/src/agents/cluster_config_agent.py` for a complete example of:
- LangGraph workflow
- Multiple chains
- Tool integration
- State management
- Error handling

