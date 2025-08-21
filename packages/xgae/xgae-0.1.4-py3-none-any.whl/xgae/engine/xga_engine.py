
import logging
import json

from typing import List, Any, Dict, Optional, AsyncGenerator, cast, Union, Literal
from uuid import uuid4

from xgae.engine.responser.xga_responser_base import TaskResponseContext, TaskResponseProcessor, TaskRunContinuousState
from xgae.engine.xga_base import XGAContextMsg, XGAToolBox, XGAResponseMsg
from xgae.utils.llm_client import LLMClient, LLMConfig
from xgae.utils.setup_env import langfuse
from xgae.utils.utils import handle_error

from xga_prompt_builder import XGAPromptBuilder
from xga_mcp_tool_box import XGAMcpToolBox

class XGATaskEngine:
    def __init__(self,
                 session_id: Optional[str] = None,
                 task_id: Optional[str] = None,
                 agent_id: Optional[str] = None,
                 system_prompt: Optional[str] = None,
                 llm_config: Optional[LLMConfig] = None,
                 prompt_builder: Optional[XGAPromptBuilder] = None,
                 tool_box: Optional[XGAToolBox] = None):
        self.session_id = session_id if session_id else f"xga_sid_{uuid4()}"
        self.task_id = task_id if task_id else f"xga_task_{uuid4()}"
        self.agent_id = agent_id

        self.llm_client = LLMClient(llm_config)
        self.model_name = self.llm_client.model_name
        self.is_stream = self.llm_client.is_stream

        self.prompt_builder = prompt_builder or XGAPromptBuilder(system_prompt)
        self.tool_box = tool_box or XGAMcpToolBox()

        self.task_context_msgs: List[XGAContextMsg] = []
        self.task_no = -1
        self.task_run_id = f"{self.task_id}[{self.task_no}]"
        self.trace_id = None

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
                     system_prompt: Optional[str] = None,
                     general_tools: Optional[List[str]] = None,
                     custom_tools: Optional[List[str]] = None,
                     llm_config: Optional[LLMConfig] = None,
                     prompt_builder: Optional[XGAPromptBuilder] = None,
                     tool_box: Optional[XGAToolBox] = None) -> 'XGATaskEngine':
        engine: XGATaskEngine = cls(session_id=session_id,
                                    task_id=task_id,
                                    agent_id=agent_id,
                                    system_prompt=system_prompt,
                                    llm_config=llm_config,
                                    prompt_builder=prompt_builder,
                                    tool_box=tool_box)

        general_tools = general_tools or ["complete"]
        custom_tools = custom_tools or []
        await engine.__async_init__(general_tools, custom_tools)

        logging.info("*"*30 + f"   XGATaskEngine Task'{engine.task_id}' Initialized   " + "*"*30)
        logging.info(f"model_name={engine.model_name}, is_stream={engine.is_stream}, trace_id={engine.trace_id}")
        logging.info(f"general_tools={general_tools}, custom_tools={custom_tools}")

        return engine


    async def run_task(self,
                       task_message: Dict[str, Any],
                       max_auto_run: int = 25,
                       trace_id: Optional[str] = None) -> AsyncGenerator[Dict[str, Any], None]:
        try:
            self.trace_id = trace_id or self.trace_id or langfuse.create_trace_id()

            self.task_no += 1
            self.task_run_id = f"{self.task_id}[{self.task_no}]"

            self.add_context_msg(type="user", content=task_message, is_llm_message=True)

            if max_auto_run <= 1:
                continuous_state:TaskRunContinuousState  = {
                    "accumulated_content": "",
                    "auto_continue_count": 0,
                    "auto_continue": False
                }
                async for chunk in self._run_task_once(continuous_state):
                    yield chunk
            else:
                async for chunk in self._run_task_auto(max_auto_run):
                    yield chunk
        finally:
            await self.tool_box.destroy_task_tool_box(self.task_id)

    async def _run_task_once(self, continuous_state: TaskRunContinuousState) -> AsyncGenerator[Dict[str, Any], None]:
        llm_messages = [{"role": "system", "content": self.task_prompt}]
        cxt_llm_contents = self._get_context_llm_contents()
        llm_messages.extend(cxt_llm_contents)

        partial_content = continuous_state.get('accumulated_content', '')
        if partial_content:
            temp_assistant_message = {
                "role": "assistant",
                "content": partial_content
            }
            llm_messages.append(temp_assistant_message)

        llm_response = await self.llm_client.create_completion(llm_messages)
        response_processor = self._create_response_processer()

        async for chunk in response_processor.process_response(llm_response, llm_messages, continuous_state):
            yield chunk


    async def _run_task_auto(self, max_auto_run: int) -> AsyncGenerator:
        continuous_state: TaskRunContinuousState = {
            "accumulated_content": "",
            "auto_continue_count": 0,
            "auto_continue": True
        }

        def update_continuous_state(_auto_continue_count,  _auto_continue):
            continuous_state["auto_continue_count"] = _auto_continue_count
            continuous_state["auto_continue"] = _auto_continue

        auto_continue_count = 0
        auto_continue = True
        while auto_continue and auto_continue_count < max_auto_run:
            auto_continue = False

            try:
                async for chunk in self._run_task_once(continuous_state):
                    try:
                        if chunk.get("type") == "status":
                            content = json.loads(chunk.get('content', '{}'))
                            status_type = content.get('status_type', None)
                            if status_type == "error":
                                logging.error(f"run_task_auto: task_response error: {chunk.get('message', 'Unknown error')}")
                                yield chunk
                                return
                            elif status_type == 'finish':
                                finish_reason = content.get('finish_reason', None)
                                if finish_reason == 'stop' :
                                    auto_continue = True
                                    auto_continue_count += 1
                                    update_continuous_state(auto_continue_count, auto_continue)
                                    logging.info(f"run_task_auto: Detected finish_reason='stop', auto-continuing ({auto_continue_count}/{max_auto_run})")
                                    continue
                                elif finish_reason == 'xml_tool_limit_reached':
                                    logging.info(f"run_task_auto: Detected finish_reason='xml_tool_limit_reached', stopping auto-continue")
                                    auto_continue = False
                                    update_continuous_state(auto_continue_count, auto_continue)
                                elif finish_reason == 'length':
                                    auto_continue = True
                                    auto_continue_count += 1
                                    update_continuous_state(auto_continue_count, auto_continue)
                                    logging.info(f"run_task_auto: Detected finish_reason='length', auto-continuing ({auto_continue_count}/{max_auto_run})")
                                    continue
                    except Exception as parse_error:
                        logging.error(f"run_task_auto: Error in parse chunk: {str(parse_error)}")
                        yield {
                            "type": "status",
                            "status": "error",
                            "message": f"Error in parse chunk: {str(parse_error)}"
                        }
                        return

                    # Otherwise just yield the chunk normally
                    yield chunk

                # If not auto-continuing, we're done
                if not auto_continue:
                    break
            except Exception as run_error:
                logging.error(f"run_task_auto: Call task_run_once error: {str(run_error)}")
                yield {
                    "type": "status",
                    "status": "error",
                    "message": f"Call task_run_once error: {str(run_error)}"
                }
                return

    def add_context_msg(self, type: Literal["user", "status",  "tool", "assistant", "assistant_response_end"],
                        content: Union[Dict[str, Any], List[Any], str],
                        is_llm_message: bool,
                        metadata: Optional[Dict[str, Any]]=None)-> XGAContextMsg:
        message = XGAContextMsg(
            message_id = f"xga_msg_{uuid4()}",
            type = type,
            content = content,
            is_llm_message=is_llm_message,
            metadata = metadata,
            session_id = self.session_id,
            agent_id = self.agent_id,
            task_id = self.task_id,
            task_run_id = self.task_run_id,
            trace_id = self.trace_id
        )
        self.task_context_msgs.append(message)

        return message

    def _get_context_llm_contents (self) -> List[Dict[str, Any]]:
        llm_messages = []
        for message in self.task_context_msgs:
            if message["is_llm_message"]:
                llm_messages.append(message)

        cxt_llm_contents = []
        for llm_message in llm_messages:
            content = llm_message["content"]
            # @todo content List type
            if isinstance(content, str):
                try:
                    _content = json.loads(content)
                    cxt_llm_contents.append(_content)
                except json.JSONDecodeError as e:
                    logging.error(f"get_context_llm_contents: Failed to decode json, content=:{content}")
                    handle_error(e)
            else:
                cxt_llm_contents.append(content)

        return cxt_llm_contents

    def _create_response_processer(self) -> TaskResponseProcessor:
        response_context = self._create_response_context()
        is_stream = response_context.get("is_stream", False)
        if is_stream:
            from xgae.engine.responser.xga_stream_responser import StreamTaskResponser
            return StreamTaskResponser(response_context)
        else:
            from xgae.engine.responser.xga_non_stream_responser import NonStreamTaskResponser
            return NonStreamTaskResponser(response_context)

    def _create_response_context(self) -> TaskResponseContext:
        response_context: TaskResponseContext = {
            "is_stream": self.is_stream,
            "task_id": self.task_id,
            "task_run_id": self.task_run_id,
            "trace_id": self.trace_id,
            "model_name": self.model_name,
            "max_xml_tool_calls": 0,
            "add_context_msg": self.add_context_msg,
            "tool_box": self.tool_box,
            "tool_execution_strategy": "parallel",
            "xml_adding_strategy": "user_message",
        }
        return response_context

if __name__ == "__main__":
    import asyncio
    from xgae.utils.utils import read_file
    async def main():
        tool_box = XGAMcpToolBox(custom_mcp_server_file="mcpservers/custom_servers.json")
        system_prompt = read_file("templates/scp_test_prompt.txt")
        engine = await XGATaskEngine.create(tool_box=tool_box,
                                            general_tools=[],
                                            custom_tools=["bomc_fault.*"],
                                            llm_config=LLMConfig(stream=False),
                                            system_prompt=system_prompt)
        #engine = await XGATaskEngine.create()

        async for chunk in engine.run_task(task_message={"role": "user", "content": "定位10.0.0.1的故障"},
                                           max_auto_run=8):
             print(chunk)

    asyncio.run(main())