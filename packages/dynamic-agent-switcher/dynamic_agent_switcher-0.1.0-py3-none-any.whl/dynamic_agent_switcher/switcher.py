"""
Dynamic Agent Switcher - Core functionality for switching AI models during execution.
"""

import asyncio
import time
import random
from typing import Dict, List, Optional, Any, Callable, Union
from enum import Enum
from dataclasses import dataclass
from pydantic import BaseModel, Field
from pydantic_ai import Agent, Tool
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.providers.groq import GroqProvider
from .conditions import SwitchCondition, ConditionType, create_condition, BaseCondition
import logging

logger = logging.getLogger(__name__)

# Global cooldown map so all switchers avoid recently rate-limited models
GLOBAL_DISABLED_UNTIL: Dict[str, float] = {}

class SwitchStrategy(Enum):
    """Strategies for model switching."""
    ROUND_ROBIN = "round_robin"
    RATE_LIMIT_BASED = "rate_limit_based"
    RANDOM = "random"
    WEIGHTED = "weighted"
    FALLBACK = "fallback"

@dataclass
class ModelConfig:
    """Configuration for an AI model."""
    name: str
    provider: str
    model_name: str
    api_key: str
    base_url: Optional[str] = None
    weight: float = 1.0
    max_requests_per_minute: int = 60
    timeout: int = 60
    retries: int = 3
    is_active: bool = True

class ModelRegistry:
    """Registry for managing multiple AI models."""
    
    def __init__(self):
        self.models: Dict[str, ModelConfig] = {}
        self.request_counts: Dict[str, List[float]] = {}
        self.last_switch_time: Dict[str, float] = {}
        self.disabled_until: Dict[str, float] = {}
        
    def add_model(self, model_config: ModelConfig):
        """Add a model to the registry."""
        self.models[model_config.name] = model_config
        self.request_counts[model_config.name] = []
        self.last_switch_time[model_config.name] = 0
        self.disabled_until[model_config.name] = 0
        
    def get_model_config(self, name: str) -> Optional[ModelConfig]:
        """Get model configuration by name."""
        return self.models.get(name)
        
    def update_request_count(self, model_name: str):
        """Update request count for rate limiting."""
        current_time = time.time()
        self.request_counts[model_name].append(current_time)
        
        # Keep only requests from last minute
        self.request_counts[model_name] = [
            req_time for req_time in self.request_counts[model_name]
            if current_time - req_time < 60
        ]
        
    def is_rate_limited(self, model_name: str) -> bool:
        """Check if a model is rate limited."""
        if model_name not in self.models:
            return True
            
        config = self.models[model_name]
        current_count = len(self.request_counts.get(model_name, []))
        return current_count >= config.max_requests_per_minute
        
    def get_available_models(self) -> List[str]:
        """Get list of available (non-rate-limited) models."""
        available = []
        current_time = time.time()
        for name, config in self.models.items():
            if not config.is_active:
                continue
            # Skip models that are temporarily disabled due to recent rate limit errors
            if self.disabled_until.get(name, 0) > current_time:
                continue
            if GLOBAL_DISABLED_UNTIL.get(name, 0) > current_time:
                continue
            if not self.is_rate_limited(name):
                available.append(name)
        return available

    def temporarily_disable(self, model_name: str, seconds: int = 30):
        """Temporarily mark a model as unavailable (e.g., after a rate limit error)."""
        until = time.time() + max(0, seconds)
        self.disabled_until[model_name] = until
        GLOBAL_DISABLED_UNTIL[model_name] = max(GLOBAL_DISABLED_UNTIL.get(model_name, 0), until)

class DynamicAgentSwitcher:
    """
    Dynamic agent switcher that can switch between different AI models
    during execution based on configurable conditions.
    """
    
    def __init__(
        self,
        model_configs: List[ModelConfig],
        conditions: List[Union[SwitchCondition, Dict[str, Any]]] = None,
        strategy: SwitchStrategy = SwitchStrategy.RATE_LIMIT_BASED,
        system_prompt: str = "",
        output_type: Optional[type] = None,
        tools: Optional[List[Tool]] = None,
        switch_threshold: int = 3,
        cooldown_seconds: int = 30
    ):
        self.registry = ModelRegistry()
        self.strategy = strategy
        self.system_prompt = system_prompt
        self.output_type = output_type
        self.tools = tools or []
        self.switch_threshold = switch_threshold
        self.cooldown_seconds = cooldown_seconds
        
        # Initialize conditions
        self.conditions: List[BaseCondition] = []
        if conditions:
            for condition_config in conditions:
                condition = create_condition(condition_config)
                if condition:
                    self.conditions.append(condition)
        
        # Add default conditions if none provided
        if not self.conditions:
            self.conditions = [
                create_condition({
                    "type": ConditionType.RATE_LIMIT.value,
                    "name": "default_rate_limit",
                    "description": "Default rate limit condition"
                }),
                create_condition({
                    "type": ConditionType.ERROR_COUNT.value,
                    "name": "default_error_count",
                    "description": "Default error count condition",
                    "parameters": {"max_errors": 3}
                })
            ]
        
        # Add all models to registry
        for config in model_configs:
            self.registry.add_model(config)
            
        # Track current model and execution context
        self.current_model_name = None
        self.execution_context = {
            "start_time": time.time(),
            "error_count": 0,
            "tool_call_count": 0,
            "current_model": None,
            "last_error": None,
            "last_tool_response": None,
            "last_ai_response": None
        }
        
    def _create_agent(self, model_name: str) -> Agent:
        """Create an agent with the specified model."""
        config = self.registry.get_model_config(model_name)
        if not config:
            raise ValueError(f"Model {model_name} not found in registry")
            
        # Create model based on provider
        if config.provider == "gemini":
            model = GeminiModel(config.model_name, provider=GoogleGLAProvider(api_key=config.api_key))
        elif config.provider == "openai":
            model = OpenAIModel(config.model_name, provider=OpenAIProvider(api_key=config.api_key))
        elif config.provider == "groq":
            model = GroqModel(config.model_name, provider=GroqProvider(api_key=config.api_key))
        else:
            raise ValueError(f"Unsupported provider: {config.provider}")
            
        return Agent(
            model,
            system_prompt=self.system_prompt,
            name=f"DynamicAgent_{model_name}",
            output_type=self.output_type,
            tools=self.tools,
            model_settings={"timeout": config.timeout},
            retries=config.retries
        )
        
    def _select_next_model(self, strategy: SwitchStrategy) -> Optional[str]:
        """Select the next model based on the strategy."""
        available_models = self.registry.get_available_models()
        
        if not available_models:
            logger.warning("No available models found")
            return None
            
        if strategy == SwitchStrategy.ROUND_ROBIN:
            # Simple round-robin selection
            if not self.current_model_name or self.current_model_name not in available_models:
                return available_models[0]
            
            current_index = available_models.index(self.current_model_name)
            next_index = (current_index + 1) % len(available_models)
            return available_models[next_index]
            
        elif strategy == SwitchStrategy.RATE_LIMIT_BASED:
            # Select model with lowest current request count
            best_model = None
            min_requests = float('inf')
            
            for model_name in available_models:
                request_count = len(self.registry.request_counts.get(model_name, []))
                if request_count < min_requests:
                    min_requests = request_count
                    best_model = model_name
                    
            return best_model
            
        elif strategy == SwitchStrategy.RANDOM:
            # Random selection from available models
            return random.choice(available_models)
            
        elif strategy == SwitchStrategy.WEIGHTED:
            # Weighted selection based on model weights
            total_weight = sum(self.registry.models[model].weight for model in available_models)
            if total_weight == 0:
                return random.choice(available_models)
                
            rand_val = random.uniform(0, total_weight)
            current_weight = 0
            
            for model_name in available_models:
                current_weight += self.registry.models[model_name].weight
                if rand_val <= current_weight:
                    return model_name
                    
            return available_models[-1]
            
        elif strategy == SwitchStrategy.FALLBACK:
            # Use fallback strategy: try current, then others in order
            if self.current_model_name and self.current_model_name in available_models:
                return self.current_model_name
            return available_models[0]
            
        return available_models[0]
        
    async def _should_switch_model(self) -> tuple[bool, str]:
        """Determine if we should switch models based on conditions."""
        current_time = time.time()
        
        # Update context with current model
        self.execution_context["current_model"] = self.current_model_name
        
        # Check all conditions
        for condition in self.conditions:
            try:
                if await condition.should_switch(self.execution_context):
                    reason = condition.get_switch_reason(self.execution_context)
                    logger.debug(f"Condition '{condition.condition.name}' triggered: {reason}")
                    # If the triggering condition is RATE_LIMIT, bypass cooldown to switch immediately
                    from .conditions import ConditionType as _CT
                    if condition.condition.condition_type == _CT.RATE_LIMIT:
                        return True, reason
                    # Enforce cooldown for non-rate-limit condition triggers
                    if current_time - self.execution_context.get("last_error_time", 0) < self.cooldown_seconds:
                        return False, "In cooldown period"
                    return True, reason
            except Exception as e:
                logger.error(f"Error checking condition {condition.condition.name}: {e}")
                
        return False, "No conditions met"
        
    def update_context(self, **kwargs):
        """Update the execution context with new information."""
        self.execution_context.update(kwargs)
        
    async def run(self, prompt: str, max_attempts: int = 5) -> Any:
        """
        Run the agent with dynamic model switching.
        
        Args:
            prompt: The prompt to send to the agent
            max_attempts: Maximum number of attempts before giving up
            
        Returns:
            The agent's response
            
        Raises:
            Exception: If all attempts fail
        """
        last_exception = None
        
        for attempt in range(max_attempts):
            try:
                # Determine if we should switch models
                should_switch, reason = await self._should_switch_model()
                if should_switch or not self.current_model_name:
                    new_model = self._select_next_model(self.strategy)
                    if new_model:
                        self.current_model_name = new_model
                        logger.info(f"Switched to model: {new_model} - Reason: {reason}")
                    else:
                        # Wait a bit and try again
                        await asyncio.sleep(2)
                        continue
                        
                # Create agent with current model
                agent = self._create_agent(self.current_model_name)
                
                # Update request count
                self.registry.update_request_count(self.current_model_name)
                
                # Run the agent
                logger.debug(f"Running agent with model: {self.current_model_name} (attempt {attempt + 1})")
                result = await agent.run(prompt)
                
                # Update context with successful response
                self.update_context(
                    last_ai_response=result,
                    error_count=0,  # Reset error count on success
                    last_error=None
                )
                
                return result
                
            except Exception as e:
                last_exception = e
                self.execution_context["error_count"] += 1
                self.execution_context["last_error"] = str(e)
                self.execution_context["last_error_time"] = time.time()
                self.execution_context["error_message"] = str(e)
                
                logger.warning(f"Attempt {attempt + 1} failed with model {self.current_model_name}: {str(e)}")

                # If we hit a rate limit, temporarily disable this model to avoid immediate reuse
                err = str(e).lower()
                if any(token in err for token in ["rate limit", "429", "quota", "resource exhausted", "exceeded"]):
                    try:
                        self.registry.temporarily_disable(self.current_model_name, self.cooldown_seconds)
                        logger.debug(f"Temporarily disabled model '{self.current_model_name}' for {self.cooldown_seconds}s due to rate limit")
                    except Exception:
                        pass
                
                # Wait before retry
                await asyncio.sleep(1 + random.uniform(0, 2))
                
        # All attempts failed
        raise Exception(f"All {max_attempts} attempts failed. Last error: {str(last_exception)}")
        
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the switcher."""
        return {
            "current_model": self.current_model_name,
            "available_models": self.registry.get_available_models(),
            "model_request_counts": {
                name: len(counts) for name, counts in self.registry.request_counts.items()
            },
            "strategy": self.strategy.value,
            "conditions": [condition.condition.name for condition in self.conditions],
            "execution_context": self.execution_context
        }
        
    def reset_context(self):
        """Reset the execution context."""
        self.execution_context = {
            "start_time": time.time(),
            "error_count": 0,
            "tool_call_count": 0,
            "current_model": None,
            "last_error": None,
            "last_tool_response": None,
            "last_ai_response": None
        }
        
    def add_condition(self, condition: Union[SwitchCondition, Dict[str, Any]]):
        """Add a new condition to the switcher."""
        condition_instance = create_condition(condition)
        if condition_instance:
            self.conditions.append(condition_instance)
            logger.info(f"Added condition: {condition_instance.condition.name}")
        else:
            logger.warning("Failed to create condition instance")
            
    def remove_condition(self, condition_name: str):
        """Remove a condition by name."""
        self.conditions = [c for c in self.conditions if c.condition.name != condition_name]
        logger.info(f"Removed condition: {condition_name}")
