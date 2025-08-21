import re
import json
from typing import Any, Optional, List, Dict, Union
from dataclasses import dataclass

# 导入你现有的模块
from descartcan.llm.llm import LLM, ChatResponse
from descartcan.llm.mcp_client import MCPManager, MCPClient


@dataclass
class MCPCallResult:
    success: bool
    result: Any = None
    error: Optional[str] = None
    tool_name: Optional[str] = None
    server_name: Optional[str] = None


class MCPIntegratedLLM(LLM):
    def __init__(self):
        self.mcp_manager = MCPManager()
        self.auto_tool_calling = True

    async def add_mcp_server(self, name: str, server_url: str, transport: str = "http") -> MCPClient:
        """添加 MCP 服务器"""
        return await self.mcp_manager.add_server(name, server_url, transport)

    async def remove_mcp_server(self, name: str):
        """移除 MCP 服务器"""
        await self.mcp_manager.remove_server(name)

    def _generate_tools_prompt(self) -> str:
        """生成工具描述的提示词"""
        all_tools = self.mcp_manager.get_all_tools()
        if not all_tools:
            return ""

        tools_desc = "\n\n=== 可用工具 ===\n"
        for server_name, tools in all_tools.items():
            if tools:
                tools_desc += f"\n服务器: {server_name}\n"
                for tool in tools:
                    tools_desc += f"- {tool.name}: {tool.description}\n"
                    if tool.input_schema.get('properties'):
                        tools_desc += f"  参数: {list(tool.input_schema['properties'].keys())}\n"

        tools_desc += """
使用工具时，请按以下格式回复：
```mcp_call
{
    "server": "服务器名称",
    "tool": "工具名称", 
    "arguments": {
        "参数名": "参数值"
    },
    "reasoning": "使用此工具的原因"
}
```
"""
        return tools_desc

    def _extract_mcp_calls(self, text: str) -> List[Dict[str, Any]]:
        """从文本中提取 MCP 工具调用"""
        pattern = r'```mcp_call\s*\n(.*?)\n```'
        matches = re.findall(pattern, text, re.DOTALL)

        calls = []
        for match in matches:
            try:
                call_data = json.loads(match.strip())
                calls.append(call_data)
            except json.JSONDecodeError as e:
                print(f"Failed to parse MCP call: {e}")

        return calls

    async def _execute_mcp_call(self, call_data: Dict[str, Any]) -> MCPCallResult:
        """执行 MCP 工具调用"""
        try:
            server_name = call_data.get('server')
            tool_name = call_data.get('tool')
            arguments = call_data.get('arguments', {})

            if not server_name or not tool_name:
                return MCPCallResult(
                    success=False,
                    error="Missing server or tool name"
                )

            result = await self.mcp_manager.call_tool(server_name, tool_name, arguments)

            if 'error' in result:
                return MCPCallResult(
                    success=False,
                    error=result['error'],
                    tool_name=tool_name,
                    server_name=server_name
                )

            return MCPCallResult(
                success=True,
                result=result.get('result'),
                tool_name=tool_name,
                server_name=server_name
            )

        except Exception as e:
            return MCPCallResult(
                success=False,
                error=str(e),
                tool_name=call_data.get('tool'),
                server_name=call_data.get('server')
            )

    async def _process_with_tools(self, model: str, messages: List[Dict], max_iterations: int = 5, **kwargs) -> ChatResponse:
        """处理带工具调用的对话"""
        current_messages = messages.copy()

        # 添加工具描述到系统提示
        tools_prompt = self._generate_tools_prompt()
        if tools_prompt and current_messages and current_messages[0].get('role') == 'system':
            current_messages[0]['content'] += tools_prompt
        elif tools_prompt:
            current_messages.insert(0, {'role': 'system', 'content': tools_prompt})

        for iteration in range(max_iterations):
            # 获取模型响应
            response = await super()._execute_completion(model, current_messages, **kwargs)

            if not response.success:
                return response

            # 检查是否有工具调用
            mcp_calls = self._extract_mcp_calls(response.content)

            if not mcp_calls:
                # 没有工具调用，返回结果
                return response

            # 执行工具调用
            tool_results = []
            for call_data in mcp_calls:
                result = await self._execute_mcp_call(call_data)
                tool_results.append(result)

            # 构建工具结果消息
            current_messages.append({'role': 'assistant', 'content': response.content})

            results_text = "工具调用结果:\n"
            for i, result in enumerate(tool_results):
                call_data = mcp_calls[i]
                if result.success:
                    results_text += f"✅ {result.server_name}.{result.tool_name}: {result.result}\n"
                else:
                    results_text += f"❌ {result.server_name}.{result.tool_name}: {result.error}\n"

            current_messages.append({'role': 'user', 'content': results_text + "\n请根据工具调用结果继续回答。"})

        # 达到最大迭代次数
        final_response = await super()._execute_completion(model, current_messages, **kwargs)
        return final_response

    async def chat_with_mcp(self, model: str, messages: Union[str, List[Dict]],
                           system_prompt: Optional[str] = None,
                           enable_tools: bool = True,
                           max_tool_iterations: int = 5,
                           **kwargs) -> ChatResponse:
        """支持 MCP 工具调用的对话"""
        prepared_messages = self._prepare_messages(messages, system_prompt)

        if enable_tools and self.auto_tool_calling:
            return await self._process_with_tools(model, prepared_messages, max_tool_iterations, **kwargs)
        else:
            return await self._execute_completion(model, prepared_messages, **kwargs)

    async def ask_with_mcp(self, model: str, prompt: str,
                          system_prompt: Optional[str] = None,
                          enable_tools: bool = True,
                          **kwargs) -> ChatResponse:
        """支持 MCP 工具调用的问答"""
        return await self.chat_with_mcp(model, prompt, system_prompt, enable_tools, **kwargs)

    async def get_mcp_resource(self, server_name: str, uri: str) -> Dict[str, Any]:
        """获取 MCP 资源"""
        client = self.mcp_manager.get_client(server_name)
        if not client:
            raise ValueError(f"Server '{server_name}' not found")
        return await client.read_resource(uri)

    async def get_mcp_prompt(self, server_name: str, prompt_name: str,
                            arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """获取 MCP 提示"""
        client = self.mcp_manager.get_client(server_name)
        if not client:
            raise ValueError(f"Server '{server_name}' not found")
        return await client.get_prompt(prompt_name, arguments)

    def list_mcp_capabilities(self) -> Dict[str, Any]:
        """列出所有 MCP 能力"""
        capabilities = {
            'servers': list(self.mcp_manager.clients.keys()),
            'tools': {},
            'resources': {},
            'prompts': {}
        }

        for server_name, client in self.mcp_manager.clients.items():
            capabilities['tools'][server_name] = [
                {'name': tool.name, 'description': tool.description}
                for tool in client.get_available_tools()
            ]
            capabilities['resources'][server_name] = [
                {'uri': res.uri, 'name': res.name, 'description': res.description}
                for res in client.get_available_resources()
            ]
            capabilities['prompts'][server_name] = [
                {'name': prompt.name, 'description': prompt.description}
                for prompt in client.get_available_prompts()
            ]

        return capabilities

    async def cleanup(self):
        """清理资源"""
        await self.mcp_manager.disconnect_all()


async def main():
    llm = MCPIntegratedLLM()

    # 添加 MCP 服务器
    try:
        # 添加文件系统 MCP 服务器
        await llm.add_mcp_server(
            "filesystem",
            "http://localhost:8000",
            "http"
        )

        # 添加数据库 MCP 服务器
        await llm.add_mcp_server(
            "database",
            "ws://localhost:8001",
            "websocket"
        )

        print("MCP servers connected successfully!")

        # 查看可用能力
        capabilities = llm.list_mcp_capabilities()
        print("Available capabilities:", capabilities)

        # 与 MCP 工具进行对话
        response = await llm.ask_with_mcp(
            model="litellm_proxy/aws_cs4",
            prompt="请帮我读取当前目录下的文件列表，然后分析这些文件的类型分布",
            system_prompt="你是一个文件管理助手，可以使用文件系统工具来帮助用户管理文件。",
            enable_tools=True
        )

        print("Response:", response.content)
        print("Tokens used:", response.total_tokens)

        # 直接调用工具
        tool_result = await llm.mcp_manager.call_tool(
            "filesystem",
            "list_directory",
            {"path": "."}
        )
        print("Tool result:", tool_result)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await llm.cleanup()



if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
