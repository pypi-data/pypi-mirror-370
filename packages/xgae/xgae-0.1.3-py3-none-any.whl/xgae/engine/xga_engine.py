
from typing import List, Any, Dict, Optional, AsyncGenerator
from uuid import uuid4

from xgae.engine.xga_base import XGAMessage, XGAToolBox
from xgae.utils.llm_client import LLMClient
from xgae.utils.setup_env import langfuse
from xga_prompt_builder import XGAPromptBuilder
from xga_mcp_tool_box import XGAMcpToolBox


class XGATaskEngine():
    def __init__(self,
                 session_id: Optional[str] = None,
                 task_id: Optional[str] = None,
                 agent_id: Optional[str] = None,
                 trace_id: Optional[str] = None,
                 system_prompt: Optional[str] = None,
                 llm_config: Optional[Dict[str, Any]] = None,
                 prompt_builder: Optional[XGAPromptBuilder] = None,
                 tool_box: Optional[XGAToolBox] = None):
        self.session_id = session_id if session_id else f"xga_sid_{uuid4()}"
        self.task_id = task_id if task_id else f"xga_task_{uuid4()}"
        self.agent_id = agent_id
        self.trace_id = trace_id if trace_id else langfuse.create_trace_id()

        self.messages: List[XGAMessage] = []
        self.llm_client = LLMClient(llm_config)
        self.model_name = self.llm_client.model_name
        self.is_stream = self.llm_client.is_stream

        self.prompt_builder = prompt_builder or XGAPromptBuilder(system_prompt)
        self.tool_box = tool_box or XGAMcpToolBox()


    async def __async_init__(self, general_tools:List[str], custom_tools: List[str]) -> None:
        await  self.tool_box.load_mcp_tools_schema()
        await self.tool_box.creat_task_tool_box(self.task_id, general_tools, custom_tools)
        general_tool_schemas = self.tool_box.get_task_tool_schemas(self.task_id, "general_tool")
        custom_tool_schemas = self.tool_box.get_task_tool_schemas(self.task_id, "custom_tool")

        self.task_prompt = self.prompt_builder.build_task_prompt(self.model_name, general_tool_schemas, custom_tool_schemas)

    @classmethod
    async def create(cls,
                     session_id: Optional[str] = None,
                     task_id: Optional[str] = None,
                     agent_id: Optional[str] = None,
                     trace_id: Optional[str] = None,
                     system_prompt: Optional[str] = None,
                     general_tools: Optional[List[str]] = None,
                     custom_tools: Optional[List[str]] = None,
                     llm_config: Optional[Dict[str, Any]] = None,
                     prompt_builder: Optional[XGAPromptBuilder] = None,
                     tool_box: Optional[XGAToolBox] = None) -> 'XGATaskEngine':
        engine: XGATaskEngine = cls(session_id=session_id,
                                    task_id=task_id,
                                    agent_id=agent_id,
                                    trace_id=trace_id,
                                    system_prompt=system_prompt,
                                    llm_config=llm_config,
                                    prompt_builder=prompt_builder,
                                    tool_box=tool_box)
        general_tools = general_tools or ["*"]
        custom_tools = custom_tools or []
        await engine.__async_init__(general_tools, custom_tools)
        return engine


    async def run_task(self, task_messages: List[Dict[str, Any]]) -> AsyncGenerator:
        try:
            yield self.task_prompt

        finally:
            await self.tool_box.destroy_task_tool_box(self.task_id)
        

    def _run_task_once(self):
        pass


    def add_message(self, message: XGAMessage):
        message.message_id = f"xga_msg_{uuid4()}"
        message.session_id = self.session_id
        message.agent_id = self.agent_id
        self.messages.append(message)

if __name__ == "__main__":
    import asyncio

    async def main():
        tool_box = XGAMcpToolBox(custom_mcp_server_file="mcpservers/custom_servers.json")
        engine = await XGATaskEngine.create(tool_box=tool_box, custom_tools=["bomc_fault.*"])
        # engine = await XGATaskEngine.create()

        async for chunk in engine.run_task(task_messages=[{}]):
             print(chunk)

    asyncio.run(main())