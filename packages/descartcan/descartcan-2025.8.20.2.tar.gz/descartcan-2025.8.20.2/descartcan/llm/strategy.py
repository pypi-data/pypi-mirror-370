from abc import ABC, abstractmethod
from typing import Dict, List, Optional, AsyncGenerator, Any, Union, BinaryIO, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import asyncio
import tiktoken
from descartcan.utils.log import logger


@dataclass
class ChatResponse:
    content: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    elapsed_time_ms: int = 0


class ChatStreamResponse:
    def __init__(self, content: AsyncGenerator[str, None], prompt_tokens: int):
        self.content = content
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = 0

    async def __aiter__(self):
        async for chunk in self.content:
            self.completion_tokens += 1
            yield chunk

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


@dataclass
class ChatRequest:
    messages: List[Dict[str, str]]
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    max_tokens: Optional[int] = None
    timeout: Optional[float] = None
    stream: bool = False
    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None
    stop: Optional[List[str]] = None


@dataclass
class TokenUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


@dataclass
class ModelMetrics:
    latency: float
    tokens_used: int
    success: bool
    timestamp: datetime
    error: Optional[str] = None


@dataclass
class ModelConfig:
    temperature: float = 0.7
    top_p: float = 1.0
    max_tokens: Optional[int] = 20_000
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    stop: Optional[List[str]] = None


@dataclass
class FunctionDefinition:
    name: str
    description: str
    parameters: Dict[str, Any]
    required: List[str] = None


@dataclass
class ImageContent:
    url: Optional[str] = None
    base64: Optional[str] = None
    path: Optional[str] = None


class ModelStrategy(ABC):
    def __init__(self, model_property):
        self._property = model_property
        self._encoding_name = "cl100k_base"
        self._encoding = self._initialize_encoding()
        self._metrics_history: List[ModelMetrics] = []
        self._functions: Dict[str, FunctionDefinition] = {}
        self._function_handlers: Dict[str, Callable] = {}

    def _initialize_encoding(self):
        try:
            return tiktoken.get_encoding(self._encoding_name)
        except Exception as e:
            logger.error(f"Failed to initialize tiktoken encoding: {e}")
            return None

    @abstractmethod
    def base_url(self) -> str:
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    async def chat(
        self,
        question: str,
        system: Optional[str] = None,
        history: Optional[List[Dict]] = None,
        **kwargs,
    ) -> ChatResponse:
        pass

    @abstractmethod
    async def chat_stream(
        self,
        question: str,
        system: Optional[str] = None,
        history: Optional[List[Dict]] = None,
        **kwargs,
    ) -> ChatStreamResponse:
        pass
