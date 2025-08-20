
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

    async def __async_init__(self) -> None:
        await  self.tool_box.load_mcp_tools_schema()

    @classmethod
    async def create(cls,
                     session_id: Optional[str] = None,
                     trace_id: Optional[str] = None,
                     agent_id: Optional[str] = None,
                     llm_config: Optional[Dict[str, Any]] = None,
                     prompt_builder: Optional[XGAPromptBuilder] = None,
                     tool_box: Optional[XGAToolBox] = None) -> 'XGAEngine' :
        engine: XGAEngine = cls(session_id=session_id,
                                trace_id=trace_id,
                                agent_id=agent_id,
                                llm_config=llm_config,
                                prompt_builder=prompt_builder,
                                tool_box=tool_box)

        await engine.__async_init__()
        return engine


    async def run_task(self,
                       task_messages: List[Dict[str, Any]],
                       task_id: Optional[str] = None,
                       system_prompt: Optional[str] = None,
                       general_tools: Optional[List[str]] = ["*"],
                       custom_tools: Optional[List[str]] = []) -> AsyncGenerator:
        try:
            self.task_id = task_id if task_id else f"xga_task_{uuid4()}"
            await self.tool_box.creat_task_tool_box(self.task_id, general_tools, custom_tools)
            task_prompt = self.build_task_prompt(system_prompt)
            yield task_prompt

        finally:
            await self.tool_box.destroy_task_tool_box(self.task_id)
        

    def _run_task_once(self):
        pass

    def build_task_prompt(self, system_prompt: Optional[str] = None) -> str:
        task_prompt = self.prompt_builder.build_system_prompt(self.model_name, system_prompt)

        tool_schemas =self.tool_box.get_task_tool_schemas(self.task_id, "general_tool")
        tool_prompt = self.prompt_builder.build_general_tool_prompt(tool_schemas)
        task_prompt = task_prompt + "\n" + tool_prompt

        tool_schemas = self.tool_box.get_task_tool_schemas(self.task_id, "custom_tool")
        tool_prompt = self.prompt_builder.build_custom_tool_prompt(tool_schemas)
        task_prompt = task_prompt + "\n" + tool_prompt

        return task_prompt

    def add_message(self, message: XGAMessage):
        message.message_id = f"xga_msg_{uuid4()}"
        message.session_id = self.session_id
        message.agent_id = self.agent_id
        self.messages.append(message)

if __name__ == "__main__":
    import asyncio

    async def main():
        #tool_box = XGAMcpToolBox(custom_mcp_server_file="mcpservers/custom_servers.json")
        tool_box = None
        engine = await XGAEngine.create(tool_box=tool_box)
        # async for chunk in engine.run_task(task_messages=[{}], custom_tools=["bomc_fault.*"]):
        async for chunk in engine.run_task(task_messages=[{}], custom_tools=[]):
             print(chunk)

    asyncio.run(main())