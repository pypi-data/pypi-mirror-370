import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from lunaversex-genai import genai, Message, ChatOptions, ConfigurationError

@pytest.fixture
def mock_response():
    return {
        "id": "test-id",
        "model": "lumi-o1",
        "provider": "LunaVerseX",
        "choices": [{
            "message": {"role": "assistant", "content": "Test response"},
            "finish_reason": "stop",
            "index": 0
        }],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 5,
            "total_tokens": 15
        }
    }

@pytest.fixture
def setup_client():
    genai.init(api_key="test-key")
    yield
    asyncio.create_task(genai.close())

class TestClientInitialization:
    def test_init_with_valid_key(self):
        genai.init(api_key="test-key")
        assert genai._config.api_key == "test-key"
    
    def test_init_without_key_raises_error(self):
        with pytest.raises(ConfigurationError):
            genai.init(api_key="")

class TestChatMethods:
    @pytest.mark.asyncio
    async def test_chat_success(self, setup_client, mock_response):
        with patch.object(genai.http_client, 'request') as mock_request:
            mock_resp = AsyncMock()
            mock_resp.json.return_value = mock_response
            mock_request.return_value = mock_resp
            
            messages = [Message(role="user", content="Hello")]
            options = ChatOptions(model="lumi-o1")
            
            response = await genai.chat(messages, options)
            
            assert response.content == "Test response"
            assert response.usage.total_tokens == 15
    
    @pytest.mark.asyncio
    async def test_generate_simple(self, setup_client, mock_response):
        with patch.object(genai.http_client, 'request') as mock_request:
            mock_resp = AsyncMock()
            mock_resp.json.return_value = mock_response
            mock_request.return_value = mock_resp
            
            result = await genai.generate("Test prompt")
            assert result == "Test response"

class TestModelOperations:
    @pytest.mark.asyncio
    async def test_list_models(self, setup_client):
        mock_models_response = {
            "models": [
                {"id": "lumi-o1", "name": "Lumi o1", "supportsReasoning": False},
                {"id": "lumi-o1-mini", "name": "Lumi o1 Mini", "supportsReasoning": True}
            ],
            "plan": "free",
            "limits": {}
        }
        
        with patch.object(genai.http_client, 'request') as mock_request:
            mock_resp = AsyncMock()
            mock_resp.json.return_value = mock_models_response
            mock_request.return_value = mock_resp
            
            models = await genai.listModels()
            
            assert len(models.models) == 2
            assert models.models[0].id == "lumi-o1"

class TestStreamingChat:
    @pytest.mark.asyncio
    async def test_chat_stream(self, setup_client):
        mock_chunks = [
            b'data: {"choices":[{"delta":{"content":"Hello"}}]}\n\n',
            b'data: {"choices":[{"delta":{"content":" world"}}]}\n\n',
            b'data: [DONE]\n\n'
        ]
        
        with patch.object(genai.http_client, 'request') as mock_request:
            mock_resp = AsyncMock()
            mock_resp.content.__aiter__.return_value = mock_chunks
            mock_request.return_value = mock_resp
            
            messages = [Message(role="user", content="Hello")]
            options = ChatOptions(model="lumi-o1", stream=True)
            
            content = ""
            async for delta in genai.chatStream(messages, options):
                if delta.type == "delta" and delta.content:
                    content += delta.content
            
            assert content == "Hello world"

class TestErrorHandling:
    @pytest.mark.asyncio
    async def test_invalid_model_error(self, setup_client):
        with patch.object(genai._model_cache, 'is_valid_model', return_value=False):
            messages = [Message(role="user", content="Test")]
            options = ChatOptions(model="invalid-model")
            
            with pytest.raises(Exception):
                await genai.chat(messages, options)

class TestContextManager:
    @pytest.mark.asyncio
    async def test_context_manager_usage(self):
        genai.init(api_key="test-key")
        
        async with genai as client:
            assert client is genai