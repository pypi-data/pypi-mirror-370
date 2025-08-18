from xgatools.tool_base import XGASandBoxTool
from daytona_sdk import AsyncSandbox

class WebSearchTool(XGASandBoxTool):
    def __init__(self, sandbox: AsyncSandbox):
        super().__init__(sandbox)

    def web_search(self, query: str):
        return "noting to search" + query