from typing import Literal, Union, List, Dict, Any

Provider = Literal['openai', 'anthropic']
Mode = Literal['test', 'live']
Role = Literal['system', 'user', 'assistant']

TextPart = Dict[str, str]  # { type: 'text', text: string }
PointerPart = Dict[str, str]  # { type: 'pointer', blob_id: string }
MessagePart = Union[TextPart, PointerPart]

Message = Dict[str, Union[Role, str, List[MessagePart]]]  # { role: Role, content: string | MessagePart[] }

class ChatRequest:
    def __init__(self, provider: Provider, model: str, messages: List[Message]):
        self.provider = provider
        self.model = model
        self.messages = messages

class SkimlyMeta:
    def __init__(self, provider: Provider, mode: Mode, tokens_saved: int = None, **kwargs):
        self.provider = provider
        self.mode = mode
        self.tokens_saved = tokens_saved
        for key, value in kwargs.items():
            setattr(self, key, value)

class ChatResponse:
    def __init__(self, id: str = None, choices: Any = None, skimly: SkimlyMeta = None, **kwargs):
        self.id = id
        self.choices = choices
        self.skimly = skimly
        for key, value in kwargs.items():
            setattr(self, key, value)

class BlobCreateRequest:
    def __init__(self, content: str, mime_type: str = "text/plain"):
        self.content = content
        self.mime_type = mime_type

class BlobCreateResponse:
    def __init__(self, blob_id: str):
        self.blob_id = blob_id
