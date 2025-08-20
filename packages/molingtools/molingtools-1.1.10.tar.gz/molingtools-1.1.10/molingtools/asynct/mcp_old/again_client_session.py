from contextlib import AsyncExitStack
from typing import Any
from threading import Thread
try:
    from mcp import ClientSession, StdioServerParameters
except ModuleNotFoundError:
    raise ModuleNotFoundError('pip install mcp')
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client 
from mcp.server.fastmcp import FastMCP
from mcp.types import ListToolsResult, CallToolResult


class MCPAgainClientSession:
    """用于对mcp server方法的二次开发
    """
    def __init__(self, name=None):
        self.exit_stack = AsyncExitStack()
        self.server = FastMCP(name)
        self.session:ClientSession=None

    async def _connect_to_server(self, read_stream, write_stream):
        self.session = await self.exit_stack.enter_async_context(ClientSession(read_stream, write_stream))

    async def connect_to_stdio_server(self, command:str, *args: str, env:dict=None):
        server_params = StdioServerParameters(command=command, args=args, env=env)
        read_stream, write_stream = await self.exit_stack.enter_async_context(stdio_client(server_params))
        return await self._connect_to_server(read_stream, write_stream)

    async def connect_to_sse_server(self, url:str):
        read_stream, write_stream = await self.exit_stack.enter_async_context(sse_client(url))
        return await self._connect_to_server(read_stream, write_stream)
                    
    async def initialize(self):
        Thread(target=self.server.run, daemon=True).start()
        if self.session: await self.session.initialize()
    
    async def list_tools(self)->ListToolsResult:
        tools = await self.server.list_tools()
        self.hnames = [tool.name for tool in tools]
        if self.session:
            for tool in (await self.session.list_tools()).tools:
                if tool.name not in self.hnames:
                    tools.append(tool)
        retool = ListToolsResult(tools=tools)
        return retool
    
    async def call_tool(self, name: str, arguments: dict[str, Any] | None = None)->CallToolResult:
        if name in self.hnames:
            try:
                result = await self.server.call_tool(name, arguments)
                return CallToolResult(content=result)
            except:
                return CallToolResult(content=[], isError=True)
        else:
            return await self.session.call_tool(name, arguments)

    async def cleanup(self):
        await self.exit_stack.aclose()

    def extend(self, name: str|None = None, description: str|None = None):
        """用于给需要继承的方法进行注册
        """
        return self.server.tool(name=name,description=description)

    async def get_parent_result(self, name:str, arguments: dict[str, Any]|None = None, is_text=True):
        result = await self.session.call_tool(name, arguments)
        return result.content[0].text if is_text else result
    
# from test1 import MCPAgainClientSession
# from pydantic import Field

# @cer.extend(name='maps_direction_bicycling', description='用于测试描述')
# async def maps_direction_bicycling(a:str=Field(...,description="测试字段")):
#     content = cer.get_parent_result('maps_direction_bicycling', {'a':a})
#     pass

# await cer.connect_to_sse_server('')
