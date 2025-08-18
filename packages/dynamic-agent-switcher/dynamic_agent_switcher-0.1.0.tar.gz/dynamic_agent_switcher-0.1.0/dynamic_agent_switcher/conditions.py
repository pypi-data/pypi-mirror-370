"""
Flexible switching conditions for dynamic agent switching.
"""

import asyncio
import time
import re
from typing import Dict, List, Optional, Any, Callable, Union
from enum import Enum
from dataclasses import dataclass
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class ConditionType(Enum):
    """Types of switching conditions."""
    RATE_LIMIT = "rate_limit"
    TOOL_CALL_COUNT = "tool_call_count"
    TOOL_RESPONSE = "tool_response"
    AI_RESPONSE_STATUS = "ai_response_status"
    AI_RESPONSE_CONTENT = "ai_response_content"
    TIME_BASED = "time_based"
    ERROR_COUNT = "error_count"
    CUSTOM_FUNCTION = "custom_function"
    COMBINATION = "combination"

@dataclass
class SwitchCondition:
    """A condition that determines when to switch models."""
    condition_type: ConditionType
    name: str
    description: str = ""
    enabled: bool = True
    priority: int = 1
    
    # Condition-specific parameters
    parameters: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}

class BaseCondition(ABC):
    """Base class for all switching conditions."""
    
    def __init__(self, condition: SwitchCondition):
        self.condition = condition
        
    @abstractmethod
    async def should_switch(self, context: Dict[str, Any]) -> bool:
        """Determine if the model should be switched based on this condition."""
        pass
        
    @abstractmethod
    def get_switch_reason(self, context: Dict[str, Any]) -> str:
        """Get the reason for switching."""
        pass

class RateLimitCondition(BaseCondition):
    """Switch when rate limit is detected."""
    
    async def should_switch(self, context: Dict[str, Any]) -> bool:
        # Consider multiple error fields and common vendor phrases
        error_message = (context.get("error_message") or context.get("last_error") or "").lower()
        patterns = [
            "rate limit",
            "429",
            "quota",
            "exceeded",
            "resource exhausted",
            "too many requests"
        ]
        return any(p in error_message for p in patterns)
        
    def get_switch_reason(self, context: Dict[str, Any]) -> str:
        return "Rate limit detected"

class ToolCallCountCondition(BaseCondition):
    """Switch after a certain number of tool calls."""
    
    async def should_switch(self, context: Dict[str, Any]) -> bool:
        max_calls = self.condition.parameters.get("max_calls", 5)
        current_calls = context.get("tool_call_count", 0)
        return current_calls >= max_calls
        
    def get_switch_reason(self, context: Dict[str, Any]) -> str:
        current_calls = context.get("tool_call_count", 0)
        max_calls = self.condition.parameters.get("max_calls", 5)
        return f"Tool call count exceeded ({current_calls}/{max_calls})"

class ToolResponseCondition(BaseCondition):
    """Switch based on tool response."""
    
    async def should_switch(self, context: Dict[str, Any]) -> bool:
        tool_response = context.get("tool_response", {})
        tool_name = context.get("tool_name", "")

        # Optional: check if this condition applies only to a specific tool
        target_tool = self.condition.parameters.get("tool_name")
        if target_tool and tool_name != target_tool:
            return False

        # Helper: extract nested value from dict/list using dotted path (e.g., "data.items.0.score")
        def _extract_value(obj: Any, path: Optional[str]) -> Any:
            if not path:
                return obj
            parts = str(path).split(".")
            cur = obj
            for part in parts:
                if isinstance(cur, dict) and part in cur:
                    cur = cur[part]
                elif isinstance(cur, list) and part.isdigit():
                    idx = int(part)
                    if 0 <= idx < len(cur):
                        cur = cur[idx]
                    else:
                        return None
                else:
                    return None
            return cur

        # Helper: try to coerce to float
        def _to_number(val: Any) -> Optional[float]:
            try:
                return float(val)
            except Exception:
                return None

        # Operator implementations
        def op_contains(target: Any, value: Any) -> bool:
            if isinstance(target, (list, dict)):
                return value in target
            return str(value) in str(target)

        def op_equals(target: Any, value: Any) -> bool:
            if type(target) is type(value):
                return target == value
            # Try numeric compare if possible
            tnum, vnum = _to_number(target), _to_number(value)
            if tnum is not None and vnum is not None:
                return tnum == vnum
            return str(target) == str(value)

        def op_regex(target: Any, value: Any) -> bool:
            try:
                return re.search(str(value), str(target)) is not None
            except re.error:
                return False

        def op_greater_than(target: Any, value: Any) -> bool:
            tnum, vnum = _to_number(target), _to_number(value)
            if tnum is None or vnum is None:
                return False
            return tnum > vnum

        def op_less_than(target: Any, value: Any) -> bool:
            tnum, vnum = _to_number(target), _to_number(value)
            if tnum is None or vnum is None:
                return False
            return tnum < vnum

        def op_between(target: Any, value: Any) -> bool:
            # value expected as [min, max]
            if not isinstance(value, (list, tuple)) or len(value) != 2:
                return False
            tnum, vmin, vmax = _to_number(target), _to_number(value[0]), _to_number(value[1])
            if None in (tnum, vmin, vmax):
                return False
            return vmin <= tnum <= vmax

        OP_EVALS = {
            "contains": op_contains,
            "equals": op_equals,
            "regex": op_regex,
            "greater_than": op_greater_than,
            "less_than": op_less_than,
            "between": op_between,
        }

        # Evaluate response conditions. Default logic is ANY.
        response_conditions = self.condition.parameters.get("response_conditions", [])
        logic = str(self.condition.parameters.get("logic", "ANY")).upper()

        results: List[bool] = []
        for cond in response_conditions:
            op = str(cond.get("type", "equals")).lower()
            value = cond.get("value")
            path = cond.get("path")  # optional dotted path into tool_response

            target = _extract_value(tool_response, path)
            evaluator = OP_EVALS.get(op, op_equals)
            try:
                results.append(evaluator(target, value))
            except Exception:
                results.append(False)

        if not results:
            return False

        if logic == "ALL":
            return all(results)
        elif logic == "NONE":
            return not any(results)
        else:  # ANY
            return any(results)
        
    def get_switch_reason(self, context: Dict[str, Any]) -> str:
        tool_name = context.get("tool_name", "unknown")
        return f"Tool response condition met for {tool_name}"

class AIResponseStatusCondition(BaseCondition):
    """Switch based on AI response status codes or patterns."""
    
    async def should_switch(self, context: Dict[str, Any]) -> bool:
        response = context.get("ai_response", {})
        status_codes = self.condition.parameters.get("status_codes", [])
        error_patterns = self.condition.parameters.get("error_patterns", [])
        
        # Check status codes
        if hasattr(response, 'status_code') and response.status_code in status_codes:
            return True
            
        # Check error patterns in response
        response_text = str(response)
        for pattern in error_patterns:
            if re.search(pattern, response_text, re.IGNORECASE):
                return True
                
        return False
        
    def get_switch_reason(self, context: Dict[str, Any]) -> str:
        return "AI response status condition met"

class AIResponseContentCondition(BaseCondition):
    """Switch based on AI response content."""
    
    async def should_switch(self, context: Dict[str, Any]) -> bool:
        response_content = context.get("ai_response_content", "")
        content_conditions = self.condition.parameters.get("content_conditions", [])
        
        for condition in content_conditions:
            condition_type = condition.get("type")
            value = condition.get("value")
            
            if condition_type == "contains" and value in response_content:
                return True
            elif condition_type == "regex" and re.search(value, response_content):
                return True
            elif condition_type == "length_greater_than" and len(response_content) > value:
                return True
            elif condition_type == "length_less_than" and len(response_content) < value:
                return True
            elif condition_type == "word_count_greater_than":
                word_count = len(response_content.split())
                if word_count > value:
                    return True
            elif condition_type == "word_count_less_than":
                word_count = len(response_content.split())
                if word_count < value:
                    return True
                    
        return False
        
    def get_switch_reason(self, context: Dict[str, Any]) -> str:
        return "AI response content condition met"

class TimeBasedCondition(BaseCondition):
    """Switch based on time conditions."""
    
    async def should_switch(self, context: Dict[str, Any]) -> bool:
        current_time = time.time()
        start_time = context.get("start_time", current_time)
        
        max_duration = self.condition.parameters.get("max_duration_seconds", 300)
        elapsed = current_time - start_time
        
        return elapsed >= max_duration
        
    def get_switch_reason(self, context: Dict[str, Any]) -> str:
        current_time = time.time()
        start_time = context.get("start_time", current_time)
        elapsed = current_time - start_time
        max_duration = self.condition.parameters.get("max_duration_seconds", 300)
        return f"Time limit exceeded ({elapsed:.1f}s/{max_duration}s)"

class ErrorCountCondition(BaseCondition):
    """Switch after a certain number of errors."""
    
    async def should_switch(self, context: Dict[str, Any]) -> bool:
        max_errors = self.condition.parameters.get("max_errors", 3)
        error_count = context.get("error_count", 0)
        return error_count >= max_errors
        
    def get_switch_reason(self, context: Dict[str, Any]) -> str:
        error_count = context.get("error_count", 0)
        max_errors = self.condition.parameters.get("max_errors", 3)
        return f"Error count exceeded ({error_count}/{max_errors})"

class CustomFunctionCondition(BaseCondition):
    """Switch based on a custom function."""
    
    async def should_switch(self, context: Dict[str, Any]) -> bool:
        custom_func = self.condition.parameters.get("function")
        if custom_func and callable(custom_func):
            try:
                if asyncio.iscoroutinefunction(custom_func):
                    return await custom_func(context)
                else:
                    return custom_func(context)
            except Exception as e:
                logger.error(f"Error in custom condition function: {e}")
                return False
        return False
        
    def get_switch_reason(self, context: Dict[str, Any]) -> str:
        return self.condition.parameters.get("reason", "Custom condition met")

class CombinationCondition(BaseCondition):
    """Switch based on combination of conditions."""
    
    async def should_switch(self, context: Dict[str, Any]) -> bool:
        conditions = self.condition.parameters.get("conditions", [])
        operator = self.condition.parameters.get("operator", "OR")  # AND, OR, XOR
        
        if not conditions:
            return False
            
        results = []
        for condition_config in conditions:
            condition = create_condition(condition_config)
            if condition:
                result = await condition.should_switch(context)
                results.append(result)
                
        if operator == "AND":
            return all(results)
        elif operator == "OR":
            return any(results)
        elif operator == "XOR":
            return sum(results) == 1
        else:
            return any(results)
            
    def get_switch_reason(self, context: Dict[str, Any]) -> str:
        return "Combination condition met"

def create_condition(condition_config: Union[SwitchCondition, Dict[str, Any]]) -> Optional[BaseCondition]:
    """Create a condition instance from configuration."""
    
    if isinstance(condition_config, SwitchCondition):
        condition = condition_config
    else:
        condition = SwitchCondition(
            condition_type=ConditionType(condition_config["type"]),
            name=condition_config["name"],
            description=condition_config.get("description", ""),
            enabled=condition_config.get("enabled", True),
            priority=condition_config.get("priority", 1),
            parameters=condition_config.get("parameters", {})
        )
    
    if not condition.enabled:
        return None
        
    condition_type = condition.condition_type
    
    if condition_type == ConditionType.RATE_LIMIT:
        return RateLimitCondition(condition)
    elif condition_type == ConditionType.TOOL_CALL_COUNT:
        return ToolCallCountCondition(condition)
    elif condition_type == ConditionType.TOOL_RESPONSE:
        return ToolResponseCondition(condition)
    elif condition_type == ConditionType.AI_RESPONSE_STATUS:
        return AIResponseStatusCondition(condition)
    elif condition_type == ConditionType.AI_RESPONSE_CONTENT:
        return AIResponseContentCondition(condition)
    elif condition_type == ConditionType.TIME_BASED:
        return TimeBasedCondition(condition)
    elif condition_type == ConditionType.ERROR_COUNT:
        return ErrorCountCondition(condition)
    elif condition_type == ConditionType.CUSTOM_FUNCTION:
        return CustomFunctionCondition(condition)
    elif condition_type == ConditionType.COMBINATION:
        return CombinationCondition(condition)
    else:
        logger.warning(f"Unknown condition type: {condition_type}")
        return None

# Predefined condition configurations for common use cases
def create_rate_limit_condition(max_errors: int = 3) -> SwitchCondition:
    """Create a rate limit condition."""
    return SwitchCondition(
        condition_type=ConditionType.RATE_LIMIT,
        name="rate_limit",
        description="Switch when rate limit is detected",
        priority=1
    )

def create_tool_call_count_condition(max_calls: int = 5) -> SwitchCondition:
    """Create a tool call count condition."""
    return SwitchCondition(
        condition_type=ConditionType.TOOL_CALL_COUNT,
        name="tool_call_count",
        description=f"Switch after {max_calls} tool calls",
        parameters={"max_calls": max_calls}
    )

def create_word_count_condition(max_words: int = 800) -> SwitchCondition:
    """Create a word count condition for AI responses."""
    return SwitchCondition(
        condition_type=ConditionType.AI_RESPONSE_CONTENT,
        name="word_count_limit",
        description=f"Switch when response exceeds {max_words} words",
        parameters={
            "content_conditions": [
                {"type": "word_count_greater_than", "value": max_words}
            ]
        }
    )

def create_time_limit_condition(max_seconds: int = 300) -> SwitchCondition:
    """Create a time limit condition."""
    return SwitchCondition(
        condition_type=ConditionType.TIME_BASED,
        name="time_limit",
        description=f"Switch after {max_seconds} seconds",
        parameters={"max_duration_seconds": max_seconds}
    )

def create_error_count_condition(max_errors: int = 3) -> SwitchCondition:
    """Create an error count condition."""
    return SwitchCondition(
        condition_type=ConditionType.ERROR_COUNT,
        name="error_count",
        description=f"Switch after {max_errors} errors",
        parameters={"max_errors": max_errors}
    )
