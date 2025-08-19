import time
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Union
from enum import Enum

class ModelType(Enum):
    STANDARD = "lumi-o1"
    MINI = "lumi-o1-mini"
    PRO = "lumi-o1-pro"
    HIGH = "lumi-o1-high"
    O3 = "lumi-o3"

@dataclass
class FileAttachment:
    name: str
    content: str
    mime_type: str = "text/plain"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "content": self.content,
            "mime_type": self.mime_type
        }

@dataclass
class Message:
    role: str
    content: str
    files: List[FileAttachment] = field(default_factory=list)
    name: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None
    
    def __post_init__(self):
        valid_roles = ["user", "assistant", "system", "tool"]
        if self.role not in valid_roles:
            raise ValueError(f"Invalid role: {self.role}")
    
    def add_file(self, name: str, content: str, mime_type: str = "text/plain") -> "Message":
        self.files.append(FileAttachment(name, content, mime_type))
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        data = {"role": self.role, "content": self.content}
        
        if self.files:
            data["files"] = [f.to_dict() for f in self.files]
        if self.name:
            data["name"] = self.name
        if self.tool_calls:
            data["tool_calls"] = self.tool_calls
        if self.tool_call_id:
            data["tool_call_id"] = self.tool_call_id
            
        return data

@dataclass
class ReasoningConfig:
    enabled: bool = True
    effort: str = "medium"
    
    def __post_init__(self):
        if self.effort not in ["low", "medium", "high"]:
            raise ValueError(f"Invalid effort: {self.effort}")
    
    def to_dict(self) -> Dict[str, Any]:
        return {"enabled": self.enabled, "effort": self.effort}

@dataclass
class ToolFunction:
    name: str
    description: str
    parameters: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }

@dataclass
class ChatOptions:
    model: str
    temperature: float = 1.0
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop: Optional[Union[str, List[str]]] = None
    reasoning: Optional[ReasoningConfig] = None
    stream: bool = False
    tools: Optional[List[ToolFunction]] = None
    tool_choice: str = "auto"
    response_format: Optional[Dict[str, str]] = None
    seed: Optional[int] = None
    user: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = {
            "model": self.model,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "stream": self.stream
        }
        
        if self.max_tokens:
            data["max_tokens"] = self.max_tokens
        if self.stop:
            data["stop"] = self.stop
        if self.reasoning:
            data["reasoning"] = self.reasoning.to_dict()
        if self.tools:
            data["tools"] = [tool.to_dict() for tool in self.tools]
            data["tool_choice"] = self.tool_choice
        if self.response_format:
            data["response_format"] = self.response_format
        if self.seed:
            data["seed"] = self.seed
        if self.user:
            data["user"] = self.user
            
        return data

@dataclass
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0
    system_tokens: int = 0
    reasoning_tokens: int = 0
    total_tokens: int = 0
    
    def __post_init__(self):
        if self.total_tokens == 0:
            self.total_tokens = self.input_tokens + self.output_tokens + self.system_tokens + self.reasoning_tokens

@dataclass
class ChatChoice:
    message: Message
    reasoning: Optional[Dict[str, Any]] = None
    finish_reason: Optional[str] = None
    index: int = 0

@dataclass
class ChatResponse:
    id: str
    model: str
    provider: str
    choices: List[ChatChoice]
    usage: Usage
    created: int = field(default_factory=lambda: int(time.time()))
    
    @property
    def first_choice(self) -> Optional[ChatChoice]:
        return self.choices[0] if self.choices else None
    
    @property
    def content(self) -> str:
        choice = self.first_choice
        return choice.message.content if choice else ""
    
    @property
    def reasoning_data(self) -> Optional[Dict[str, Any]]:
        choice = self.first_choice
        return choice.reasoning if choice else None

@dataclass
class StreamDelta:
    type: str
    content: Optional[str] = None
    reasoning: Optional[Dict[str, Any]] = None
    usage: Optional[Usage] = None
    finish_reason: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None

@dataclass
class Model:
    id: str
    name: str
    supports_reasoning: bool = False
    supports_tools: bool = True
    is_default: bool = False
    has_native_reasoning: bool = False
    max_tokens: int = 4096
    context_window: int = 128000
    
    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "Model":
        return cls(
            id=data["id"],
            name=data["name"],
            supports_reasoning=data.get("supportsReasoning", False),
            supports_tools=data.get("supportsTools", True),
            is_default=data.get("isDefault", False),
            has_native_reasoning=data.get("hasNativeReasoning", False),
            max_tokens=data.get("maxTokens", 4096),
            context_window=data.get("contextWindow", 128000)
        )

@dataclass
class ModelsResponse:
    models: List[Model]
    plan: str
    limits: Dict[str, Any]
    
    def get_model(self, model_id: str) -> Optional[Model]:
        return next((m for m in self.models if m.id == model_id), None)
    
    def get_reasoning_models(self) -> List[Model]:
        return [m for m in self.models if m.supports_reasoning or m.has_native_reasoning]
    
    def get_default_models(self) -> List[Model]:
        return [m for m in self.models if m.is_default]