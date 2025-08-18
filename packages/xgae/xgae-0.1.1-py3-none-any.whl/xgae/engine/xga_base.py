from typing import Union, Optional, Dict, List, Any, Literal
from dataclasses import dataclass
from abc import ABC, abstractmethod



@dataclass
class XGAMessage:
    message_id: str
    type: Literal["status",  "tool", "assistant", "assistant_response_end"]
    is_llm_message: bool
    content: Union[Dict[str, Any], List[Any], str]
    metadata: Optional[Dict[str, Any]]
    session_id: Optional[str]
    agent_id: Optional[str]
    task_id: Optional[str]

@dataclass
class XGAToolSchema:
    tool_name: str
    server_name: str
    description: str
    input_schema: Optional[str]


@dataclass
class XGAToolResult:
    success: bool
    output: str

class XGAToolBox(ABC):
    @abstractmethod
    async def creat_task_tool_box(self, task_id: str, general_tools: List[str], custom_tools: List[str]):
        pass

    @abstractmethod
    async def destroy_task_tool_box(self, task_id: str):
        pass

    @abstractmethod
    def get_task_tool_schemas(self, task_id: str, type: Literal["general_tool",  "custom_tool"]) -> List[XGAToolSchema]:
        pass

    @abstractmethod
    async def call_tool(self, task_id: str, tool_name: str, args: Optional[Dict[str, Any]] = None) -> XGAToolResult:
        pass
