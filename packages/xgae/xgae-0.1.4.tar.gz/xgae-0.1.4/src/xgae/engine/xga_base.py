from typing import Union, Optional, Dict, List, Any, Literal, TypedDict
from dataclasses import dataclass
from abc import ABC, abstractmethod

class XGAError(Exception):
    """Custom exception for errors in the XGA system."""
    pass


class XGAContextMsg(TypedDict, total=False):
    type: Literal["user", "status",  "tool", "assistant", "assistant_response_end"]
    content: Union[Dict[str, Any], List[Any], str]
    is_llm_message: bool
    metadata: Dict[str, Any]
    message_id: str
    session_id: str
    agent_id: str
    task_id: str
    task_run_id: str
    trace_id: str

class XGAResponseMsg(TypedDict, total=False):
    type: Literal["content", "status"]
    content: Union[Dict[str, Any], List[Any], str]
    status: Literal["error", "status"]
    message: str

@dataclass
class XGAToolSchema:
    tool_name: str
    server_name: str
    description: str
    input_schema: Dict[str, Any]
    metadata: Optional[Dict[str, Any]]


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
    def get_task_tool_names(self, task_id: str) -> List[str]:
        pass

    @abstractmethod
    async def call_tool(self, task_id: str, tool_name: str, args: Optional[Dict[str, Any]] = None) -> XGAToolResult:
        pass
