import pytest
from lunaversex-genai.models import (
    Message, FileAttachment, ChatOptions, ReasoningConfig,
    ToolFunction, Usage, Model, ModelsResponse
)

class TestMessage:
    def test_message_creation(self):
        msg = Message(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"
        assert msg.files == []
    
    def test_invalid_role_raises_error(self):
        with pytest.raises(ValueError):
            Message(role="invalid", content="Hello")
    
    def test_add_file(self):
        msg = Message(role="user", content="Test")
        msg.add_file("test.txt", "content", "text/plain")
        
        assert len(msg.files) == 1
        assert msg.files[0].name == "test.txt"
    
    def test_to_dict(self):
        msg = Message(role="user", content="Hello")
        data = msg.to_dict()
        
        assert data["role"] == "user"
        assert data["content"] == "Hello"

class TestFileAttachment:
    def test_file_creation(self):
        file = FileAttachment("test.py", "print('hello')", "text/python")
        assert file.name == "test.py"
        assert file.content == "print('hello')"
        assert file.mime_type == "text/python"
    
    def test_to_dict(self):
        file = FileAttachment("test.txt", "content")
        data = file.to_dict()
        
        expected = {"name": "test.txt", "content": "content", "mime_type": "text/plain"}
        assert data == expected

class TestReasoningConfig:
    def test_default_config(self):
        config = ReasoningConfig()
        assert config.enabled is True
        assert config.effort == "medium"
    
    def test_invalid_effort_raises_error(self):
        with pytest.raises(ValueError):
            ReasoningConfig(effort="invalid")
    
    def test_to_dict(self):
        config = ReasoningConfig(enabled=True, effort="high")
        data = config.to_dict()
        
        assert data == {"enabled": True, "effort": "high"}

class TestToolFunction:
    def test_tool_creation(self):
        tool = ToolFunction(
            name="test_func",
            description="Test function",
            parameters={"type": "object"}
        )
        assert tool.name == "test_func"
        assert tool.description == "Test function"
    
    def test_to_dict(self):
        tool = ToolFunction("test", "desc", {"type": "object"})
        data = tool.to_dict()
        
        assert data["type"] == "function"
        assert data["function"]["name"] == "test"

class TestChatOptions:
    def test_default_options(self):
        options = ChatOptions(model="lumi-o1")
        assert options.model == "lumi-o1"
        assert options.temperature == 1.0
        assert options.stream is False
    
    def test_to_dict_minimal(self):
        options = ChatOptions(model="lumi-o1")
        data = options.to_dict()
        
        assert data["model"] == "lumi-o1"
        assert data["temperature"] == 1.0
        assert "max_tokens" not in data
    
    def test_to_dict_with_tools(self):
        tool = ToolFunction("test", "desc", {})
        options = ChatOptions(model="lumi-o1", tools=[tool])
        data = options.to_dict()
        
        assert "tools" in data
        assert len(data["tools"]) == 1

class TestUsage:
    def test_usage_calculation(self):
        usage = Usage(input_tokens=10, output_tokens=5)
        assert usage.total_tokens == 15
    
    def test_usage_with_all_tokens(self):
        usage = Usage(
            input_tokens=10,
            output_tokens=5,
            system_tokens=2,
            reasoning_tokens=3
        )
        assert usage.total_tokens == 20

class TestModel:
    def test_model_creation(self):
        model = Model(id="lumi-o1", name="Lumi o1")
        assert model.id == "lumi-o1"
        assert model.name == "Lumi o1"
        assert model.supports_tools is True
    
    def test_from_api(self):
        api_data = {
            "id": "lumi-o1",
            "name": "Lumi o1",
            "supportsReasoning": True,
            "maxTokens": 8192
        }
        
        model = Model.from_api(api_data)
        assert model.id == "lumi-o1"
        assert model.supports_reasoning is True
        assert model.max_tokens == 8192

class TestModelsResponse:
    def test_get_model(self):
        models = [
            Model("lumi-o1", "Lumi o1"),
            Model("lumi-o1-mini", "Lumi o1 Mini")
        ]
        response = ModelsResponse(models, "free", {})
        
        model = response.get_model("lumi-o1")
        assert model is not None
        assert model.id == "lumi-o1"
    
    def test_get_reasoning_models(self):
        models = [
            Model("lumi-o1", "Lumi o1", supports_reasoning=False),
            Model("lumi-o1-mini", "Lumi o1 Mini", supports_reasoning=True),
            Model("lumi-o3", "Lumi o3", has_native_reasoning=True)
        ]
        response = ModelsResponse(models, "free", {})
        
        reasoning_models = response.get_reasoning_models()
        assert len(reasoning_models) == 2