import time
from datetime import datetime
from typing import List, Dict, Optional
import random
from openai import OpenAI
from descartcan.utils.log import logger
from descartcan.llm.strategy import (
    ModelStrategy,
    ModelMetrics,
    ChatResponse,
    ModelConfig,
    TokenUsage,
    ChatStreamResponse,
    ChatRequest,
)


class BaseStrategy(ModelStrategy):
    def base_url(self) -> str:
        pass

    def get_name(self) -> str:
        pass

    async def chat(self, question: str, system: Optional[str] = None, history: Optional[List[Dict]] = None,
                   **kwargs) -> ChatResponse:
        pass

    async def chat_stream(self, question: str, system: Optional[str] = None, history: Optional[List[Dict]] = None,
                          **kwargs) -> ChatStreamResponse:
        pass

    def __init__(self, keys: Dict[str, Dict[str, str]], model_property: ModelConfig):
        super().__init__(model_property)
        self._keys = keys
        self._client_pool = self._initialize_client_pool()

    def _initialize_client_pool(self):
        client_pool = []
        for key_id, key_info in self._keys.items():
            try:
                client = OpenAI(
                    api_key=key_info.get("api_key"),
                    base_url=self.base_url(),
                    organization=key_info.get("organization"),
                )
                client_pool.append(
                    {"client": client, "key_id": key_id, "info": key_info}
                )
            except Exception as e:
                logger.warning(
                    f"Failed to initialize client with key_id {key_id}: {str(e)}"
                )

        if not client_pool:
            logger.error("No clients were successfully initialized")

        return client_pool

    def _get_client(self):
        if not self._client_pool:
            raise Exception(f"No {self.get_name()} client available.")
        return random.choice(self._client_pool)

    def _gen_messages(
        self,
        question: str,
        system: Optional[str] = None,
        history: Optional[List[Dict]] = None,
    ) -> List[Dict[str, str]]:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        if history:
            messages.extend(history)
        if question:
            messages.append({"role": "user", "content": question})
        return messages

    def calculate_messages_token_count(
        self, messages: List[Dict[str, str]]
    ) -> TokenUsage:
        prompt_tokens = 0
        for message in messages:
            content = f"role:{message['role']} content:{message['content']}"
            prompt_tokens += self.calculate_token_count(content)
        return TokenUsage(prompt_tokens=prompt_tokens)

    def calculate_token_count(self, text: str) -> int:
        if self._encoding:
            return len(self._encoding.encode(text))
        return len(text)

    async def record_metrics(self, metrics: ModelMetrics):
        self._metrics_history.append(metrics)
        if len(self._metrics_history) > 1000:
            self._metrics_history = self._metrics_history[-1000:]

    async def handle_error(self, error: Exception) -> None:
        logger.error(f"Model error in {self.get_name()}: {str(error)}")
        raise error

    def _create_chat_request(
        self, messages: List[Dict[str, str]], stream: bool = False, **kwargs
    ) -> ChatRequest:
        return ChatRequest(
            messages=messages,
            temperature=kwargs.get("temperature", self._property.temperature),
            top_p=kwargs.get("top_p", self._property.top_p),
            max_tokens=kwargs.get("max_tokens", self._property.max_tokens),
            timeout=kwargs.get("timeout"),
            stream=stream,
            presence_penalty=kwargs.get(
                "presence_penalty", self._property.presence_penalty
            ),
            frequency_penalty=kwargs.get(
                "frequency_penalty", self._property.frequency_penalty
            ),
            stop=kwargs.get("stop", self._property.stop),
        )


class BaseImplementStrategy(BaseStrategy):
    """OpenAI API 兼容的基础策略类"""

    def get_name(self) -> str:
        pass

    def base_url(self) -> str:
        pass

    async def chat(
        self,
        question: str,
        system: Optional[str] = None,
        history: Optional[List[Dict]] = None,
        **kwargs,
    ) -> ChatResponse:
        client_info = self._get_client()
        client = client_info["client"]
        start_time_ms = int(time.monotonic() * 1000)
        try:
            messages = self._gen_messages(question, system, history)
            token_usage = self.calculate_messages_token_count(messages)
            request = self._create_chat_request(messages, stream=False, **kwargs)

            response = client.chat.completions.create(
                model=self._property.name,
                messages=request.messages,
                timeout=request.timeout,
                temperature=request.temperature,
                top_p=request.top_p,
                max_tokens=request.max_tokens,
                presence_penalty=request.presence_penalty,
                frequency_penalty=request.frequency_penalty,
                stop=request.stop,
            )

            finished_time_ms = int(time.monotonic() * 1000)
            metrics = ModelMetrics(
                latency=int((start_time_ms - finished_time_ms)/1000),
                tokens_used=response.usage.total_tokens,
                success=True,
                timestamp=datetime.now(),
            )
            await self.record_metrics(metrics)

            return ChatResponse(
                content=response.choices[0].message.content,
                prompt_tokens=token_usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens,
                elapsed_time_ms=finished_time_ms-start_time_ms
            )
        except Exception as e:
            finished_time_ms = int(time.monotonic() * 1000)
            metrics = ModelMetrics(
                latency=int((start_time_ms - finished_time_ms)/1000),
                tokens_used=0,
                success=False,
                timestamp=datetime.now(),
                error=str(e),
            )
            await self.record_metrics(metrics)
            await self.handle_error(e)

    async def chat_stream(
        self,
        question: str,
        system: Optional[str] = None,
        history: Optional[List[Dict]] = None,
        **kwargs,
    ) -> ChatStreamResponse:
        client_info = self._get_client()
        client = client_info["client"]
        messages = self._gen_messages(question, system, history)
        token_usage = self.calculate_messages_token_count(messages)
        request = self._create_chat_request(messages, stream=True, **kwargs)

        async def stream_content():
            start_time_ms = int(time.monotonic() * 1000)
            total_tokens = 0

            try:
                for part in client.chat.completions.create(
                    model=self._property.name,
                    messages=request.messages,
                    timeout=request.timeout,
                    temperature=request.temperature,
                    top_p=request.top_p,
                    max_tokens=request.max_tokens,
                    presence_penalty=request.presence_penalty,
                    frequency_penalty=request.frequency_penalty,
                    stop=request.stop,
                    stream=True,
                ):
                    if part.choices:
                        content = part.choices[0].delta.content
                        if content:
                            total_tokens += len(content)
                            yield content

                finished_time_ms = int(time.monotonic() * 1000)
                metrics = ModelMetrics(
                    latency=int((start_time_ms - finished_time_ms)/1000),
                    tokens_used=total_tokens,
                    success=True,
                    timestamp=datetime.now(),
                )
                await self.record_metrics(metrics)
            except Exception as e:
                finished_time_ms = int(time.monotonic() * 1000)
                metrics = ModelMetrics(
                    latency=int((start_time_ms - finished_time_ms)/1000),
                    tokens_used=total_tokens,
                    success=False,
                    timestamp=datetime.now(),
                    error=str(e),
                )
                await self.record_metrics(metrics)
                await self.handle_error(e)

        return ChatStreamResponse(
            content=stream_content(), prompt_tokens=token_usage.prompt_tokens
        )
