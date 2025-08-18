"""
Usage examples for Dynamic Agent Switcher package.
"""

import asyncio
from dynamic_agent_switcher import (
    DynamicAgentWrapper,
    ModelConfig,
    SwitchStrategy,
    ConditionType,
    create_custom_condition,
    create_default_conditions
)

# Example 1: Basic usage with rate limit handling
async def basic_example():
    """Basic example with rate limit handling."""
    
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
    
    agent = DynamicAgentWrapper(
        model_configs=model_configs,
        system_prompt="You are a helpful AI assistant.",
        strategy=SwitchStrategy.RATE_LIMIT_BASED
    )
    
    result = await agent.run("Generate a story about a robot.")
    print(f"Result: {result}")

# Example 2: Tool call count based switching
async def tool_call_example():
    """Example that switches after a certain number of tool calls."""
    
    model_configs = [
        ModelConfig("openai_gpt4", "openai", "gpt-4", "your-key"),
        ModelConfig("gemini_pro", "gemini", "gemini-1.5-pro", "your-key")
    ]
    
    tool_call_condition = {
        "type": ConditionType.TOOL_CALL_COUNT.value,
        "name": "tool_call_limit",
        "parameters": {"max_calls": 3}
    }
    
    agent = DynamicAgentWrapper(
        model_configs=model_configs,
        conditions=[tool_call_condition]
    )
    
    # Simulate tool calls
    agent.update_context(tool_call_count=2)
    result = await agent.run("Generate content with multiple tool calls.")
    print(f"Result: {result}")

# Example 3: Response content based switching
async def content_based_example():
    """Example that switches based on response content."""
    
    model_configs = [
        ModelConfig("openai_gpt4", "openai", "gpt-4", "your-key"),
        ModelConfig("gemini_pro", "gemini", "gemini-1.5-pro", "your-key")
    ]
    
    word_count_condition = {
        "type": ConditionType.AI_RESPONSE_CONTENT.value,
        "name": "word_limit",
        "parameters": {
            "content_conditions": [
                {"type": "word_count_greater_than", "value": 500}
            ]
        }
    }
    
    agent = DynamicAgentWrapper(
        model_configs=model_configs,
        conditions=[word_count_condition]
    )
    
    result = await agent.run("Write a detailed explanation of machine learning.")
    print(f"Result: {result}")

# Example 4: Time-based switching
async def time_based_example():
    """Example that switches after a time limit."""
    
    model_configs = [
        ModelConfig("openai_gpt4", "openai", "gpt-4", "your-key"),
        ModelConfig("gemini_pro", "gemini", "gemini-1.5-pro", "your-key")
    ]
    
    time_condition = {
        "type": ConditionType.TIME_BASED.value,
        "name": "time_limit",
        "parameters": {"max_duration_seconds": 120}  # 2 minutes
    }
    
    agent = DynamicAgentWrapper(
        model_configs=model_configs,
        conditions=[time_condition]
    )
    
    result = await agent.run("Generate a complex analysis.")
    print(f"Result: {result}")

# Example 5: Custom function condition
async def custom_function_example():
    """Example with custom switching logic."""
    
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
    
    def is_peak_hours():
        """Check if it's peak hours (simplified)."""
        import datetime
        hour = datetime.datetime.now().hour
        return 9 <= hour <= 17  # 9 AM to 5 PM
    
    model_configs = [
        ModelConfig("openai_gpt4", "openai", "gpt-4", "your-key"),
        ModelConfig("gemini_pro", "gemini", "gemini-1.5-pro", "your-key")
    ]
    
    custom_condition = {
        "type": ConditionType.CUSTOM_FUNCTION.value,
        "name": "custom_logic",
        "parameters": {
            "function": custom_switch_logic,
            "reason": "Custom business logic"
        }
    }
    
    agent = DynamicAgentWrapper(
        model_configs=model_configs,
        conditions=[custom_condition]
    )
    
    result = await agent.run("Generate content.")
    print(f"Result: {result}")

# Example 6: Combination conditions
async def combination_example():
    """Example with combination of multiple conditions."""
    
    model_configs = [
        ModelConfig("openai_gpt4", "openai", "gpt-4", "your-key"),
        ModelConfig("gemini_pro", "gemini", "gemini-1.5-pro", "your-key")
    ]
    
    combination_condition = {
        "type": ConditionType.COMBINATION.value,
        "name": "complex_logic",
        "operator": "OR",  # Switch if ANY condition is met
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
    
    agent = DynamicAgentWrapper(
        model_configs=model_configs,
        conditions=[combination_condition]
    )
    
    result = await agent.run("Generate complex content with multiple requirements.")
    print(f"Result: {result}")

# Example 7: Tool response based switching
async def tool_response_example():
    """Example that switches based on tool responses."""
    
    model_configs = [
        ModelConfig("openai_gpt4", "openai", "gpt-4", "your-key"),
        ModelConfig("gemini_pro", "gemini", "gemini-1.5-pro", "your-key")
    ]
    
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
    
    agent = DynamicAgentWrapper(
        model_configs=model_configs,
        conditions=[tool_response_condition]
    )
    
    # Simulate tool response
    agent.update_context(
        tool_name="validate_html",
        tool_response={"is_valid": False, "errors": ["invalid tag"]}
    )
    
    result = await agent.run("Generate HTML content.")
    print(f"Result: {result}")

# Example 8: Monitoring and debugging
async def monitoring_example():
    """Example showing monitoring and debugging capabilities."""
    
    model_configs = [
        ModelConfig("openai_gpt4", "openai", "gpt-4", "your-key"),
        ModelConfig("gemini_pro", "gemini", "gemini-1.5-pro", "your-key")
    ]
    
    agent = DynamicAgentWrapper(
        model_configs=model_configs,
        conditions=create_default_conditions()
    )
    
    # Get initial status
    status = agent.get_status()
    print(f"Initial status: {status}")
    
    # Update context manually
    agent.update_context(
        tool_call_count=5,
        last_tool_response={"word_count": 750},
        task_type="creative"
    )
    
    # Get updated status
    status = agent.get_status()
    print(f"Updated status: {status}")
    
    # Add a new condition dynamically
    new_condition = create_custom_condition(
        condition_type=ConditionType.ERROR_COUNT,
        name="dynamic_error_limit",
        parameters={"max_errors": 2}
    )
    agent.add_condition(new_condition)
    
    result = await agent.run("Generate content with monitoring.")
    print(f"Result: {result}")

# Example 9: Integration with existing code
async def integration_example():
    """Example showing integration with existing pydantic_ai.Agent code."""
    
    from pydantic_ai import Agent, Tool
    from pydantic_ai.models.openai import OpenAIModel
    from pydantic_ai.providers.openai import OpenAIProvider
    
    # Your existing agent
    openai_model = OpenAIModel("gpt-4", provider=OpenAIProvider(api_key="your-key"))
    
    original_agent = Agent(
        openai_model,
        system_prompt="You are a helpful assistant.",
        tools=[Tool(lambda x: len(x.split()))]  # Simple word counter
    )
    
    # Replace with dynamic version
    from dynamic_agent_switcher import replace_agent_with_dynamic
    
    model_configs = [
        ModelConfig("openai_gpt4", "openai", "gpt-4", "your-key"),
        ModelConfig("gemini_pro", "gemini", "gemini-1.5-pro", "your-key")
    ]
    
    dynamic_agent = replace_agent_with_dynamic(
        original_agent=original_agent,
        model_configs=model_configs,
        conditions=create_default_conditions()
    )
    
    # Use exactly the same way
    result = await dynamic_agent.run("Generate content.")
    print(f"Result: {result}")

# Example 10: Advanced context-aware switching
async def context_aware_example():
    """Example showing context-aware switching."""
    
    model_configs = [
        ModelConfig("openai_gpt4", "openai", "gpt-4", "your-key"),
        ModelConfig("gemini_pro", "gemini", "gemini-1.5-pro", "your-key")
    ]
    
    def context_aware_condition(context):
        """Switch based on context."""
        task_type = context.get("task_type")
        current_model = context.get("current_model")
        
        # Switch to Gemini for creative tasks
        if task_type == "creative" and current_model == "openai_gpt4":
            return True
        
        # Switch to OpenAI for analytical tasks
        if task_type == "analytical" and current_model == "gemini_pro":
            return True
        
        return False
    
    custom_condition = {
        "type": ConditionType.CUSTOM_FUNCTION.value,
        "name": "context_aware",
        "parameters": {
            "function": context_aware_condition,
            "reason": "Context-aware switching"
        }
    }
    
    agent = DynamicAgentWrapper(
        model_configs=model_configs,
        conditions=[custom_condition]
    )
    
    # Update context for creative task
    agent.update_context(task_type="creative")
    result1 = await agent.run("Write a creative story.")
    print(f"Creative result: {result1}")
    
    # Update context for analytical task
    agent.update_context(task_type="analytical")
    result2 = await agent.run("Analyze this data.")
    print(f"Analytical result: {result2}")

# Run all examples
async def run_all_examples():
    """Run all examples."""
    print("Running Dynamic Agent Switcher examples...")
    
    examples = [
        ("Basic Example", basic_example),
        ("Tool Call Example", tool_call_example),
        ("Content Based Example", content_based_example),
        ("Time Based Example", time_based_example),
        ("Custom Function Example", custom_function_example),
        ("Combination Example", combination_example),
        ("Tool Response Example", tool_response_example),
        ("Monitoring Example", monitoring_example),
        ("Integration Example", integration_example),
        ("Context Aware Example", context_aware_example)
    ]
    
    for name, example_func in examples:
        print(f"\n{'='*50}")
        print(f"Running: {name}")
        print('='*50)
        try:
            await example_func()
            print(f"✓ {name} completed successfully")
        except Exception as e:
            print(f"✗ {name} failed: {e}")

if __name__ == "__main__":
    asyncio.run(run_all_examples())
