import httpx
import click
from mcp.server.fastmcp import FastMCP
from typing import Literal, Any, Dict, Optional

from .xga_tool_manager import XGAToolManager

class XGAMcpTools:
    mcp = FastMCP(name="Extreme General Agent Tools")
    sandbox_type: Literal["daytona", "e2b"] = "daytona"
    tool_manager :XGAToolManager = None

    def __init__(self, host: str, port: int, transport: Literal["stdio", "sse", "streamable-http"] = "sse", sandbox_type: Literal["daytona", "e2b"] = "daytona") -> None:
        self.transport = transport

        if transport != "stdio":
            XGAMcpTools.mcp.settings.host = host
            XGAMcpTools.mcp.settings.port = port

        XGAMcpTools.sandbox_type = sandbox_type
        XGAMcpTools.tool_manager = XGAToolManager(sandbox_type)

    def run(self):
        self.mcp.run(transport=self.transport)

    @mcp.tool()
    async def end_task(task_id: str) :
        print(f"end_task, task_id: {task_id}")
        XGAMcpTools.tool_manager.end_task(task_id)

    @mcp.tool()
    async def web_search(task_id: str, query: str) :
        print(f"Starting web search, task_id: {task_id}, query: {query}, sandbox_type={XGAMcpTools.sandbox_type}")
        return await XGAMcpTools.tool_manager.call(task_id, "web_search", {"query": query})

    @mcp.tool()
    async def complete(task_id: str) :
        print(f"Starting complete task_id: {task_id}")
        return await XGAMcpTools.tool_manager.call(task_id, "complete")


@click.command()
@click.option("--transport", type=click.Choice(["stdio", "sse", "streamable-http"]), default="sse", help="Transport type")
@click.option("--host", default="0.0.0.0", help="Host to listen on for MCP")
@click.option("--port", default=16060, help="Port to listen on for MCP")
@click.option("--sandbox_type", type=click.Choice(["daytona", "e2b"]), default="daytona", help="Sandbox type")
def main(transport: str, host: str, port: int, sandbox_type:str):
    xga_mcp_tools = XGAMcpTools(host, port, transport, sandbox_type)
    xga_mcp_tools.run()

if __name__ == "__main__":
    main()