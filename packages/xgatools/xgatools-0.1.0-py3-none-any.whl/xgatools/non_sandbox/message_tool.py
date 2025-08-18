from xgatools.tool_base import XGATool

from typing import Dict

class MessageTool(XGATool):
    def __init__(self) -> None:
        pass

    def complete(self) -> Dict[str, str]:
        return {"status": "complete"}