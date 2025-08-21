import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
import httpx
import websockets
from contextlib import asynccontextmanager
from descartcan.utils.log import logger


@dataclass
class MCPTool:
    name: str
    description: str
    input_schema: Dict[str, Any]


@dataclass
class MCPResource:
    uri: str
    name: str
    description: Optional[str] = None
    mime_type: Optional[str] = None


@dataclass
class MCPPrompt:
    name: str
    description: str
    arguments: Optional[List[Dict[str, Any]]] = None


class MCPClient:
    def __init__(self, server_url: str, transport: str = "http"):
        """
        MCP 客户端

        Args:
            server_url: MCP 服务器地址
            transport: 传输协议 ('http' 或 'websocket')
        """
        self.server_url = server_url
        self.transport = transport
        self.session: Optional[httpx.AsyncClient] = None
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.tools: Dict[str, MCPTool] = {}
        self.resources: Dict[str, MCPResource] = {}
        self.prompts: Dict[str, MCPPrompt] = {}
        self.connected = False

    async def connect(self, timeout=30):
        """连接到 MCP 服务器"""
        try:
            if self.transport == "http":
                self.session = httpx.AsyncClient(timeout=timeout)
                # 初始化握手
                response = await self.session.post(
                    f"{self.server_url}/initialize",
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "initialize",
                        "params": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {
                                "tools": {},
                                "resources": {},
                                "prompts": {}
                            },
                            "clientInfo": {
                                "name": "LLM-MCP-Client",
                                "version": "1.0.0"
                            }
                        }
                    }
                )
                response.raise_for_status()

            elif self.transport == "websocket":
                self.websocket = await websockets.connect(self.server_url)
                # WebSocket 初始化
                await self.websocket.send(json.dumps({
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {},
                            "resources": {},
                            "prompts": {}
                        },
                        "clientInfo": {
                            "name": "LLM-MCP-Client",
                            "version": "1.0.0"
                        }
                    }
                }))

                response = await self.websocket.recv()
                init_response = json.loads(response)
                logger.info(f"MCP Server initialized: {init_response}")

            self.connected = True
            await self._discover_capabilities()
            logger.info(f"Connected to MCP server: {self.server_url}")

        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            raise

    async def disconnect(self):
        """断开连接"""
        if self.session:
            await self.session.aclose()
        if self.websocket:
            await self.websocket.close()
        self.connected = False

    async def _discover_capabilities(self):
        """发现服务器能力"""
        # 获取可用工具
        tools_response = await self._send_request("tools/list", {})
        if tools_response and "result" in tools_response:
            for tool_info in tools_response["result"].get("tools", []):
                tool = MCPTool(
                    name=tool_info["name"],
                    description=tool_info["description"],
                    input_schema=tool_info["inputSchema"]
                )
                self.tools[tool.name] = tool

        # 获取可用资源
        resources_response = await self._send_request("resources/list", {})
        if resources_response and "result" in resources_response:
            for resource_info in resources_response["result"].get("resources", []):
                resource = MCPResource(
                    uri=resource_info["uri"],
                    name=resource_info["name"],
                    description=resource_info.get("description"),
                    mime_type=resource_info.get("mimeType")
                )
                self.resources[resource.uri] = resource

        # 获取可用提示
        prompts_response = await self._send_request("prompts/list", {})
        if prompts_response and "result" in prompts_response:
            for prompt_info in prompts_response["result"].get("prompts", []):
                prompt = MCPPrompt(
                    name=prompt_info["name"],
                    description=prompt_info["description"],
                    arguments=prompt_info.get("arguments")
                )
                self.prompts[prompt.name] = prompt

        logger.info(f"Discovered {len(self.tools)} tools, {len(self.resources)} resources, {len(self.prompts)} prompts")

    async def _send_request(self, method: str, params: Dict[str, Any], request_id: int = None) -> Dict[str, Any]:
        """发送 JSON-RPC 请求"""
        if not self.connected:
            raise RuntimeError("Not connected to MCP server")

        request_id = request_id or int(asyncio.get_event_loop().time() * 1000)
        request = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params
        }

        try:
            if self.transport == "http":
                response = await self.session.post(
                    f"{self.server_url}/message",
                    json=request
                )
                response.raise_for_status()
                return response.json()

            elif self.transport == "websocket":
                await self.websocket.send(json.dumps(request))
                response = await self.websocket.recv()
                return json.loads(response)

        except Exception as e:
            logger.error(f"Request failed: {e}")
            return {"error": str(e)}

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """调用 MCP 工具"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found")

        response = await self._send_request("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })

        return response

    async def read_resource(self, uri: str) -> Dict[str, Any]:
        """读取 MCP 资源"""
        response = await self._send_request("resources/read", {
            "uri": uri
        })
        return response

    async def get_prompt(self, name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """获取 MCP 提示"""
        params = {"name": name}
        if arguments:
            params["arguments"] = arguments

        response = await self._send_request("prompts/get", params)
        return response

    def get_available_tools(self) -> List[MCPTool]:
        """获取可用工具列表"""
        return list(self.tools.values())

    def get_available_resources(self) -> List[MCPResource]:
        """获取可用资源列表"""
        return list(self.resources.values())

    def get_available_prompts(self) -> List[MCPPrompt]:
        """获取可用提示列表"""
        return list(self.prompts.values())


class MCPManager:
    """MCP 服务器管理器，支持多个 MCP 服务器"""

    def __init__(self):
        self.clients: Dict[str, MCPClient] = {}

    async def add_server(self, name: str, server_url: str, transport: str = "http") -> MCPClient:
        """添加 MCP 服务器"""
        client = MCPClient(server_url, transport)
        await client.connect()
        self.clients[name] = client
        return client

    async def remove_server(self, name: str):
        """移除 MCP 服务器"""
        if name in self.clients:
            await self.clients[name].disconnect()
            del self.clients[name]

    async def disconnect_all(self):
        """断开所有连接"""
        for client in self.clients.values():
            await client.disconnect()
        self.clients.clear()

    def get_client(self, name: str) -> Optional[MCPClient]:
        """获取指定的客户端"""
        return self.clients.get(name)

    def get_all_tools(self) -> Dict[str, List[MCPTool]]:
        """获取所有服务器的工具"""
        all_tools = {}
        for name, client in self.clients.items():
            all_tools[name] = client.get_available_tools()
        return all_tools

    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """调用指定服务器的工具"""
        client = self.get_client(server_name)
        if not client:
            raise ValueError(f"Server '{server_name}' not found")
        return await client.call_tool(tool_name, arguments)
