"""Data models for OpenRouter Client.

This module defines Pydantic models for structured data representation
of API requests, responses, and configuration.

Exported:
- Base models (from core.py)
- Chat-related models (from chat.py)
- Completions-related models (from completions.py)
- Models-related models (from models.py)
- Credits-related models (from credits.py)
- Provider-related models (from providers.py)
- Generations-related models (from generations.py)
"""

from .core import (
    FunctionDefinition,
    ToolDefinition,
    ResponseFormat,
    Message,
)

from .chat import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionResponseChoice,
    ChatCompletionStreamResponse,
    ChatCompletionStreamResponseChoice,
    ChatCompletionStreamResponseDelta,
    ChatCompletionFunction,
    ChatCompletionFunctionCall,
    ChatCompletionTool,
    ChatCompletionToolCall,
    ChatCompletionToolChoiceOption,
    ToolCallChunk,
    ToolCallFunction,
    Usage,
    ReasoningConfig,
)

from .completions import (
    CompletionsRequest,
    CompletionsResponse,
    CompletionsResponseChoice,
    CompletionsStreamResponse,
    LogProbs,
)

from .models import (
    Model,
    ModelList,
    ModelPermission,
    ModelProvider,
    ModelPricing,
    ModelQuantization,
    ModelContextWindow,
    ModelDataPolicy,
)

from .credits import (
    CreditsResponse,
)

from .providers import (
    ProviderPreferences,
    ProviderMaxPrice,
)

from .generations import (
    Generation,
    GenerationList,
    GenerationListParams,
    GenerationUsage,
    GenerationCost,
    GenerationStats,
    GenerationStatsParams,
    ModelStats,
    ModelStatsParams,
    StatsPoint,
    ModelStatsPoint,
    GenerationListMeta,
)

# Function models are imported from chat.py
from .chat import (
    ParameterType,
    ParameterDefinition,
    StringParameter,
    NumberParameter,
    BooleanParameter,
    ArrayParameter,
    ObjectParameter,
    FunctionParameters,
    FunctionCall,
    FunctionCallResult,
    StructuredToolResult,
    FunctionToolChoice,
    ToolChoice,
)

# Simple API models
from .attachment import Attachment
from .llm import LLMModel, get_model

__all__ = [
    # Core models
    "FunctionDefinition",
    "ToolDefinition",
    "ResponseFormat",
    "Message",
    
    # Chat models
    "ChatCompletionRequest",
    "ChatCompletionResponse",
    "ChatCompletionResponseChoice",
    "ChatCompletionStreamResponse",
    "ChatCompletionStreamResponseChoice",
    "ChatCompletionStreamResponseDelta",
    "ChatCompletionFunction",
    "ChatCompletionFunctionCall",
    "ChatCompletionTool",
    "ChatCompletionToolCall",
    "ChatCompletionToolChoiceOption",
    "ToolCallChunk",
    "ToolCallFunction",
    "Usage",
    "ReasoningConfig",
    
    # Completions models
    "CompletionsRequest",
    "CompletionsResponse",
    "CompletionsResponseChoice",
    "CompletionsStreamResponse",
    "LogProbs",
    
    # Models models
    "Model",
    "ModelList",
    "ModelPermission",
    "ModelProvider",
    "ModelPricing",
    "ModelQuantization",
    "ModelContextWindow",
    "ModelDataPolicy",
    
    # Credits models
    "CreditsResponse",
    
    # Provider models
    "ProviderPreferences",
    "ProviderMaxPrice",
    
    # Generations models
    "Generation",
    "GenerationList",
    "GenerationListParams",
    "GenerationUsage",
    "GenerationCost",
    "GenerationStats",
    "GenerationStatsParams",
    "ModelStats",
    "ModelStatsParams",
    "StatsPoint",
    "ModelStatsPoint",
    "GenerationListMeta",
    
    # Function call models
    "ParameterType",
    "ParameterDefinition",
    "StringParameter",
    "NumberParameter",
    "BooleanParameter",
    "ArrayParameter",
    "ObjectParameter",
    "FunctionParameters",
    "FunctionCall",
    "FunctionCallResult",
    "StructuredToolResult",
    "FunctionToolChoice",
    "ToolChoice",
    
    # Simple API
    "Attachment",
    "LLMModel",
    "get_model",
]