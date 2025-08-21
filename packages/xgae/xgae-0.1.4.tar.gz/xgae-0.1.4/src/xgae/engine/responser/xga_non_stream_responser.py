import uuid
import logging

from typing import List, Dict, Any, AsyncGenerator, override,Optional

from xgae.engine.responser.xga_responser_base import TaskResponseProcessor, TaskResponseContext, TaskRunContinuousState

from xgae.utils.json_helpers import (
    safe_json_parse,
    to_json_string, format_for_yield
)

class NonStreamTaskResponser(TaskResponseProcessor):
    def __init__(self, response_context: TaskResponseContext):
        super().__init__(response_context)

    @override
    async def process_response(self,
                               llm_response: Any,
                               prompt_messages: List[Dict[str, Any]],
                               continuous_state: Optional[TaskRunContinuousState] = None) -> AsyncGenerator[Dict[str, Any], None]:
        content = ""
        all_tool_data = []  # Stores {'tool_call': ..., 'parsing_details': ...}
        tool_index = 0
        assistant_message_object = None
        tool_result_message_objects = {}
        finish_reason = None

        native_tool_calls_for_message = []
        llm_model = self.response_context.get("model_name")
        thread_id = self.response_context.get("task_id")
        thread_run_id = self.response_context.get("task_run_id")
        tool_execution_strategy = self.response_context.get("tool_execution_strategy", "parallel")
        xml_adding_strategy = self.response_context.get("xml_adding_strategy", "user_message")
        max_xml_tool_calls = self.response_context.get("max_xml_tool_calls", 0)
        try:
            # Save and Yield thread_run_start status message
            start_content = {"status_type": "thread_run_start", "thread_run_id": thread_run_id}
            start_msg_obj = self.add_message(
                type="status", content=start_content,
                is_llm_message=False, metadata={"thread_run_id": thread_run_id}
            )
            if start_msg_obj: yield format_for_yield(start_msg_obj)

            # Extract finish_reason, content, tool calls
            if hasattr(llm_response, 'choices') and llm_response.choices:
                if hasattr(llm_response.choices[0], 'finish_reason'):
                    finish_reason = llm_response.choices[0].finish_reason
                    logging.info(f"Non-streaming finish_reason: {finish_reason}")
                    self.trace.event(name="non_streaming_finish_reason", level="DEFAULT",
                                     status_message=(f"Non-streaming finish_reason: {finish_reason}"))
                response_message = llm_response.choices[0].message if hasattr(llm_response.choices[0],
                                                                              'message') else None
                if response_message:
                    if hasattr(response_message, 'content') and response_message.content:
                        content = response_message.content
                        
                        parsed_xml_data = self._parse_xml_tool_calls(content)
                        if max_xml_tool_calls > 0 and len(parsed_xml_data) > max_xml_tool_calls:
                            # Truncate content and tool data if limit exceeded
                            # ... (Truncation logic similar to streaming) ...
                            if parsed_xml_data:
                                xml_chunks = self._extract_xml_chunks(content)[:max_xml_tool_calls]
                                if xml_chunks:
                                    last_chunk = xml_chunks[-1]
                                    last_chunk_pos = content.find(last_chunk)
                                    if last_chunk_pos >= 0: content = content[:last_chunk_pos + len(last_chunk)]
                            parsed_xml_data = parsed_xml_data[:max_xml_tool_calls]
                            finish_reason = "xml_tool_limit_reached"
                        all_tool_data.extend(parsed_xml_data)

                    # if config.native_tool_calling and hasattr(response_message,
                    #                                           'tool_calls') and response_message.tool_calls:
                    #     for tool_call in response_message.tool_calls:
                    #         if hasattr(tool_call, 'function'):
                    #             exec_tool_call = {
                    #                 "function_name": tool_call.function.name,
                    #                 "arguments": safe_json_parse(tool_call.function.arguments) if isinstance(
                    #                     tool_call.function.arguments, str) else tool_call.function.arguments,
                    #                 "id": tool_call.id if hasattr(tool_call, 'id') else str(uuid.uuid4())
                    #             }
                    #             all_tool_data.append({"tool_call": exec_tool_call, "parsing_details": None})
                    #             native_tool_calls_for_message.append({
                    #                 "id": exec_tool_call["id"], "type": "function",
                    #                 "function": {
                    #                     "name": tool_call.function.name,
                    #                     "arguments": tool_call.function.arguments if isinstance(
                    #                         tool_call.function.arguments, str) else to_json_string(
                    #                         tool_call.function.arguments)
                    #                 }
                    #             })

            # --- SAVE and YIELD Final Assistant Message ---
            message_data = {"role": "assistant", "content": content,
                            "tool_calls": native_tool_calls_for_message or None}
            assistant_message_object = self._add_message_with_agent_info(type="assistant", content=message_data,
                is_llm_message=True, metadata={"thread_run_id": thread_run_id}
            )
            if assistant_message_object:
                yield assistant_message_object
            else:
                logging.error(f"Failed to save non-streaming assistant message for thread {thread_id}")
                self.trace.event(name="failed_to_save_non_streaming_assistant_message_for_thread", level="ERROR",
                                 status_message=(
                                     f"Failed to save non-streaming assistant message for thread {thread_id}"))
                err_content = {"role": "system", "status_type": "error", "message": "Failed to save assistant message"}
                err_msg_obj = self.add_message(
                    type="status", content=err_content,
                    is_llm_message=False, metadata={"thread_run_id": thread_run_id}
                )
                if err_msg_obj: yield format_for_yield(err_msg_obj)

            # --- Execute Tools and Yield Results ---
            tool_calls_to_execute = [item['tool_call'] for item in all_tool_data]
            if  tool_calls_to_execute:
                logging.info(
                    f"Executing {len(tool_calls_to_execute)} tools with strategy: {tool_execution_strategy}")
                self.trace.event(name="executing_tools_with_strategy", level="DEFAULT", status_message=(
                    f"Executing {len(tool_calls_to_execute)} tools with strategy: {tool_execution_strategy}"))
                tool_results = await self._execute_tools(tool_calls_to_execute, tool_execution_strategy)

                for i, (returned_tool_call, result) in enumerate(tool_results):
                    original_data = all_tool_data[i]
                    tool_call_from_data = original_data['tool_call']
                    parsing_details = original_data['parsing_details']
                    current_assistant_id = assistant_message_object['message_id'] if assistant_message_object else None

                    context = self._create_tool_context(
                        tool_call_from_data, tool_index, current_assistant_id, parsing_details
                    )
                    context.result = result

                    # Save and Yield start status
                    started_msg_obj = self._yield_and_save_tool_started(context, thread_id, thread_run_id)
                    if started_msg_obj: yield format_for_yield(started_msg_obj)

                    # Save tool result
                    saved_tool_result_object = self._add_tool_result(
                        thread_id, tool_call_from_data, result, xml_adding_strategy,
                        current_assistant_id, parsing_details
                    )

                    # Save and Yield completed/failed status
                    completed_msg_obj = self._yield_and_save_tool_completed(
                        context,
                        saved_tool_result_object['message_id'] if saved_tool_result_object else None,
                        thread_id, thread_run_id
                    )
                    if completed_msg_obj: yield format_for_yield(completed_msg_obj)

                    # Yield the saved tool result object
                    if saved_tool_result_object:
                        tool_result_message_objects[tool_index] = saved_tool_result_object
                        yield format_for_yield(saved_tool_result_object)
                    else:
                        logging.error(f"Failed to save tool result for index {tool_index}")
                        self.trace.event(name="failed_to_save_tool_result_for_index", level="ERROR",
                                         status_message=(f"Failed to save tool result for index {tool_index}"))

                    tool_index += 1

            # --- Save and Yield Final Status ---
            if finish_reason:
                finish_content = {"status_type": "finish", "finish_reason": finish_reason}
                finish_msg_obj = self.add_message(
                    type="status", content=finish_content,
                    is_llm_message=False, metadata={"thread_run_id": thread_run_id}
                )
                if finish_msg_obj: yield format_for_yield(finish_msg_obj)

            # --- Save and Yield assistant_response_end ---
            if assistant_message_object:  # Only save if assistant message was saved
                try:
                    # Save the full LiteLLM response object directly in content
                    self.add_message(
                        type="assistant_response_end",
                        content=llm_response,
                        is_llm_message=False,
                        metadata={"thread_run_id": thread_run_id}
                    )
                    logging.info("Assistant response end saved for non-stream")
                except Exception as e:
                    logging.error(f"Error saving assistant response end for non-stream: {str(e)}")
                    self.trace.event(name="error_saving_assistant_response_end_for_non_stream", level="ERROR",
                                     status_message=(f"Error saving assistant response end for non-stream: {str(e)}"))

        except Exception as e:
            logging.error(f"Error processing non-streaming response: {str(e)}", exc_info=True)
            self.trace.event(name="error_processing_non_streaming_response", level="ERROR",
                             status_message=(f"Error processing non-streaming response: {str(e)}"))
            # Save and yield error status
            err_content = {"role": "system", "status_type": "error", "message": str(e)}
            err_msg_obj = self.add_message(
                type="status", content=err_content,
                is_llm_message=False, metadata={"thread_run_id": thread_run_id if 'thread_run_id' in locals() else None}
            )
            if err_msg_obj: yield format_for_yield(err_msg_obj)

            # Re-raise the same exception (not a new one) to ensure proper error propagation
            logging.critical(f"Re-raising error to stop further processing: {str(e)}")
            self.trace.event(name="re_raising_error_to_stop_further_processing", level="CRITICAL",
                             status_message=(f"Re-raising error to stop further processing: {str(e)}"))
            raise  # Use bare 'raise' to preserve the original exception with its traceback

        finally:
            # Save and Yield the final thread_run_end status
            end_content = {"status_type": "thread_run_end"}
            end_msg_obj = self.add_message(
                type="status", content=end_content,
                is_llm_message=False, metadata={"thread_run_id": thread_run_id if 'thread_run_id' in locals() else None}
            )
            if end_msg_obj: yield format_for_yield(end_msg_obj)

