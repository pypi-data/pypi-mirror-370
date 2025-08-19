"""
Basic tests for Multimind SDK.
"""

import pytest
from typing import AsyncGenerator, Coroutine, Any, Optional, List, Dict, Union, cast
from multimind import (
    BaseLLM, ModelRouter, Config,
    Agent, AgentMemory, CalculatorTool,
    PromptChain, TaskRunner,
    MCPParser, MCPExecutor,
    TraceLogger, UsageTracker
)
from asyncio import sleep

def test_imports():
    """Test that all major components can be imported."""
    # Core components
    assert BaseLLM is not None
    assert ModelRouter is not None
    assert Config is not None

    # Agent components
    assert Agent is not None
    assert AgentMemory is not None
    assert CalculatorTool is not None

    # Orchestration components
    assert PromptChain is not None
    assert TaskRunner is not None

    # MCP components
    assert MCPParser is not None
    assert MCPExecutor is not None

    # Logging components
    assert TraceLogger is not None
    assert UsageTracker is not None

def test_agent_creation():
    """Test basic agent creation."""
    # Create a mock model
    class MockModel(BaseLLM):
        def __init__(self, model_name: str = "mock-model"):
            self.model_name = model_name

        async def generate(self, prompt: str, temperature: float = 0.7, max_tokens: Optional[int] = None, **kwargs) -> str:
            return "Mock response"

        async def generate_stream(self, prompt: str, temperature: float = 0.7, max_tokens: Optional[int] = None, **kwargs) -> AsyncGenerator[str, None]:
            async def stream() -> AsyncGenerator[str, None]:
                yield "Mock response"
            return stream()

        async def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: Optional[int] = None, **kwargs) -> str:
            return "Mock chat response"

        async def chat_stream(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: Optional[int] = None, **kwargs) -> AsyncGenerator[str, None]:
            async def stream() -> AsyncGenerator[str, None]:
                yield "Mock chat response"
            return stream()

        async def embeddings(self, text: Union[str, List[str]], **kwargs) -> Union[List[float], List[List[float]]]:
            if isinstance(text, str):
                return [0.0] * 768
            return [[0.0] * 768 for _ in text]

    # Instantiate MockModel with required parameter
    model = MockModel(model_name="mock-model")
    memory = AgentMemory()
    calculator = CalculatorTool()

    # Create agen
    agent = Agent(
        model=model,
        memory=memory,
        tools=[calculator],
        system_prompt="You are a helpful assistant."
    )

    assert agent.model == model
    assert agent.memory == memory
    assert len(agent.tools) == 1
    assert agent.system_prompt == "You are a helpful assistant."

def test_prompt_chain():
    """Test basic prompt chain creation."""
    # Create a mock model
    class MockModel(BaseLLM):
        async def generate(self, prompt: str, temperature: float = 0.7, max_tokens: Optional[int] = None, **kwargs) -> str:
            return "Mock response"

        async def generate_stream(self, prompt: str, temperature: float = 0.7, max_tokens: Optional[int] = None, **kwargs) -> AsyncGenerator[str, None]:
            yield "Mock response"

        async def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: Optional[int] = None, **kwargs) -> str:
            return "Mock chat response"

        async def chat_stream(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: Optional[int] = None, **kwargs) -> AsyncGenerator[str, None]:
            async def stream() -> AsyncGenerator[str, None]:
                yield "Mock chat response"
            return stream()

        async def embeddings(self, text: Union[str, List[str]], **kwargs) -> Union[List[float], List[List[float]]]:
            if isinstance(text, str):
                return [0.0] * 768
            return [[0.0] * 768 for _ in text]

    # Create prompt chain
    model = MockModel(model_name="mock-model")
    chain = PromptChain(model)

    # Add prompts
    chain.add_prompt("First prompt: {input}")
    chain.add_prompt("Second prompt: {last_response}")

    # Set variables
    chain.set_variable("input", "test input")

    # Run chain
    import asyncio
    results = asyncio.run(chain.run())

    assert len(results) == 2
    assert results[0]["prompt"] == "First prompt: test input"
    assert results[1]["prompt"] == "Second prompt: Mock response"

def test_mcp_parser():
    """Test MCP parser with basic spec."""
    parser = MCPParser()

    # Create a basic spec
    spec = {
        "version": "1.0.0",
        "models": [
            {
                "name": "test-model",
                "type": "openai",
                "config": {
                    "model": "gpt-3.5-turbo",
                    "temperature": 0.7
                }
            }
        ],
        "workflow": {
            "steps": [
                {
                    "id": "step1",
                    "type": "model",
                    "config": {
                        "model": "test-model",
                        "prompt_template": "Test prompt"
                    }
                }
            ],
            "connections": []
        }
    }

    # Parse spec
    parsed = parser.parse(spec)
    assert parsed == spec

def test_usage_tracker():
    """Test basic usage tracking."""
    tracker = UsageTracker(":memory:")  # Use in-memory database for testing

    # Set model costs
    tracker.set_model_costs(
        model="test-model",
        input_cost_per_token=0.001,
        output_cost_per_token=0.002
    )

    # Track usage
    tracker.track_usage(
        model="test-model",
        operation="test",
        input_tokens=100,
        output_tokens=50
    )

    # Get summary
    summary = tracker.get_usage_summary()
    assert summary["total_cost"] == 0.2  # 100 * 0.001 + 50 * 0.002
    assert "test-model" in summary["models"]
    assert summary["models"]["test-model"]["total_cost"] == 0.2