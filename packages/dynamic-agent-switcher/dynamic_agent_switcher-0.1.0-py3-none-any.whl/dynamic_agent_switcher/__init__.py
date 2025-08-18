"""
Dynamic Agent Switcher - A package to switch AI models during agent execution
to handle rate limits and distribute API calls across different providers.
"""

__version__ = "0.1.1"

from .switcher import DynamicAgentSwitcher, ModelConfig, SwitchStrategy
from .rate_limiter import RateLimiter, RateLimitConfig
from .conditions import SwitchCondition, ConditionType, create_condition
from .agent_wrapper import DynamicAgentWrapper, create_dynamic_agent_from_config, replace_agent_with_dynamic

__all__ = [
    "DynamicAgentSwitcher",
    "ModelConfig", 
    "SwitchStrategy",
    "RateLimiter",
    "RateLimitConfig",
    "SwitchCondition",
    "ConditionType",
    "create_condition",
    "DynamicAgentWrapper",
    "create_dynamic_agent_from_config",
    "replace_agent_with_dynamic"
]
