import asyncio
import aiohttp
import time
import logging
from typing import Optional, List, Dict, Any, AsyncGenerator, Tuple

from .models import (
    Message, ChatOptions, ChatResponse, StreamDelta,
    Model, ModelsResponse, ReasoningConfig, ChatChoice, Usage
)
from .exceptions import APIError, ConfigurationError, ModelNotFoundError, ValidationError
from .utils import TextProcessor, ModelCache, StreamParser, retry_async

__version__ = "1.0.0"

class Configuration:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.lunaversex.com",
        timeout: int = 30,
        debug: bool = False
    ):
        if not api_key:
            raise ConfigurationError("API key is required")
        
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.debug = debug
        
        if debug:
            logging.basicConfig(level=logging.DEBUG)

class HTTPClient:
    def __init__(self, base_url: str, api_key: str, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self._session: Optional[aiohttp.ClientSession] = None
    
    @property
    def session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=self.timeout,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}",
                    "User-Agent": f"LunaVerseX-Python-SDK/{__version__}"
                }
            )
        return self._session
    
    async def request(self, method: str, endpoint: str, json_data: Optional[Dict] = None) -> aiohttp.ClientResponse:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = await self.session.request(method, url, json=json_data)
            
            if not response.ok:
                error_text = await response.text()
                raise APIError(f"API request failed: {response.status} {error_text}", response.status)
            
            return response
        except aiohttp.ClientError as e:
            raise APIError(f"HTTP client error: {str(e)}")
    
    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

class LunaVerseXGenAI:
    def __init__(self, config: Optional[Configuration] = None):
        self._config = config
        self._http_client: Optional[HTTPClient] = None
        self._model_cache = ModelCache()
    
    def init(self, api_key: str, base_url: str = "https://api.lunaversex.com", **kwargs):
        """Initialize the SDK with API credentials and configuration"""
        config = Configuration(api_key, base_url, **kwargs)
        self._config = config
        if self._http_client:
            asyncio.create_task(self._http_client.close())
        self._http_client = None
        self._model_cache = ModelCache()
    
    @property
    def http_client(self) -> HTTPClient:
        if self._http_client is None:
            if not self._config:
                raise ConfigurationError("SDK not initialized. Call genai.init() first")
            self._http_client = HTTPClient(
                self._config.base_url,
                self._config.api_key,
                self._config.timeout
            )
        return self._http_client
    
    @retry_async(max_retries=3)
    async def listModels(self) -> ModelsResponse:
        """Retrieve all available AI models with their capabilities"""
        async def fetch_models() -> ModelsResponse:
            response = await self.http_client.request("GET", "/models")
            data = await response.json()
            
            models = [Model.from_api(m) for m in data.get("models", [])]
            
            return ModelsResponse(
                models=models,
                plan=data.get("plan", "unknown"),
                limits=data.get("limits", {})
            )
        
        return await self._model_cache.get_models(fetch_models)
    
    async def _validate_request(self, options: ChatOptions) -> ChatOptions:
        if not self._model_cache.is_valid_model(options.model):
            raise ModelNotFoundError(
                f"Invalid model: {options.model}. Use genai.listModels() for available models"
            )
        
        model = self._model_cache.get_model(options.model)
        
        if model:
            if options.reasoning and not model.supports_reasoning and not model.has_native_reasoning:
                logging.warning(f"Model {options.model} doesn't support reasoning. Parameter ignored")
                options.reasoning = None
            
            if options.tools and not model.supports_tools:
                raise ValidationError(f"Model {options.model} doesn't support tools")
            
            if model.id == "lumi-o3" and options.reasoning:
                logging.info("Lumi o3 has native reasoning. Reasoning config ignored")
                options.reasoning = None
        
        return options
    
    @retry_async(max_retries=3)
    async def chat(self, messages: List[Message], options: ChatOptions) -> ChatResponse:
        """Send messages to AI model and receive complete response"""
        options = await self._validate_request(options)
        
        payload = {
            "messages": [msg.to_dict() for msg in messages],
            **options.to_dict()
        }
        payload["stream"] = False
        
        response = await self.http_client.request("POST", "/chat/v1", payload)
        data = await response.json()
        
        choices = []
        for i, choice_data in enumerate(data.get("choices", [])):
            msg_data = choice_data["message"]
            message = Message(
                role=msg_data["role"],
                content=TextProcessor.clean_text(msg_data["content"])
            )
            
            if msg_data.get("tool_calls"):
                message.tool_calls = msg_data["tool_calls"]
            
            choices.append(ChatChoice(
                message=message,
                reasoning=choice_data.get("reasoning"),
                finish_reason=choice_data.get("finish_reason"),
                index=i
            ))
        
        usage_data = data.get("usage", {})
        usage = Usage(
            input_tokens=usage_data.get("prompt_tokens", 0),
            output_tokens=usage_data.get("completion_tokens", 0),
            system_tokens=usage_data.get("system_tokens", 0),
            reasoning_tokens=usage_data.get("reasoning_tokens", 0)
        )
        
        return ChatResponse(
            id=data.get("id", f"chat-{int(time.time())}"),
            model=data.get("model", options.model),
            provider=data.get("provider", "LunaVerseX Cloud"),
            choices=choices,
            usage=usage,
            created=data.get("created", int(time.time()))
        )
    
    async def chatStream(self, messages: List[Message], options: ChatOptions) -> AsyncGenerator[StreamDelta, None]:
        """Send messages to AI model and receive streaming response chunks"""
        options = await self._validate_request(options)
        
        payload = {
            "messages": [msg.to_dict() for msg in messages],
            **options.to_dict()
        }
        payload["stream"] = True
        
        response = await self.http_client.request("POST", "/chat/v1", payload)
        parser = StreamParser()
        
        try:
            async for chunk in response.content:
                chunk_str = chunk.decode('utf-8')
                deltas = parser.parse_chunk(chunk_str)
                
                for delta in deltas:
                    yield delta
                    if delta.type == "end":
                        return
        finally:
            response.close()
    
    async def generate(self, prompt: str, model: str = "lumi-o1") -> str:
        """Generate simple text response from a prompt"""
        messages = [Message(role="user", content=prompt)]
        options = ChatOptions(model=model)
        response = await self.chat(messages, options)
        return response.content
    
    async def generateWithReasoning(
        self, 
        prompt: str, 
        effort: str = "medium",
        model: str = "lumi-o1-mini"
    ) -> Tuple[str, Optional[Dict]]:
        """Generate response with reasoning process included"""
        messages = [Message(role="user", content=prompt)]
        reasoning = ReasoningConfig(enabled=True, effort=effort)
        options = ChatOptions(model=model, reasoning=reasoning)
        
        response = await self.chat(messages, options)
        return response.content, response.reasoning_data
    
    def tokens(self, response: ChatResponse) -> Usage:
        """Extract token usage information from chat response"""
        return response.usage
    
    async def close(self):
        """Clean up HTTP connections and resources"""
        if self._http_client:
            await self._http_client.close()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

genai = LunaVerseXGenAI()