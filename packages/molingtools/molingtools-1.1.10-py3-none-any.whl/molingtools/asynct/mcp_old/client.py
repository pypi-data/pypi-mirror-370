from pydantic import BaseModel
import json
import warnings
try:
    from mcp import ClientSession, StdioServerParameters
    from openai import AsyncOpenAI
except ModuleNotFoundError:
    raise ModuleNotFoundError('pip install mcp openai')
from typing import AsyncIterator
# from dotenv import load_dotenv
from contextlib import AsyncExitStack
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client 
from openai.types.chat.chat_completion import ChatCompletion
from mcp.types import ListToolsResult

    
# 加载 .env 文件
# load_dotenv()

class MCPResult(BaseModel):
    role: str
    content: str
    tool_name: str|None = None
    tool_args: dict|list|None = None
    
class MCPClient:
    def __init__(self, base_url, model, api_key='EMPTY', prompts:list=(), **kwargs):
        self.exit_stack = AsyncExitStack()
        self.model = model
        self.kwargs=kwargs
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.server_session:dict[str, ClientSession] = {}  # 存储多个服务端会话
        self.messages = [{"role": "system", "content": prompt} for prompt in prompts]
        
    async def connect_to_server(self, server_name, session:ClientSession, debug_list_tools:bool=False):
        await session.initialize()
        self.server_session[server_name]=session
        # 更新工具映射
        response = await session.list_tools()
        if debug_list_tools:
            for tool in response.tools:
                print({"name": tool.name,
                        "description": tool.description,
                        "input_schema": tool.inputSchema})
        print(f"已连接到 MCP 服务器 {server_name}")
        
    async def connect_to_stdio_server(self, server_name:str, command:str, *args: str, env:dict=None, debug_list_tools=False):
        server_params = StdioServerParameters(command=command, args=args, env=env)
        read_stream, write_stream = await self.exit_stack.enter_async_context(stdio_client(server_params))
        session = await self.exit_stack.enter_async_context(ClientSession(read_stream, write_stream))
        return await self.connect_to_server(server_name, session, debug_list_tools=debug_list_tools)

    async def connect_to_sse_server(self, server_name:str, url:str, debug_list_tools=False):
        read_stream, write_stream = await self.exit_stack.enter_async_context(sse_client(url))
        session = await self.exit_stack.enter_async_context(ClientSession(read_stream, write_stream))
        return await self.connect_to_server(server_name, session, debug_list_tools=debug_list_tools)
    
    async def connect_to_config(self, config_or_path:dict|str, debug_list_tools=False):
        if isinstance(config_or_path, str):
            with open(config_or_path, encoding="utf-8") as f:
                config = json.load(f)
        else:
            config = config_or_path
        for server_name, server_config in config['mcpServers'].items():
            if server_config.get("command"):
                await self.connect_to_stdio_server(server_name, server_config["command"], *server_config.get("args",[]), 
                                                   env=server_config.get("env"), debug_list_tools=debug_list_tools)
            elif server_config.get("url"):
                await self.connect_to_sse_server(server_name, server_config["url"], debug_list_tools=debug_list_tools)
            else:
                warnings.warn(f"未指定command或url, 无法连接到 MCP 服务器 {server_name}")

    async def process_query(self, query: str, max_num=3)->AsyncIterator[MCPResult]:
        """调用大模型处理用户查询，并根据返回的 tools 列表调用对应工具。
        支持多次工具调用，直到所有工具调用完成。
        流式输出
        Args:
            query (str): 查询
            max_num (int, optional): 最大工具调用次数. Defaults to 3.
        Yields:
            str: 结果词语
        """
        self.messages.append({"role": "user", "content": query})
        # 构建统一的工具列表
        available_tools = []
        name_session = {}
        for server_name, session in self.server_session.items():
            tool_result:ListToolsResult = await session.list_tools()
            for tool in tool_result.tools:
                available_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "input_schema": tool.inputSchema
                        }
                    })
                name_session[tool.name] = session
        # 循环处理工具调用
        for _ in range(max_num):
            # 使用工具的请求无法进行流式输出
            response:ChatCompletion = await self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=available_tools,
                **self.kwargs,
                stream=False
            )
            content = response.choices[0].message.content
            self.messages.append({"role": "assistant", "content": content, 
                                  "tool_calls": response.choices[0].message.tool_calls})      
            # 处理返回的内容
            if response.choices[0].finish_reason == "tool_calls":
                # 执行工具调用
                for tool_call in response.choices[0].message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    yield MCPResult(role='assistant', content='正在使用工具...', 
                                    tool_name=tool_name, tool_args=tool_args)
                    # 根据工具名称找到对应的服务端
                    session:ClientSession = name_session[tool_name]
                    result = await session.call_tool(tool_name, tool_args)
                    # 将工具调用的结果添加到 messages 中
                    self.messages.append({
                        "role": "tool",
                        "name": tool_name,
                        "content": result.content[0].text,
                        "tool_call_id": tool_call.id,
                    })
                    yield MCPResult(role='tool',content=result.content[0].text, 
                                    tool_name=tool_name, tool_args=tool_args)
            else:
                yield MCPResult(role='assistant',content=content)
                break
        if not content: warnings.warn('已超出最大工具调用次数...')
        
    async def cleanup(self):
        await self.exit_stack.aclose()
        self.server_session.clear()