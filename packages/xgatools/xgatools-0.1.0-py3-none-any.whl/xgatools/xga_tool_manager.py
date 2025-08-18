import xgatools.dyatona
#import xgatools.e2b
import xgatools.non_sandbox
import inspect

from typing import Literal, Any, Dict, Type, Callable

from xgatools.dyatona.sandbox_helper import DyaSandboxHelper
from xgatools.tool_base import XGATool

from xgatools.tool_base import XGASandBoxTool

SANDBOX_TOOL_CLASS_NAME = {
    "web_search": "WebSearchTool",
}

NO_SANDBOX_TOOL_CLASS_NAME = {
    "complete": "MessageTool"
}

class XGAToolManager:
    def __init__(self, sandbox_type: Literal["daytona", "e2b"] = "daytona") -> None:
        self.sandbox_type = sandbox_type
        self.task_sandbox_map: Dict[str, str] = {}
        self.sandbox_helper = None
        if sandbox_type == "daytona":
            self.sandbox_helper = DyaSandboxHelper()

    async def call(self, task_id: str, tool_name: str, args: Dict[str, Any]= {}) -> Any:
        tool_func = self.get_tool_function(task_id, tool_name)
        args = args if args else {}

        result = None
        if tool_func:
            if inspect.iscoroutinefunction(tool_func):
                result =  await tool_func(**args)
            else:
                result = tool_func(**args)

        return result

    def end_task(self, task_id: str) -> None:
        sandbox_id = self.task_sandbox_map.pop(task_id, None)
        if sandbox_id is None:
            print(f"Sandbox no start, task_id: {task_id}")

        # @todo kill sandbox
        if self.sandbox_type == "daytona":
            self.sandbox_helper.delete_sandbox(sandbox_id)
        elif self.sandbox_type == "e2b":
            pass

    def get_tool_function(self, task_id: str, tool_name: str) -> Callable | None:
        tool_class = self.get_tool_class(tool_name)

        tool_instance = None
        if tool_class and issubclass(tool_class, XGASandBoxTool):
            sandbox_id = self.task_sandbox_map.get(task_id)
            # @todo get real sandbox
            tool_instance = tool_class(sandbox=sandbox_id)
        elif tool_class and issubclass(tool_class, XGATool):
            tool_instance = tool_class()

        tool_func = None
        if tool_instance:
            tool_func = getattr(tool_instance, tool_name)

        return tool_func

    def get_tool_class(self, tool_name: str) -> Type[XGATool] | Type[XGASandBoxTool] | None:
        tool_class = None
        tool_class_name = SANDBOX_TOOL_CLASS_NAME.get(tool_name, None)
        if tool_class_name:
            if self.sandbox_type == "daytona":
                if tool_class_name in xgatools.dyatona.__all__:
                    tool_class = getattr(xgatools.dyatona, tool_class_name)
                    return tool_class
            elif self.sandbox_type == "e2b":
                pass #e2b

        tool_class_name = NO_SANDBOX_TOOL_CLASS_NAME.get(tool_name, None)
        if tool_class_name:
            if tool_class_name in xgatools.non_sandbox.__all__:
                tool_class = getattr(xgatools.non_sandbox, tool_class_name)
                return tool_class

        return tool_class


if __name__ == "__main__":
    import asyncio
    async def main() -> None:
        tool_manager = XGAToolManager()
        result = await tool_manager.call(task_id="task_123", tool_name="web_search", args={"query": "hello"})
        print(result)

        result = await tool_manager.call(task_id="task_123", tool_name="complete")
        print(result)

    asyncio.run(main())