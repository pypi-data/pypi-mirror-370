
from typing import List, Any, Dict, Optional, AsyncGenerator
from uuid import uuid4

from xgae.engine.xga_base import XGAMessage, XGAToolSchema, XGAToolBox
from xgae.utils.llm_client import LLMClient
from xgae.utils.setup_env import langfuse
from xga_prompt_builder import XGAPromptBuilder
from xga_mcp_tool_box import XGAMcpToolBox

class XGAEngine():
    def __init__(self,
                 session_id: Optional[str] = None,
                 trace_id: Optional[str] = None,
                 agent_id: Optional[str] = None,
                 llm_config: Optional[Dict[str, Any]] = None,
                 prompt_builder: Optional[XGAPromptBuilder] = None,
                 tool_box: Optional[XGAToolBox] = None):
        self.session_id = session_id if session_id else f"xga_sid_{uuid4()}"
        self.agent_id = agent_id

        self.messages: List[XGAMessage] = []
        self.llm_client = LLMClient(llm_config)
        self.model_name = self.llm_client.model_name
        self.is_stream = self.llm_client.is_stream

        self.prompt_builder = prompt_builder or XGAPromptBuilder()
        self.tool_box = tool_box or XGAMcpToolBox()

        self.task_id = None
        self.trace_id = trace_id if trace_id else langfuse.create_trace_id()


    async def run_task(self,
                       task_messages: List[Dict[str, Any]],
                       task_id: Optional[str],
                       prompt_template: Optional[str] = None,
                       general_tools: Optional[List[str]] = ["*"],
                       custom_tools: Optional[List[str]] = []) -> AsyncGenerator:
        try:
            self.task_id = task_id if task_id else f"xga_task_{uuid4()}"
            await self.tool_box.creat_task_tool_box(self.task_id, general_tools, custom_tools)
            system_prompt = await self._build_system_prompt(prompt_template, general_tools, custom_tools)
            yield system_prompt

        finally:
            await self.tool_box.destroy_task_tool_box(self.task_id)
        

    def _run_task_once(self):
        pass

    async def _build_system_prompt(self, prompt_template: str, general_tools: List[str], custom_tools: List[str]) -> str:
        self.task_tool_schemas: Dict[str, XGAToolSchema] = {}
        system_prompt = self.prompt_builder.build_system_prompt(self.model_name, prompt_template)

        tool_schemas = await self.tool_box.get_task_tool_schemas(self.task_id, "general_tool")
        system_prompt = self.prompt_builder.build_general_tool_prompt(self.model_name, system_prompt, tool_schemas)

        tool_schemas = await self.tool_box.get_task_tool_schemas(self.task_id, "general_tool")
        system_prompt = self.prompt_builder.build_custom_tool_prompt(self.model_name, system_prompt, tool_schemas)

        return system_prompt

    def add_message(self, message: XGAMessage):
        message.message_id = f"xga_msg_{uuid4()}"
        message.session_id = self.session_id
        message.agent_id = self.agent_id
        self.messages.append(message)
