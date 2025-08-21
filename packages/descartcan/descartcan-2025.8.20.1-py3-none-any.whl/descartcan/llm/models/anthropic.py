import random
from anthropic import Anthropic
from typing import List, Dict, Optional
from datetime import datetime
from descartcan.llm.models.base import BaseImplementStrategy
from descartcan.llm.strategy import (
    ModelConfig,
    ChatResponse,
    ChatStreamResponse,
    ModelMetrics,
    ChatRequest,
)


class AnthropicStrategy(BaseImplementStrategy):
    def __init__(self, keys: Dict[str, Dict[str, str]], model_property: ModelConfig):
        super().__init__(keys, model_property)
        self._clients = {}

    def _get_client(self) -> Dict:
        """获取 Anthropic 客户端"""
        # 从可用的 key 中随机选择一个
        key_info = random.choice(list(self._keys.values()))
        key = key_info.get("key")

        # 如果该 key 已经创建了客户端，直接返回
        if key in self._clients:
            return {"client": self._clients[key], "key": key}

        # 创建新的客户端
        client = Anthropic(api_key=key)
        self._clients[key] = client

        return {"client": client, "key": key}

    def _gen_messages(
        self,
        question: str,
        system: Optional[str] = None,
        history: Optional[List[Dict]] = None,
    ) -> List[Dict[str, str]]:
        messages = []
        if history:
            messages.extend(history)
        if question:
            messages.append({"role": "user", "content": question})
        return messages

    async def chat(
        self,
        question: str,
        system: Optional[str] = None,
        history: Optional[List[Dict]] = None,
        **kwargs
    ) -> ChatResponse:
        start_time = datetime.now()
        client_info = self._get_client()
        client = client_info["client"]

        try:
            messages = self._gen_messages(question, system, history)
            request = self._create_chat_request(messages, stream=False, **kwargs)

            response = client.messages.create(
                model=self._property.name,
                messages=request.messages,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                top_p=request.top_p,
                presence_penalty=request.presence_penalty,
                frequency_penalty=request.frequency_penalty,
                stop=request.stop,
                timeout=request.timeout,
            )

            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            total_tokens = input_tokens + output_tokens

            metrics = ModelMetrics(
                latency=(datetime.now() - start_time).total_seconds(),
                tokens_used=total_tokens,
                success=True,
                timestamp=datetime.now(),
            )
            await self.record_metrics(metrics)

            return ChatResponse(
                content=response.content[0].text,
                prompt_tokens=input_tokens,
                completion_tokens=output_tokens,
                total_tokens=total_tokens,
            )
        except Exception as e:
            metrics = ModelMetrics(
                latency=(datetime.now() - start_time).total_seconds(),
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
        **kwargs
    ) -> ChatStreamResponse:
        messages = self._gen_messages(question, system, history)
        token_usage = self.calculate_messages_token_count(messages)
        client_info = self._get_client()
        client = client_info["client"]
        request = self._create_chat_request(messages, stream=True, **kwargs)

        async def stream_content():
            start_time = datetime.now()
            total_tokens = 0

            try:
                stream = client.messages.create(
                    model=self._property.name,
                    messages=request.messages,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                    top_p=request.top_p,
                    presence_penalty=request.presence_penalty,
                    frequency_penalty=request.frequency_penalty,
                    stop=request.stop,
                    timeout=request.timeout,
                    stream=True,
                )

                async for chunk in stream:
                    if chunk.content:
                        total_tokens += len(chunk.content[0].text)
                        yield chunk.content[0].text

                metrics = ModelMetrics(
                    latency=(datetime.now() - start_time).total_seconds(),
                    tokens_used=total_tokens,
                    success=True,
                    timestamp=datetime.now(),
                )
                await self.record_metrics(metrics)
            except Exception as e:
                metrics = ModelMetrics(
                    latency=(datetime.now() - start_time).total_seconds(),
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
