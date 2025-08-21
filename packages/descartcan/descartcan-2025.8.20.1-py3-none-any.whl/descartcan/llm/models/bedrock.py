import traceback
import random
import boto3
import time
from datetime import datetime
from typing import List, Dict, Optional, AsyncGenerator, Any
from anthropic import AnthropicBedrock
from descartcan.utils.log import logger
from descartcan.llm.models.base import BaseImplementStrategy
from descartcan.llm.strategy import (
    ModelConfig,
    ChatResponse,
    ModelMetrics,
    ChatStreamResponse,
    FunctionDefinition,
)


class BedrockStrategy(BaseImplementStrategy):
    def __init__(self, keys: Dict[str, Dict[str, str]], model_property: ModelConfig):
        super().__init__(keys, model_property)
        self._keys = keys
        self._client_pool = []
        self._last_refresh = datetime.min
        self._client_refresh_interval = 3600  # 1小时刷新一次
        self._sts_cache_duration = 3600
        self._refresh_clients()

    def base_url(self) -> str:
        return "https://bedrock-runtime.us-west-2.amazonaws.com"

    def get_name(self) -> str:
        return "bedrock"

    def _refresh_clients(self) -> None:
        if (
            datetime.now() - self._last_refresh
        ).seconds < self._client_refresh_interval:
            return

        try:
            self._client_pool = []
            for key_id, key_info in self._keys.items():
                sts_client = boto3.client(
                    "sts",
                    aws_access_key_id=key_info["api_key"],
                    aws_secret_access_key=key_info["api_secret"],
                )
                credentials = sts_client.get_session_token(
                    DurationSeconds=self._sts_cache_duration
                )["Credentials"]

                region = key_info.get("api_region", None)
                if not region:
                    region = "us-east-1"

                self._client_pool.append(
                    {
                        "name": region,
                        "client": AnthropicBedrock(
                            aws_access_key=credentials["AccessKeyId"],
                            aws_secret_key=credentials["SecretAccessKey"],
                            aws_session_token=credentials["SessionToken"],
                            aws_region=region,
                        ),
                    }
                )
            self._last_refresh = datetime.now()
        except Exception as e:
            logger.error(f"Failed to refresh Bedrock clients: {traceback.format_exc()}")

    def _get_client(self) -> Dict[str, AnthropicBedrock]:
        if not self._client_pool:
            self._refresh_clients()
            if not self._client_pool:
                raise Exception("No Bedrock client available")
        return random.choice(self._client_pool)

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
        **kwargs,
    ) -> ChatResponse:
        start_time_ms = int(time.monotonic() * 1000)
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
                top_p=request.top_p
            )
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            total_tokens = input_tokens + output_tokens

            finished_time_ms = int(time.monotonic() * 1000)
            metrics = ModelMetrics(
                latency=int((start_time_ms - finished_time_ms)/1000),
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
            finished_time_ms = int(time.monotonic() * 1000)
            metrics = ModelMetrics(
                latency=int((start_time_ms - finished_time_ms)/1000),
                tokens_used=0,
                success=False,
                timestamp=datetime.now(),
                error=str(e),
            )
            await self.record_metrics(metrics)
            logger.error(
                f"Bedrock生成错误\n模型: {self._property.name}"
                f"\n区域: {client_info['name']}\n错误: {traceback.format_exc()}"
            )
            await self.handle_error(e)

    async def chat_stream(
        self,
        question: str,
        system: Optional[str] = None,
        history: Optional[List[Dict]] = None,
        **kwargs,
    ) -> ChatStreamResponse:
        messages = self._gen_messages(question, system, history)
        token_usage = self.calculate_messages_token_count(messages)
        client_info = self._get_client()
        client = client_info["client"]
        request = self._create_chat_request(messages, stream=True, **kwargs)

        async def stream_content():
            start_time_ms = int(time.monotonic() * 1000)
            total_tokens = 0

            try:
                stream = client.messages.create(
                    model=self._property.name,
                    system=system,
                    messages=request.messages,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                    top_p=request.top_p,
                    stream=True,
                )

                for event in stream:
                    if event.type == "content_block_delta":
                        total_tokens += len(event.delta.text.split())
                        yield event.delta.text

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
                logger.error(
                    f"Bedrock流式生成错误\n模型: {self._property.name}"
                    f"\n区域: {client_info['name']}\n错误: {traceback.format_exc()}"
                )
                await self.handle_error(e)

        return ChatStreamResponse(
            content=stream_content(), prompt_tokens=token_usage.prompt_tokens
        )

    async def chat_with_functions(
        self,
        question: str,
        system: Optional[str] = None,
        history: Optional[List[Dict]] = None,
        functions: Optional[List[FunctionDefinition]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        raise NotImplementedError("该模型不支持函数调用")

    async def chat_stream_with_functions(
        self,
        question: str,
        system: Optional[str] = None,
        history: Optional[List[Dict]] = None,
        functions: Optional[List[FunctionDefinition]] = None,
        **kwargs,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        raise NotImplementedError("该模型不支持流式函数调用")
