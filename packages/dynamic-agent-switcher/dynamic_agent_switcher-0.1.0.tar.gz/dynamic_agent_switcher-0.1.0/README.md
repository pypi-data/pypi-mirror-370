# Dynamic Agent Switcher

A Python package that allows you to dynamically switch between different AI models during agent execution. Perfect for handling rate limits, distributing API calls, and implementing custom switching logic.

## Features

- **Flexible Switching Conditions**: Switch models based on rate limits, tool call counts, response content, time limits, error counts, or custom functions
- **Multiple AI Providers**: Support for OpenAI, Gemini, Groq, and other providers
- **Easy Integration**: Drop-in replacement for existing `pydantic_ai.Agent` instances
- **Configurable Strategies**: Round-robin, rate-limit-based, random, weighted, or fallback selection
- **Real-time Context Tracking**: Monitor execution context and make informed switching decisions
- **Extensible**: Create custom switching conditions for your specific needs

## Installation

```bash
pip install dynamic_agent_switcher
```

## Quick Start

### Basic Usage

```python
from dynamic_agent_switcher import (
    DynamicAgentWrapper, 
    ModelConfig, 
    SwitchStrategy,
    ConditionType
)

# Define your models
model_configs = [
    ModelConfig(
        name="openai_gpt4",
        provider="openai",
        model_name="gpt-4",
        api_key="your-openai-key",
        max_requests_per_minute=50
    ),
    ModelConfig(
        name="gemini_pro",
        provider="gemini",
        model_name="gemini-1.5-pro", 
        api_key="your-gemini-key",
        max_requests_per_minute=60
    )
]

# Create dynamic agent
agent = DynamicAgentWrapper(
    model_configs=model_configs,
    system_prompt="You are a helpful AI assistant.",
    strategy=SwitchStrategy.RATE_LIMIT_BASED
)

# Use like a regular agent
result = await agent.run("Generate a story about a robot.")
```

### Custom Switching Conditions

```python
# Switch after 3 tool calls
tool_call_condition = {
    "type": ConditionType.TOOL_CALL_COUNT.value,
    "name": "tool_call_limit",
    "parameters": {"max_calls": 3}
}

# Switch when the count_words tool reports > 500 words (preferred)
tool_word_count_condition = {
    "type": ConditionType.TOOL_RESPONSE.value,
    "name": "word_limit_via_tool",
    "parameters": {
        "tool_name": "count_words",             # optional: apply only to this tool
        "logic": "ANY",                         # ANY | ALL | NONE
        "response_conditions": [
            {"type": "greater_than", "path": "word_count", "value": 500}
        ]
    }
}

# Note: If you want to measure raw model output length instead of tool output,
# you can still use AI_RESPONSE_CONTENT. However, for generic, reusable logic,
# prefer TOOL_RESPONSE so it works with your explicit tool outputs.

# Switch after 2 minutes
time_condition = {
    "type": ConditionType.TIME_BASED.value,
    "name": "time_limit",
    "parameters": {"max_duration_seconds": 120}
}

agent = DynamicAgentWrapper(
    model_configs=model_configs,
    conditions=[tool_call_condition, tool_word_count_condition, time_condition]
)
```

### Tool Response Based Switching

```python
# Switch when a specific tool returns certain values
tool_response_condition = {
    "type": ConditionType.TOOL_RESPONSE.value,
    "name": "validation_failed",
    "parameters": {
        "tool_name": "validate_html",
        "response_conditions": [
            {"type": "contains", "value": "invalid"},
            {"type": "equals", "value": False}
        ]
    }
}
```

### Custom Function Conditions

```python
def custom_switch_logic(context):
    """Custom logic to determine when to switch models."""
    error_count = context.get("error_count", 0)
    current_model = context.get("current_model")
    
    # Switch if we've had 2 errors with the same model
    if error_count >= 2:
        return True
    
    # Switch if current model is OpenAI and it's peak hours
    if current_model == "openai_gpt4" and is_peak_hours():
        return True
    
    return False

custom_condition = {
    "type": ConditionType.CUSTOM_FUNCTION.value,
    "name": "custom_logic",
    "parameters": {
        "function": custom_switch_logic,
        "reason": "Custom business logic"
    }
}
```

### Combination Conditions

```python
# Switch if ANY of these conditions are met
combination_condition = {
    "type": ConditionType.COMBINATION.value,
    "name": "complex_logic",
    "operator": "OR",  # AND, OR, XOR
    "parameters": {
        "conditions": [
            {
                "type": ConditionType.RATE_LIMIT.value,
                "name": "rate_limit"
            },
            {
                "type": ConditionType.TOOL_CALL_COUNT.value,
                "name": "too_many_tools",
                "parameters": {"max_calls": 10}
            },
            {
                "type": ConditionType.TIME_BASED.value,
                "name": "timeout",
                "parameters": {"max_duration_seconds": 600}
            }
        ]
    }
}
```

## Integration with Existing Code

### Replace Existing Agents

```python
from dynamic_agent_switcher import replace_agent_with_dynamic

# Your existing agent
original_agent = Agent(
    openai_model,
    system_prompt="...",
    tools=[count_words, validate_html]
)

# Replace with dynamic version
dynamic_agent = replace_agent_with_dynamic(
    original_agent=original_agent,
    model_configs=model_configs,
    conditions=conditions
)

# Use exactly the same way
result = await dynamic_agent.run(prompt)
```

### Update Your Chapter Service

```python
# In your chapter_service.py
from dynamic_agent_switcher import DynamicAgentWrapper, ModelConfig

# Replace your existing agent definitions
full_chapter_generator = DynamicAgentWrapper(
    model_configs=[
        ModelConfig("openai_gpt4", "openai", "gpt-4", OPENAI_API_KEY),
        ModelConfig("gemini_pro", "gemini", "gemini-1.5-pro", GEMINI_API_KEY),
        ModelConfig("groq_llama3", "groq", "llama3-70b-8192", GROQ_API_KEY)
    ],
    system_prompt="You are an AI assistant for an advanced micro-learning platform...",
    output_type=FullChapter,
    tools=[Tool(count_words), Tool(validate_html)],
    conditions=[
        {
            "type": "rate_limit",
            "name": "rate_limit_detection"
        },
        {
            "type": "tool_call_count", 
            "name": "tool_call_limit",
            "parameters": {"max_calls": 5}
        },
        {
            "type": "ai_response_content",
            "name": "word_count_limit", 
            "parameters": {
                "content_conditions": [
                    {"type": "word_count_greater_than", "value": 800}
                ]
            }
        }
    ]
)

# Use exactly the same way as before
async def generate_full_chapter_node(state: AgentState) -> Dict[str, Any]:
    # ... your existing code ...
    result = await full_chapter_generator.run(prompt)
    # ... rest of your code ...
```

## Available Condition Types

| Condition Type | Description | Parameters |
|---------------|-------------|------------|
| `RATE_LIMIT` | Switch when rate limit errors occur | None |
| `TOOL_CALL_COUNT` | Switch after N tool calls | `max_calls: int` |
| `TOOL_RESPONSE` | Switch based on tool response | `tool_name: str`, `response_conditions: List` |
| `AI_RESPONSE_STATUS` | Switch based on AI response status | `status_codes: List`, `error_patterns: List` |
| `AI_RESPONSE_CONTENT` | Switch based on response content | `content_conditions: List` |
| `TIME_BASED` | Switch after time limit | `max_duration_seconds: int` |
| `ERROR_COUNT` | Switch after N errors | `max_errors: int` |
| `CUSTOM_FUNCTION` | Switch based on custom function | `function: Callable`, `reason: str` |
| `COMBINATION` | Combine multiple conditions | `conditions: List`, `operator: str` |

## Content Conditions

For `AI_RESPONSE_CONTENT` and `TOOL_RESPONSE` conditions, you can use:

- `contains`: Check if response contains text
- `equals`: Check if response equals value
- `regex`: Check if response matches regex pattern
- `greater_than`: Check if numeric value is greater
- `less_than`: Check if numeric value is less
- `length_greater_than`: Check if string length is greater
- `length_less_than`: Check if string length is less
- `word_count_greater_than`: Check if word count is greater
- `word_count_less_than`: Check if word count is less

## Monitoring and Debugging

```python
# Get current status
status = agent.get_status()
print(f"Current model: {status['current_model']}")
print(f"Available models: {status['available_models']}")
print(f"Active conditions: {status['conditions']}")
print(f"Execution context: {status['execution_context']}")

# Update context manually
agent.update_context(
    tool_call_count=5,
    last_tool_response={"word_count": 750}
)

# Reset context
agent.reset_context()

# Add/remove conditions dynamically
agent.add_condition(new_condition)
agent.remove_condition("condition_name")
```

## Advanced Usage

### Custom Model Selection Strategy

```python
def custom_model_selector(available_models, context):
    """Custom logic for model selection."""
    if context.get("task_type") == "creative":
        return "gemini_pro"  # Better for creative tasks
    elif context.get("task_type") == "analytical":
        return "openai_gpt4"  # Better for analysis
    else:
        return random.choice(available_models)

# Use with custom strategy
agent = DynamicAgentWrapper(
    model_configs=model_configs,
    strategy=custom_model_selector
)
```

### Context-Aware Switching

```python
# Update context based on your application logic
agent.update_context(
    task_type="creative",
    user_preference="fast",
    current_topic="artificial_intelligence"
)

# Your custom condition can use this context
def context_aware_condition(context):
    if context.get("task_type") == "creative" and context.get("current_model") == "openai_gpt4":
        return True  # Switch to Gemini for creative tasks
    return False
```

## Examples

See `usage_examples.py` for comprehensive examples including:
- Basic usage with rate limit handling
- Tool call count based switching
- Response content based switching
- Time-based switching
- Custom function conditions
- Combination conditions
- Tool response based switching
- Monitoring and debugging
- Integration with existing code
- Advanced context-aware switching

## License

MIT License - see LICENSE file for details.

## Author

**Sumit Paul** - sumit.18.paul@gmail.com

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
