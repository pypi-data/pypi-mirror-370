from .client import genai
from .models import (
    Message, ChatOptions, ChatResponse, StreamDelta,
    Model, ModelsResponse, ReasoningConfig, ToolFunction,
    FileAttachment, Usage, ChatChoice
)
from .exceptions import (
    LunaVerseXError, APIError, ValidationError,
    ConfigurationError, ModelNotFoundError
)

__version__ = "1.0.0"
__author__ = "LunaVerseX"
__email__ = "support@lunaversex.com"

__all__ = [
    "genai",
    "Message", "ChatOptions", "ChatResponse", "StreamDelta",
    "Model", "ModelsResponse", "ReasoningConfig", "ToolFunction", 
    "FileAttachment", "Usage", "ChatChoice",
    "LunaVerseXError", "APIError", "ValidationError",
    "ConfigurationError", "ModelNotFoundError"
]