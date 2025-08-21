import time
from dataclasses import dataclass
from typing import Dict, List, AsyncGenerator, Union, Optional
from litellm import acompletion


@dataclass
class ChatResponse:
    content: str
    input_token_count: int
    output_token_count: int
    elapsed_time_ms: int = 0
    error: Optional[str] = None
    model: Optional[str] = None
    finish_reason: Optional[str] = None

    @property
    def total_tokens(self) -> int:
        return self.input_token_count + self.output_token_count

    @property
    def success(self) -> bool:
        return self.error is None


class ChatStreamResponse:
    def __init__(self, content_generator: AsyncGenerator[str, None], model: str = None):
        self.content_generator = content_generator
        self.input_token_count = 0
        self.output_token_count = 0
        self.full_content = ""
        self.model = model
        self.finish_reason = None

    async def __aiter__(self):
        async for chunk in self.content_generator:
            if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                self.full_content += content
                yield content

    async def collect(self) -> str:
        async for _ in self:
            pass
        return self.full_content


class LLM:
    @staticmethod
    def _extract_token_usage(response) -> tuple:
        if hasattr(response, 'usage') and response.usage:
            input_tokens = getattr(response.usage, 'prompt_tokens', 0)
            output_tokens = getattr(response.usage, 'completion_tokens', 0)
        else:
            input_tokens = output_tokens = 0
        return input_tokens, output_tokens

    @staticmethod
    def _prepare_messages(messages: Union[str, List[Dict]], system_prompt: Optional[str] = None) -> List[Dict]:
        if isinstance(messages, str):
            msg_list = []
            if system_prompt:
                msg_list.append({"role": "system", "content": system_prompt})
            msg_list.append({"role": "user", "content": messages})
            return msg_list

        if system_prompt and not any(msg.get("role") == "system" for msg in messages):
            return [{"role": "system", "content": system_prompt}] + messages

        return messages

    @staticmethod
    async def _execute_completion(model: str, messages: List[Dict], **kwargs) -> ChatResponse:
        start_time = time.time()

        try:
            response = await acompletion(
                model=model,
                messages=messages,
                **kwargs
            )

            elapsed_ms = int((time.time() - start_time) * 1000)
            input_tokens, output_tokens = LLM._extract_token_usage(response)

            return ChatResponse(
                content=response.choices[0].message.content,
                input_token_count=input_tokens,
                output_token_count=output_tokens,
                elapsed_time_ms=elapsed_ms,
                model=model,
                finish_reason=getattr(response.choices[0], 'finish_reason', None)
            )

        except Exception as e:
            elapsed_ms = int((time.time() - start_time) * 1000)
            return ChatResponse(
                content="",
                input_token_count=0,
                output_token_count=0,
                elapsed_time_ms=elapsed_ms,
                error=str(e),
                model=model
            )

    @staticmethod
    async def ask(model: str, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> ChatResponse:
        messages = LLM._prepare_messages(prompt, system_prompt)
        return await LLM._execute_completion(model, messages, **kwargs)

    @staticmethod
    async def chat(model: str, messages: Union[str, List[Dict]], system_prompt: Optional[str] = None,
                   **kwargs) -> ChatResponse:
        messages = LLM._prepare_messages(messages, system_prompt)
        return await LLM._execute_completion(model, messages, **kwargs)

    @staticmethod
    async def stream(model: str, messages: Union[str, List[Dict]], system_prompt: Optional[str] = None,
                     **kwargs) -> ChatStreamResponse:
        messages = LLM._prepare_messages(messages, system_prompt)

        async def content_generator():
            try:
                stream = await acompletion(
                    model=model,
                    messages=messages,
                    stream=True,
                    **kwargs
                )
                async for chunk in stream:
                    yield chunk
            except Exception as e:
                print(f"Stream error: {e}")

        return ChatStreamResponse(content_generator(), model)

    @staticmethod
    async def quick_ask(model: str, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        response = await LLM.ask(model, prompt, system_prompt, **kwargs)
        return response.content if response.success else ""

    @staticmethod
    async def quick_chat(model: str, messages: Union[str, List[Dict]], system_prompt: Optional[str] = None,
                         **kwargs) -> str:
        response = await LLM.chat(model, messages, system_prompt, **kwargs)
        return response.content if response.success else ""

    @staticmethod
    async def quick_stream(model: str, messages: Union[str, List[Dict]], system_prompt: Optional[str] = None,
                           **kwargs) -> AsyncGenerator[str, None]:
        messages = LLM._prepare_messages(messages, system_prompt)

        try:
            stream = await acompletion(
                model=model,
                messages=messages,
                stream=True,
                **kwargs
            )
            async for chunk in stream:
                if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            print(f"Stream error: {e}")

    @staticmethod
    async def ask_with_role(model: str, prompt: str, role: str, **kwargs) -> ChatResponse:
        return await LLM.ask(model, prompt, system_prompt=role, **kwargs)

    @staticmethod
    async def translate(model: str, text: str, target_lang: str = "中文", **kwargs) -> ChatResponse:
        system_prompt = f"你是一个专业的翻译助手，请将用户输入的文本翻译成{target_lang}，只返回翻译结果。"
        return await LLM.ask(model, text, system_prompt=system_prompt, **kwargs)

    @staticmethod
    async def summarize(model: str, text: str, **kwargs) -> ChatResponse:
        system_prompt = "你是一个专业的文本总结助手，请对用户提供的文本进行简洁准确的总结。"
        return await LLM.ask(model, text, system_prompt=system_prompt, **kwargs)

    @staticmethod
    async def code_review(model: str, code: str, language: str = "Python", **kwargs) -> ChatResponse:
        system_prompt = f"你是一个专业的{language}代码审查专家，请对用户提供的代码进行审查，指出潜在问题并给出改进建议。"
        return await LLM.ask(model, code, system_prompt=system_prompt, **kwargs)


class MessageBuilder:
    @staticmethod
    def create_message(role: str, content: str) -> Dict:
        return {"role": role, "content": content}

    @staticmethod
    def user(content: str) -> Dict:
        return {"role": "user", "content": content}

    @staticmethod
    def assistant(content: str) -> Dict:
        return {"role": "assistant", "content": content}

    @staticmethod
    def system(content: str) -> Dict:
        return {"role": "system", "content": content}

    @staticmethod
    def build_conversation(system_prompt: Optional[str] = None, *exchanges) -> List[Dict]:
        messages = []

        if system_prompt:
            messages.append(MessageBuilder.system(system_prompt))

        for exchange in exchanges:
            if len(exchange) >= 1 and exchange[0]:
                messages.append(MessageBuilder.user(exchange[0]))
            if len(exchange) >= 2 and exchange[1]:
                messages.append(MessageBuilder.assistant(exchange[1]))

        return messages

    @staticmethod
    def add_message(messages: List[Dict], role: str, content: str) -> List[Dict]:
        return messages + [MessageBuilder.create_message(role, content)]


async def example_usage():
    model = "litellm_proxy/aws_cs4"

    import os
    # os.environ["LITELLM_PROXY_API_KEY"] = "sk-"
    # os.environ["LITELLM_PROXY_API_BASE"] = "https://"

    response = await LLM.ask(model, "你好", system_prompt="你是一个友好的助手", temperature=0.7)
    print(f"回答: {response.content}")
    print(f"用时: {response.elapsed_time_ms}ms")
    print(f"Token: {response.total_tokens}")

    messages = MessageBuilder.build_conversation(
        "你是一个helpful的助手",
        ("什么是Python?", "Python是一种编程语言..."),
        ("它有什么特点?", None)
    )

    chat_response = await LLM.chat(model, messages, temperature=0.5)
    print(f"对话回答: {chat_response.content}")

    print("流式输出:")
    async for content in LLM.quick_stream(model, "请写一首关于春天的诗", system_prompt="你是一个诗人"):
        print(content, end="", flush=True)
    print()

    quick_answer = await LLM.quick_ask(model, "1+1等于几?")
    print(f"快速回答: {quick_answer}")

    translation = await LLM.translate(model, "Hello World")
    print(f"翻译结果: {translation.content}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(example_usage())
