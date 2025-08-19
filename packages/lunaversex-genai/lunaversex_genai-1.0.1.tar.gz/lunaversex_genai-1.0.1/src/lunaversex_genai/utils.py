import json
import time
import asyncio
import logging
from functools import wraps
from typing import Optional, List, Callable, Awaitable
from .models import Model, Usage, StreamDelta
from .exceptions import APIError

class TextProcessor:
    @staticmethod
    def clean_text(text: str) -> str:
        if not text or not isinstance(text, str):
            return ""
        return text.replace("::OPENROUTER PROCESSING", "").replace(": OPENROUTER PROCESSING", "").strip()

class ModelCache:
    def __init__(self, ttl: int = 300):
        self.ttl = ttl
        self._models: Optional[List[Model]] = None
        self._last_update: Optional[float] = None
        self._lock = asyncio.Lock()
    
    @property
    def is_expired(self) -> bool:
        return self._last_update is None or time.time() - self._last_update > self.ttl
    
    async def get_models(self, fetcher: Callable[[], Awaitable]) -> List[Model]:
        async with self._lock:
            if self.is_expired:
                try:
                    self._models = await fetcher()
                    self._last_update = time.time()
                except Exception:
                    if self._models is None:
                        self._set_fallback()
            
            return self._models or []
    
    def _set_fallback(self):
        self._models = [
            Model("lumi-o1", "Lumi o1", False, True, True),
            Model("lumi-o1-mini", "Lumi o1 Mini", True, True, True),
            Model("lumi-o1-pro", "Lumi o1 Pro", False, False, True),
            Model("lumi-o1-high", "Lumi o1 High", True, True),
            Model("lumi-o3", "Lumi o3", False, True, has_native_reasoning=True)
        ]
    
    def is_valid_model(self, model_id: str) -> bool:
        if self._models is None:
            return model_id in ["lumi-o1", "lumi-o1-mini", "lumi-o1-pro", "lumi-o1-high", "lumi-o3"]
        return any(m.id == model_id for m in self._models)
    
    def get_model(self, model_id: str) -> Optional[Model]:
        if self._models is None:
            self._set_fallback()
        return next((m for m in self._models if m.id == model_id), None)

class StreamParser:
    def __init__(self):
        self.buffer = ""
        self.final_usage: Optional[Usage] = None
    
    def parse_chunk(self, chunk: str) -> List[StreamDelta]:
        self.buffer += chunk
        lines = self.buffer.split('\n')
        self.buffer = lines.pop()
        
        deltas = []
        for line in lines:
            delta = self._parse_line(line)
            if delta:
                deltas.append(delta)
        
        return deltas
    
    def _parse_line(self, line: str) -> Optional[StreamDelta]:
        line = line.strip()
        
        if not line or line.startswith(':') or 'OPENROUTER PROCESSING' in line:
            return None
        
        if not line.startswith("data: "):
            return None
        
        data_str = line[6:].strip()
        
        if data_str == "[DONE]":
            return StreamDelta(type="end", usage=self.final_usage)
        
        try:
            data = json.loads(data_str)
            
            if data.get("usage"):
                usage_data = data["usage"]
                self.final_usage = Usage(
                    input_tokens=usage_data.get("prompt_tokens", 0),
                    output_tokens=usage_data.get("completion_tokens", 0),
                    system_tokens=usage_data.get("system_tokens", 0),
                    reasoning_tokens=usage_data.get("reasoning_tokens", 0)
                )
            
            choices = data.get("choices", [])
            if not choices:
                return None
            
            choice = choices[0]
            
            if choice.get("finish_reason"):
                return StreamDelta(
                    type="end",
                    usage=self.final_usage,
                    finish_reason=choice["finish_reason"]
                )
            
            delta = choice.get("delta", {})
            
            if delta.get("content") or delta.get("reasoning") or delta.get("tool_calls"):
                return StreamDelta(
                    type="delta",
                    content=TextProcessor.clean_text(delta.get("content", "")),
                    reasoning=delta.get("reasoning"),
                    tool_calls=delta.get("tool_calls")
                )
            
        except json.JSONDecodeError:
            return None
        
        return None

def retry_async(max_retries: int = 3, delay: float = 1.0):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except (APIError, Exception) as e:
                    last_exception = e
                    if attempt < max_retries and isinstance(e, APIError):
                        await asyncio.sleep(delay * (2 ** attempt))
                        continue
                    break
            
            raise last_exception
        return wrapper
    return decorator