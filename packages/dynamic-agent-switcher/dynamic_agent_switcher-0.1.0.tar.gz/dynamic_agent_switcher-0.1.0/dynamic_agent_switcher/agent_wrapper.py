"""
Agent Wrapper - Easy replacement for existing Agent instances with dynamic switching.
"""

import asyncio
from typing import Dict, List, Optional, Any, Callable, Union
from pydantic_ai import Agent, Tool
from .switcher import DynamicAgentSwitcher, ModelConfig, SwitchStrategy
from .rate_limiter import RateLimiter, RateLimitConfig
from .conditions import SwitchCondition, ConditionType, create_condition
import logging

logger = logging.getLogger(__name__)

class DynamicAgentWrapper:
    """
    Wrapper that provides the same interface as pydantic_ai.Agent
    but with dynamic model switching capabilities.
    """
    
    def __init__(
        self,
        model_configs: List[ModelConfig],
        system_prompt: str = "",
        name: str = "DynamicAgent",
        output_type: Optional[type] = None,
        tools: Optional[List[Tool]] = None,
        strategy: SwitchStrategy = SwitchStrategy.RATE_LIMIT_BASED,
        conditions: List[Union[SwitchCondition, Dict[str, Any]]] = None,
        switch_threshold: int = 3,
        cooldown_seconds: int = 30
    ):
        self.switcher = DynamicAgentSwitcher(
            model_configs=model_configs,
            conditions=conditions,
            strategy=strategy,
            system_prompt=system_prompt,
            output_type=output_type,
            tools=tools,
            switch_threshold=switch_threshold,
            cooldown_seconds=cooldown_seconds
        )
        self.name = name
        self.system_prompt = system_prompt
        self.output_type = output_type
        self.tools = tools or []
        
    async def run(self, prompt: str, **kwargs) -> Any:
        """
        Run the agent with dynamic model switching.
        This method has the same signature as pydantic_ai.Agent.run()
        """
        return await self.switcher.run(prompt, max_attempts=kwargs.get('max_attempts', 5))
        
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the dynamic agent."""
        return self.switcher.get_status()
        
    def reset_context(self):
        """Reset the execution context."""
        self.switcher.reset_context()
        
    def add_condition(self, condition: Union[SwitchCondition, Dict[str, Any]]):
        """Add a new condition to the agent."""
        self.switcher.add_condition(condition)
        
    def remove_condition(self, condition_name: str):
        """Remove a condition by name."""
        self.switcher.remove_condition(condition_name)
        
    def update_context(self, **kwargs):
        """Update the execution context."""
        self.switcher.update_context(**kwargs)

def create_dynamic_agent_from_config(
    config: Dict[str, Any],
    system_prompt: str = "",
    name: str = "DynamicAgent",
    output_type: Optional[type] = None,
    tools: Optional[List[Tool]] = None,
    strategy: SwitchStrategy = SwitchStrategy.RATE_LIMIT_BASED,
    conditions: List[Union[SwitchCondition, Dict[str, Any]]] = None
) -> DynamicAgentWrapper:
    """
    Create a dynamic agent from a configuration dictionary.
    
    Args:
        config: Dictionary containing model configurations
        system_prompt: System prompt for the agent
        name: Name of the agent
        output_type: Expected output type
        tools: List of tools to attach
        strategy: Switching strategy
        conditions: List of switching conditions
        
    Returns:
        DynamicAgentWrapper instance
    """
    model_configs = []
    
    for model_name, model_config in config.items():
        config_obj = ModelConfig(
            name=model_name,
            provider=model_config["provider"],
            model_name=model_config["model_name"],
            api_key=model_config["api_key"],
            base_url=model_config.get("base_url"),
            weight=model_config.get("weight", 1.0),
            max_requests_per_minute=model_config.get("max_requests_per_minute", 60),
            timeout=model_config.get("timeout", 60),
            retries=model_config.get("retries", 3)
        )
        model_configs.append(config_obj)
        
    return DynamicAgentWrapper(
        model_configs=model_configs,
        system_prompt=system_prompt,
        name=name,
        output_type=output_type,
        tools=tools,
        strategy=strategy,
        conditions=conditions
    )

def replace_agent_with_dynamic(
    original_agent: Agent,
    model_configs: List[ModelConfig],
    strategy: SwitchStrategy = SwitchStrategy.RATE_LIMIT_BASED,
    conditions: List[Union[SwitchCondition, Dict[str, Any]]] = None
) -> DynamicAgentWrapper:
    """
    Replace an existing Agent with a dynamic version.
    
    Args:
        original_agent: The original pydantic_ai.Agent instance
        model_configs: List of model configurations for dynamic switching
        strategy: Switching strategy
        conditions: List of switching conditions
        
    Returns:
        DynamicAgentWrapper that mimics the original agent
    """
    return DynamicAgentWrapper(
        model_configs=model_configs,
        system_prompt=original_agent.system_prompt,
        name=original_agent.name,
        output_type=original_agent.output_type,
        tools=original_agent.tools,
        strategy=strategy,
        conditions=conditions
    )

# Example configuration for easy setup
def create_default_model_configs() -> List[ModelConfig]:
    """
    Create default model configurations for common providers.
    You should replace the API keys with your actual keys.
    """
    return [
        ModelConfig(
            name="openai_gpt4",
            provider="openai",
            model_name="gpt-4",
            api_key="your-openai-api-key",
            max_requests_per_minute=50,
            weight=1.0
        ),
        ModelConfig(
            name="gemini_pro",
            provider="gemini", 
            model_name="gemini-1.5-pro",
            api_key="your-gemini-api-key",
            max_requests_per_minute=60,
            weight=1.0
        ),
        ModelConfig(
            name="groq_llama3",
            provider="groq",
            model_name="llama3-70b-8192",
            api_key="your-groq-api-key", 
            max_requests_per_minute=100,
            weight=0.8
        )
    ]

# Example condition configurations
def create_default_conditions() -> List[Dict[str, Any]]:
    """
    Create default switching conditions for common scenarios.
    """
    return [
        {
            "type": ConditionType.RATE_LIMIT.value,
            "name": "rate_limit",
            "description": "Switch when rate limit is detected",
            "priority": 1
        },
        {
            "type": ConditionType.TOOL_CALL_COUNT.value,
            "name": "tool_call_limit",
            "description": "Switch after 5 tool calls",
            "parameters": {"max_calls": 5}
        },
        {
            "type": ConditionType.AI_RESPONSE_CONTENT.value,
            "name": "word_count_limit",
            "description": "Switch when response exceeds 800 words",
            "parameters": {
                "content_conditions": [
                    {"type": "word_count_greater_than", "value": 800}
                ]
            }
        },
        {
            "type": ConditionType.TIME_BASED.value,
            "name": "time_limit",
            "description": "Switch after 5 minutes",
            "parameters": {"max_duration_seconds": 300}
        }
    ]

def create_custom_condition(
    condition_type: ConditionType,
    name: str,
    description: str = "",
    parameters: Dict[str, Any] = None,
    priority: int = 1
) -> Dict[str, Any]:
    """
    Create a custom condition configuration.
    
    Args:
        condition_type: Type of condition
        name: Name of the condition
        description: Description of the condition
        parameters: Condition-specific parameters
        priority: Priority of the condition (lower = higher priority)
        
    Returns:
        Condition configuration dictionary
    """
    return {
        "type": condition_type.value,
        "name": name,
        "description": description,
        "parameters": parameters or {},
        "priority": priority
    }
