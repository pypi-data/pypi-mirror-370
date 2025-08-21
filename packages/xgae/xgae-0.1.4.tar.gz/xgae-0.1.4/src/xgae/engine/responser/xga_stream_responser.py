import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, AsyncGenerator, override

from xgae.engine.responser.xga_responser_base import TaskResponseProcessor, ProcessorConfig, TaskResponseContext,TaskRunContinuousState
from xgae.utils.json_helpers import (
    ensure_dict, safe_json_parse,
    to_json_string, format_for_yield
)

class StreamTaskResponser(TaskResponseProcessor):
    def __init__(self, response_context: TaskResponseContext):
        super().__init__(response_context)

    @override
    async def process_response(
            self,
            llm_response: AsyncGenerator,
            prompt_messages: List[Dict[str, Any]],
            continuous_state: Optional[TaskRunContinuousState] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Process a streaming LLM response, handling tool calls and execution.

        Args:
            llm_response: Streaming response from the LLM
            thread_id: ID of the conversation thread
            prompt_messages: List of messages sent to the LLM (the prompt)
            llm_model: The name of the LLM model used
            config: Configuration for parsing and execution
            can_auto_continue: Whether auto-continue is enabled
            auto_continue_count: Number of auto-continue cycles
            continuous_state: Previous state of the conversation

        Yields:
            Complete message objects matching the DB schema, except for content chunks.
        """
        # Initialize from continuous state if provided (for auto-continue)
        can_auto_continue = continuous_state.get("auto_continue", False)
        auto_continue_count = continuous_state.get("auto_continue_count", 0)
        llm_model = self.response_context.get("model_name")
        config: ProcessorConfig = ProcessorConfig()
        thread_id = self.response_context.get("task_id")

        continuous_state = continuous_state or {}
        accumulated_content = continuous_state.get('accumulated_content', "")
        tool_calls_buffer = {}
        current_xml_content = accumulated_content  # equal to accumulated_content if auto-continuing, else blank
        xml_chunks_buffer = []
        pending_tool_executions = []
        yielded_tool_indices = set()  # Stores indices of tools whose *status* has been yielded
        tool_index = 0
        xml_tool_call_count = 0
        finish_reason = None
        should_auto_continue = False
        last_assistant_message_object = None  # Store the final saved assistant message object
        tool_result_message_objects = {}  # tool_index -> full saved message object
        has_printed_thinking_prefix = False  # Flag for printing thinking prefix only once
        agent_should_terminate = False  # Flag to track if a terminating tool has been executed
        complete_native_tool_calls = []  # Initialize early for use in assistant_response_end

        # Collect metadata for reconstructing LiteLLM response object
        streaming_metadata = {
            "model": llm_model,
            "created": None,
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            },
            "response_ms": None,
            "first_chunk_time": None,
            "last_chunk_time": None
        }

        logging.info(f"Streaming Config: XML={config.xml_tool_calling}, Native={config.native_tool_calling}, "
                    f"Execute on stream={config.execute_on_stream}, Strategy={config.tool_execution_strategy}")

        # Reuse thread_run_id for auto-continue or create new one
        thread_run_id = continuous_state.get('thread_run_id') or str(uuid.uuid4())
        continuous_state['thread_run_id'] = thread_run_id

        try:
            # --- Save and Yield Start Events (only if not auto-continuing) ---
            if auto_continue_count == 0:
                start_content = {"status_type": "thread_run_start", "thread_run_id": thread_run_id}
                start_msg_obj = await self.add_message(
                   type="status", content=start_content,
                    is_llm_message=False, metadata={"thread_run_id": thread_run_id}
                )
                if start_msg_obj: yield format_for_yield(start_msg_obj)

                assist_start_content = {"status_type": "assistant_response_start"}
                assist_start_msg_obj = await self.add_message(
                    type="status", content=assist_start_content,
                    is_llm_message=False, metadata={"thread_run_id": thread_run_id}
                )
                if assist_start_msg_obj: yield format_for_yield(assist_start_msg_obj)
            # --- End Start Events ---

            __sequence = continuous_state.get('sequence', 0)  # get the sequence from the previous auto-continue cycle

            async for chunk in llm_response:
                # Extract streaming metadata from chunks
                current_time = datetime.now(timezone.utc).timestamp()
                if streaming_metadata["first_chunk_time"] is None:
                    streaming_metadata["first_chunk_time"] = current_time
                streaming_metadata["last_chunk_time"] = current_time

                # Extract metadata from chunk attributes
                if hasattr(chunk, 'created') and chunk.created:
                    streaming_metadata["created"] = chunk.created
                if hasattr(chunk, 'model') and chunk.model:
                    streaming_metadata["model"] = chunk.model
                if hasattr(chunk, 'usage') and chunk.usage:
                    # Update usage information if available (including zero values)
                    if hasattr(chunk.usage, 'prompt_tokens') and chunk.usage.prompt_tokens is not None:
                        streaming_metadata["usage"]["prompt_tokens"] = chunk.usage.prompt_tokens
                    if hasattr(chunk.usage, 'completion_tokens') and chunk.usage.completion_tokens is not None:
                        streaming_metadata["usage"]["completion_tokens"] = chunk.usage.completion_tokens
                    if hasattr(chunk.usage, 'total_tokens') and chunk.usage.total_tokens is not None:
                        streaming_metadata["usage"]["total_tokens"] = chunk.usage.total_tokens

                if hasattr(chunk, 'choices') and chunk.choices and hasattr(chunk.choices[0], 'finish_reason') and \
                        chunk.choices[0].finish_reason:
                    finish_reason = chunk.choices[0].finish_reason
                    logging.debug(f"Detected finish_reason: {finish_reason}")

                if hasattr(chunk, 'choices') and chunk.choices:
                    delta = chunk.choices[0].delta if hasattr(chunk.choices[0], 'delta') else None

                    # Check for and log Anthropic thinking content
                    if delta and hasattr(delta, 'reasoning_content') and delta.reasoning_content:
                        if not has_printed_thinking_prefix:
                            # print("[THINKING]: ", end='', flush=True)
                            has_printed_thinking_prefix = True
                        # print(delta.reasoning_content, end='', flush=True)
                        # Append reasoning to main content to be saved in the final message
                        accumulated_content += delta.reasoning_content

                    # Process content chunk
                    if delta and hasattr(delta, 'content') and delta.content:
                        chunk_content = delta.content
                        # print(chunk_content, end='', flush=True)
                        accumulated_content += chunk_content
                        current_xml_content += chunk_content

                        if not (config.max_xml_tool_calls > 0 and xml_tool_call_count >= config.max_xml_tool_calls):
                            # Yield ONLY content chunk (don't save)
                            now_chunk = datetime.now(timezone.utc).isoformat()
                            yield {
                                "sequence": __sequence,
                                "message_id": None, "thread_id": thread_id, "type": "assistant",
                                "is_llm_message": True,
                                "content": to_json_string({"role": "assistant", "content": chunk_content}),
                                "metadata": to_json_string({"stream_status": "chunk", "thread_run_id": thread_run_id}),
                                "created_at": now_chunk, "updated_at": now_chunk
                            }
                            __sequence += 1
                        else:
                            logging.info("XML tool call limit reached - not yielding more content chunks")
                            self.trace.event(name="xml_tool_call_limit_reached", level="DEFAULT", status_message=(
                                f"XML tool call limit reached - not yielding more content chunks"))

                        # --- Process XML Tool Calls (if enabled and limit not reached) ---
                        if config.xml_tool_calling and not (
                                config.max_xml_tool_calls > 0 and xml_tool_call_count >= config.max_xml_tool_calls):
                            xml_chunks = self._extract_xml_chunks(current_xml_content)
                            for xml_chunk in xml_chunks:
                                current_xml_content = current_xml_content.replace(xml_chunk, "", 1)
                                xml_chunks_buffer.append(xml_chunk)
                                result = self._parse_xml_tool_call(xml_chunk)
                                if result:
                                    tool_call, parsing_details = result
                                    xml_tool_call_count += 1
                                    current_assistant_id = last_assistant_message_object[
                                        'message_id'] if last_assistant_message_object else None
                                    context = self._create_tool_context(
                                        tool_call, tool_index, current_assistant_id, parsing_details
                                    )

                                    if config.execute_tools and config.execute_on_stream:
                                        # Save and Yield tool_started status
                                        started_msg_obj = await self._yield_and_save_tool_started(context, thread_id,
                                                                                                  thread_run_id)
                                        if started_msg_obj: yield format_for_yield(started_msg_obj)
                                        yielded_tool_indices.add(tool_index)  # Mark status as yielded

                                        execution_task = asyncio.create_task(self._execute_tool(tool_call))
                                        pending_tool_executions.append({
                                            "task": execution_task, "tool_call": tool_call,
                                            "tool_index": tool_index, "context": context
                                        })
                                        tool_index += 1

                                    if config.max_xml_tool_calls > 0 and xml_tool_call_count >= config.max_xml_tool_calls:
                                        logging.debug(f"Reached XML tool call limit ({config.max_xml_tool_calls})")
                                        finish_reason = "xml_tool_limit_reached"
                                        break  # Stop processing more XML chunks in this delta

                    # --- Process Native Tool Call Chunks ---
                    if config.native_tool_calling and delta and hasattr(delta, 'tool_calls') and delta.tool_calls:
                        for tool_call_chunk in delta.tool_calls:
                            # Yield Native Tool Call Chunk (transient status, not saved)
                            # ... (safe extraction logic for tool_call_data_chunk) ...
                            tool_call_data_chunk = {}  # Placeholder for extracted data
                            if hasattr(tool_call_chunk, 'model_dump'):
                                tool_call_data_chunk = tool_call_chunk.model_dump()
                            else:  # Manual extraction...
                                if hasattr(tool_call_chunk, 'id'): tool_call_data_chunk['id'] = tool_call_chunk.id
                                if hasattr(tool_call_chunk, 'index'): tool_call_data_chunk[
                                    'index'] = tool_call_chunk.index
                                if hasattr(tool_call_chunk, 'type'): tool_call_data_chunk['type'] = tool_call_chunk.type
                                if hasattr(tool_call_chunk, 'function'):
                                    tool_call_data_chunk['function'] = {}
                                    if hasattr(tool_call_chunk.function, 'name'): tool_call_data_chunk['function'][
                                        'name'] = tool_call_chunk.function.name
                                    if hasattr(tool_call_chunk.function, 'arguments'): tool_call_data_chunk['function'][
                                        'arguments'] = tool_call_chunk.function.arguments if isinstance(
                                        tool_call_chunk.function.arguments, str) else to_json_string(
                                        tool_call_chunk.function.arguments)

                            now_tool_chunk = datetime.now(timezone.utc).isoformat()
                            yield {
                                "message_id": None, "thread_id": thread_id, "type": "status", "is_llm_message": True,
                                "content": to_json_string({"role": "assistant", "status_type": "tool_call_chunk",
                                                           "tool_call_chunk": tool_call_data_chunk}),
                                "metadata": to_json_string({"thread_run_id": thread_run_id}),
                                "created_at": now_tool_chunk, "updated_at": now_tool_chunk
                            }

                            # --- Buffer and Execute Complete Native Tool Calls ---
                            if not hasattr(tool_call_chunk, 'function'): continue
                            idx = tool_call_chunk.index if hasattr(tool_call_chunk, 'index') else 0
                            # ... (buffer update logic remains same) ...
                            # ... (check complete logic remains same) ...
                            has_complete_tool_call = False  # Placeholder
                            if (tool_calls_buffer.get(idx) and
                                    tool_calls_buffer[idx]['id'] and
                                    tool_calls_buffer[idx]['function']['name'] and
                                    tool_calls_buffer[idx]['function']['arguments']):
                                try:
                                    safe_json_parse(tool_calls_buffer[idx]['function']['arguments'])
                                    has_complete_tool_call = True
                                except json.JSONDecodeError:
                                    pass

                            if has_complete_tool_call and config.execute_tools and config.execute_on_stream:
                                current_tool = tool_calls_buffer[idx]
                                tool_call_data = {
                                    "function_name": current_tool['function']['name'],
                                    "arguments": safe_json_parse(current_tool['function']['arguments']),
                                    "id": current_tool['id']
                                }
                                current_assistant_id = last_assistant_message_object[
                                    'message_id'] if last_assistant_message_object else None
                                context = self._create_tool_context(
                                    tool_call_data, tool_index, current_assistant_id
                                )

                                # Save and Yield tool_started status
                                started_msg_obj = await self._yield_and_save_tool_started(context, thread_id,
                                                                                          thread_run_id)
                                if started_msg_obj: yield format_for_yield(started_msg_obj)
                                yielded_tool_indices.add(tool_index)  # Mark status as yielded

                                execution_task = asyncio.create_task(self._execute_tool(tool_call_data))
                                pending_tool_executions.append({
                                    "task": execution_task, "tool_call": tool_call_data,
                                    "tool_index": tool_index, "context": context
                                })
                                tool_index += 1

                if finish_reason == "xml_tool_limit_reached":
                    logging.info("Stopping stream processing after loop due to XML tool call limit")
                    self.trace.event(name="stopping_stream_processing_after_loop_due_to_xml_tool_call_limit",
                                     level="DEFAULT", status_message=(
                            f"Stopping stream processing after loop due to XML tool call limit"))
                    break

            # print() # Add a final newline after the streaming loop finishes

            # --- After Streaming Loop ---

            if (
                    streaming_metadata["usage"]["total_tokens"] == 0
            ):
                logging.info("🔥 No usage data from provider, counting with litellm.token_counter")

                try:
                    # prompt side
                    # prompt_tokens = token_counter(
                    #     model=llm_model,
                    #     messages=prompt_messages  # chat or plain; token_counter handles both
                    # )
                    #
                    # # completion side
                    # completion_tokens = token_counter(
                    #     model=llm_model,
                    #     text=accumulated_content or ""  # empty string safe
                    # )

                    # streaming_metadata["usage"]["prompt_tokens"] = prompt_tokens
                    # streaming_metadata["usage"]["completion_tokens"] = completion_tokens
                    # streaming_metadata["usage"]["total_tokens"] = prompt_tokens + completion_tokens
                    #
                    # logging.info(
                    #     f"🔥 Estimated tokens – prompt: {prompt_tokens}, "
                    #     f"completion: {completion_tokens}, total: {prompt_tokens + completion_tokens}"
                    # )
                    self.trace.event(name="usage_calculated_with_litellm_token_counter", level="DEFAULT",
                                     status_message=(f"Usage calculated with litellm.token_counter"))
                except Exception as e:
                    logging.warning(f"Failed to calculate usage: {str(e)}")
                    self.trace.event(name="failed_to_calculate_usage", level="WARNING",
                                     status_message=(f"Failed to calculate usage: {str(e)}"))

            # Wait for pending tool executions from streaming phase
            tool_results_buffer = []  # Stores (tool_call, result, tool_index, context)
            if pending_tool_executions:
                logging.info(f"Waiting for {len(pending_tool_executions)} pending streamed tool executions")
                self.trace.event(name="waiting_for_pending_streamed_tool_executions", level="DEFAULT", status_message=(
                    f"Waiting for {len(pending_tool_executions)} pending streamed tool executions"))
                # ... (asyncio.wait logic) ...
                pending_tasks = [execution["task"] for execution in pending_tool_executions]
                done, _ = await asyncio.wait(pending_tasks)

                for execution in pending_tool_executions:
                    tool_idx = execution.get("tool_index", -1)
                    context = execution["context"]
                    tool_name = context.function_name

                    # Check if status was already yielded during stream run
                    if tool_idx in yielded_tool_indices:
                        logging.debug(f"Status for tool index {tool_idx} already yielded.")
                        # Still need to process the result for the buffer
                        try:
                            if execution["task"].done():
                                result = execution["task"].result()
                                context.result = result
                                tool_results_buffer.append((execution["tool_call"], result, tool_idx, context))

                                if tool_name in ['ask', 'complete']:
                                    logging.info(
                                        f"Terminating tool '{tool_name}' completed during streaming. Setting termination flag.")
                                    self.trace.event(name="terminating_tool_completed_during_streaming",
                                                     level="DEFAULT", status_message=(
                                            f"Terminating tool '{tool_name}' completed during streaming. Setting termination flag."))
                                    agent_should_terminate = True

                            else:  # Should not happen with asyncio.wait
                                logging.warning(f"Task for tool index {tool_idx} not done after wait.")
                                self.trace.event(name="task_for_tool_index_not_done_after_wait", level="WARNING",
                                                 status_message=(
                                                     f"Task for tool index {tool_idx} not done after wait."))
                        except Exception as e:
                            logging.error(f"Error getting result for pending tool execution {tool_idx}: {str(e)}")
                            self.trace.event(name="error_getting_result_for_pending_tool_execution", level="ERROR",
                                             status_message=(
                                                 f"Error getting result for pending tool execution {tool_idx}: {str(e)}"))
                            context.error = e
                            # Save and Yield tool error status message (even if started was yielded)
                            error_msg_obj = await self._yield_and_save_tool_error(context, thread_id, thread_run_id)
                            if error_msg_obj: yield format_for_yield(error_msg_obj)
                        continue  # Skip further status yielding for this tool index

                    # If status wasn't yielded before (shouldn't happen with current logic), yield it now
                    try:
                        if execution["task"].done():
                            result = execution["task"].result()
                            context.result = result
                            tool_results_buffer.append((execution["tool_call"], result, tool_idx, context))

                            # Check if this is a terminating tool
                            if tool_name in ['ask', 'complete']:
                                logging.info(
                                    f"Terminating tool '{tool_name}' completed during streaming. Setting termination flag.")
                                self.trace.event(name="terminating_tool_completed_during_streaming", level="DEFAULT",
                                                 status_message=(
                                                     f"Terminating tool '{tool_name}' completed during streaming. Setting termination flag."))
                                agent_should_terminate = True

                            # Save and Yield tool completed/failed status
                            completed_msg_obj = await self._yield_and_save_tool_completed(
                                context, None, thread_id, thread_run_id
                            )
                            if completed_msg_obj: yield format_for_yield(completed_msg_obj)
                            yielded_tool_indices.add(tool_idx)
                    except Exception as e:
                        logging.error(
                            f"Error getting result/yielding status for pending tool execution {tool_idx}: {str(e)}")
                        self.trace.event(name="error_getting_result_yielding_status_for_pending_tool_execution",
                                         level="ERROR", status_message=(
                                f"Error getting result/yielding status for pending tool execution {tool_idx}: {str(e)}"))
                        context.error = e
                        # Save and Yield tool error status
                        error_msg_obj = await self._yield_and_save_tool_error(context, thread_id, thread_run_id)
                        if error_msg_obj: yield format_for_yield(error_msg_obj)
                        yielded_tool_indices.add(tool_idx)

            # Save and yield finish status if limit was reached
            if finish_reason == "xml_tool_limit_reached":
                finish_content = {"status_type": "finish", "finish_reason": "xml_tool_limit_reached"}
                finish_msg_obj = await self.add_message(
                     type="status", content=finish_content,
                    is_llm_message=False, metadata={"thread_run_id": thread_run_id}
                )
                if finish_msg_obj: yield format_for_yield(finish_msg_obj)
                logging.info(
                    f"Stream finished with reason: xml_tool_limit_reached after {xml_tool_call_count} XML tool calls")
                self.trace.event(name="stream_finished_with_reason_xml_tool_limit_reached_after_xml_tool_calls",
                                 level="DEFAULT", status_message=(
                        f"Stream finished with reason: xml_tool_limit_reached after {xml_tool_call_count} XML tool calls"))

            # Calculate if auto-continue is needed if the finish reason is length
            should_auto_continue = (can_auto_continue and finish_reason == 'length')

            # --- SAVE and YIELD Final Assistant Message ---
            # Only save assistant message if NOT auto-continuing due to length to avoid duplicate messages
            if accumulated_content and not should_auto_continue:
                # ... (Truncate accumulated_content logic) ...
                if config.max_xml_tool_calls > 0 and xml_tool_call_count >= config.max_xml_tool_calls and xml_chunks_buffer:
                    last_xml_chunk = xml_chunks_buffer[-1]
                    last_chunk_end_pos = accumulated_content.find(last_xml_chunk) + len(last_xml_chunk)
                    if last_chunk_end_pos > 0:
                        accumulated_content = accumulated_content[:last_chunk_end_pos]

                # ... (Extract complete_native_tool_calls logic) ...
                # Update complete_native_tool_calls from buffer (initialized earlier)
                if config.native_tool_calling:
                    for idx, tc_buf in tool_calls_buffer.items():
                        if tc_buf['id'] and tc_buf['function']['name'] and tc_buf['function']['arguments']:
                            try:
                                args = safe_json_parse(tc_buf['function']['arguments'])
                                complete_native_tool_calls.append({
                                    "id": tc_buf['id'], "type": "function",
                                    "function": {"name": tc_buf['function']['name'], "arguments": args}
                                })
                            except json.JSONDecodeError:
                                continue

                message_data = {  # Dict to be saved in 'content'
                    "role": "assistant", "content": accumulated_content,
                    "tool_calls": complete_native_tool_calls or None
                }

                last_assistant_message_object = await self._add_message_with_agent_info(type="assistant", content=message_data,
                    is_llm_message=True, metadata={"thread_run_id": thread_run_id}
                )

                if last_assistant_message_object:
                    # Yield the complete saved object, adding stream_status metadata just for yield
                    yield_metadata = ensure_dict(last_assistant_message_object.get('metadata'), {})
                    yield_metadata['stream_status'] = 'complete'
                    # Format the message for yielding
                    yield_message = last_assistant_message_object.copy()
                    yield_message['metadata'] = yield_metadata
                    yield format_for_yield(yield_message)
                else:
                    logging.error(f"Failed to save final assistant message for thread {thread_id}")
                    self.trace.event(name="failed_to_save_final_assistant_message_for_thread", level="ERROR",
                                     status_message=(f"Failed to save final assistant message for thread {thread_id}"))
                    # Save and yield an error status
                    err_content = {"role": "system", "status_type": "error",
                                   "message": "Failed to save final assistant message"}
                    err_msg_obj = await self.add_message(
                        type="status", content=err_content,
                        is_llm_message=False, metadata={"thread_run_id": thread_run_id}
                    )
                    if err_msg_obj: yield format_for_yield(err_msg_obj)

            # --- Process All Tool Results Now ---
            if config.execute_tools:
                final_tool_calls_to_process = []
                # ... (Gather final_tool_calls_to_process from native and XML buffers) ...
                # Gather native tool calls from buffer
                if config.native_tool_calling and complete_native_tool_calls:
                    for tc in complete_native_tool_calls:
                        final_tool_calls_to_process.append({
                            "function_name": tc["function"]["name"],
                            "arguments": tc["function"]["arguments"],  # Already parsed object
                            "id": tc["id"]
                        })
                # Gather XML tool calls from buffer (up to limit)
                parsed_xml_data = []
                if config.xml_tool_calling:
                    # Reparse remaining content just in case (should be empty if processed correctly)
                    xml_chunks = self._extract_xml_chunks(current_xml_content)
                    xml_chunks_buffer.extend(xml_chunks)
                    # Process only chunks not already handled in the stream loop
                    remaining_limit = config.max_xml_tool_calls - xml_tool_call_count if config.max_xml_tool_calls > 0 else len(
                        xml_chunks_buffer)
                    xml_chunks_to_process = xml_chunks_buffer[:remaining_limit]  # Ensure limit is respected

                    for chunk in xml_chunks_to_process:
                        parsed_result = self._parse_xml_tool_call(chunk)
                        if parsed_result:
                            tool_call, parsing_details = parsed_result
                            # Avoid adding if already processed during streaming
                            if not any(exec['tool_call'] == tool_call for exec in pending_tool_executions):
                                final_tool_calls_to_process.append(tool_call)
                                parsed_xml_data.append({'tool_call': tool_call, 'parsing_details': parsing_details})

                all_tool_data_map = {}  # tool_index -> {'tool_call': ..., 'parsing_details': ...}
                # Add native tool data
                native_tool_index = 0
                if config.native_tool_calling and complete_native_tool_calls:
                    for tc in complete_native_tool_calls:
                        # Find the corresponding entry in final_tool_calls_to_process if needed
                        # For now, assume order matches if only native used
                        exec_tool_call = {
                            "function_name": tc["function"]["name"],
                            "arguments": tc["function"]["arguments"],
                            "id": tc["id"]
                        }
                        all_tool_data_map[native_tool_index] = {"tool_call": exec_tool_call, "parsing_details": None}
                        native_tool_index += 1

                # Add XML tool data
                xml_tool_index_start = native_tool_index
                for idx, item in enumerate(parsed_xml_data):
                    all_tool_data_map[xml_tool_index_start + idx] = item

                tool_results_map = {}  # tool_index -> (tool_call, result, context)

                # Populate from buffer if executed on stream
                if config.execute_on_stream and tool_results_buffer:
                    logging.info(f"Processing {len(tool_results_buffer)} buffered tool results")
                    self.trace.event(name="processing_buffered_tool_results", level="DEFAULT",
                                     status_message=(f"Processing {len(tool_results_buffer)} buffered tool results"))
                    for tool_call, result, tool_idx, context in tool_results_buffer:
                        if last_assistant_message_object: context.assistant_message_id = last_assistant_message_object[
                            'message_id']
                        tool_results_map[tool_idx] = (tool_call, result, context)

                # Or execute now if not streamed
                elif final_tool_calls_to_process and not config.execute_on_stream:
                    logging.info(
                        f"Executing {len(final_tool_calls_to_process)} tools ({config.tool_execution_strategy}) after stream")
                    self.trace.event(name="executing_tools_after_stream", level="DEFAULT", status_message=(
                        f"Executing {len(final_tool_calls_to_process)} tools ({config.tool_execution_strategy}) after stream"))
                    results_list = await self._execute_tools(final_tool_calls_to_process,
                                                             config.tool_execution_strategy)
                    current_tool_idx = 0
                    for tc, res in results_list:
                        # Map back using all_tool_data_map which has correct indices
                        if current_tool_idx in all_tool_data_map:
                            tool_data = all_tool_data_map[current_tool_idx]
                            context = self._create_tool_context(
                                tc, current_tool_idx,
                                last_assistant_message_object['message_id'] if last_assistant_message_object else None,
                                tool_data.get('parsing_details')
                            )
                            context.result = res
                            tool_results_map[current_tool_idx] = (tc, res, context)
                        else:
                            logging.warning(f"Could not map result for tool index {current_tool_idx}")
                            self.trace.event(name="could_not_map_result_for_tool_index", level="WARNING",
                                             status_message=(f"Could not map result for tool index {current_tool_idx}"))
                        current_tool_idx += 1

                # Save and Yield each result message
                if tool_results_map:
                    logging.info(f"Saving and yielding {len(tool_results_map)} final tool result messages")
                    self.trace.event(name="saving_and_yielding_final_tool_result_messages", level="DEFAULT",
                                     status_message=(
                                         f"Saving and yielding {len(tool_results_map)} final tool result messages"))
                    for tool_idx in sorted(tool_results_map.keys()):
                        tool_call, result, context = tool_results_map[tool_idx]
                        context.result = result
                        if not context.assistant_message_id and last_assistant_message_object:
                            context.assistant_message_id = last_assistant_message_object['message_id']

                        # Yield start status ONLY IF executing non-streamed (already yielded if streamed)
                        if not config.execute_on_stream and tool_idx not in yielded_tool_indices:
                            started_msg_obj = await self._yield_and_save_tool_started(context, thread_id, thread_run_id)
                            if started_msg_obj: yield format_for_yield(started_msg_obj)
                            yielded_tool_indices.add(tool_idx)  # Mark status yielded

                        # Save the tool result message to DB
                        saved_tool_result_object = await self._add_tool_result(  # Returns full object or None
                            thread_id, tool_call, result, config.xml_adding_strategy,
                            context.assistant_message_id, context.parsing_details
                        )

                        # Yield completed/failed status (linked to saved result ID if available)
                        completed_msg_obj = await self._yield_and_save_tool_completed(
                            context,
                            saved_tool_result_object['message_id'] if saved_tool_result_object else None,
                            thread_id, thread_run_id
                        )
                        if completed_msg_obj: yield format_for_yield(completed_msg_obj)
                        # Don't add to yielded_tool_indices here, completion status is separate yield

                        # Yield the saved tool result object
                        if saved_tool_result_object:
                            tool_result_message_objects[tool_idx] = saved_tool_result_object
                            yield format_for_yield(saved_tool_result_object)
                        else:
                            logging.error(
                                f"Failed to save tool result for index {tool_idx}, not yielding result message.")
                            self.trace.event(name="failed_to_save_tool_result_for_index", level="ERROR",
                                             status_message=(
                                                 f"Failed to save tool result for index {tool_idx}, not yielding result message."))
                            # Optionally yield error status for saving failure?

            # --- Final Finish Status ---
            if finish_reason and finish_reason != "xml_tool_limit_reached":
                finish_content = {"status_type": "finish", "finish_reason": finish_reason}
                finish_msg_obj = await self.add_message(
                    type="status", content=finish_content,
                    is_llm_message=False, metadata={"thread_run_id": thread_run_id}
                )
                if finish_msg_obj: yield format_for_yield(finish_msg_obj)

            # Check if agent should terminate after processing pending tools
            if agent_should_terminate:
                logging.info(
                    "Agent termination requested after executing ask/complete tool. Stopping further processing.")
                self.trace.event(name="agent_termination_requested", level="DEFAULT",
                                 status_message="Agent termination requested after executing ask/complete tool. Stopping further processing.")

                # Set finish reason to indicate termination
                finish_reason = "agent_terminated"

                # Save and yield termination status
                finish_content = {"status_type": "finish", "finish_reason": "agent_terminated"}
                finish_msg_obj = await self.add_message(
                    type="status", content=finish_content,
                    is_llm_message=False, metadata={"thread_run_id": thread_run_id}
                )
                if finish_msg_obj: yield format_for_yield(finish_msg_obj)

                # Save assistant_response_end BEFORE terminating
                if last_assistant_message_object:
                    try:
                        # Calculate response time if we have timing data
                        if streaming_metadata["first_chunk_time"] and streaming_metadata["last_chunk_time"]:
                            streaming_metadata["response_ms"] = (streaming_metadata["last_chunk_time"] -
                                                                 streaming_metadata["first_chunk_time"]) * 1000

                        # Create a LiteLLM-like response object for streaming (before termination)
                        # Check if we have any actual usage data
                        has_usage_data = (
                                streaming_metadata["usage"]["prompt_tokens"] > 0 or
                                streaming_metadata["usage"]["completion_tokens"] > 0 or
                                streaming_metadata["usage"]["total_tokens"] > 0
                        )

                        assistant_end_content = {
                            "choices": [
                                {
                                    "finish_reason": finish_reason or "stop",
                                    "index": 0,
                                    "message": {
                                        "role": "assistant",
                                        "content": accumulated_content,
                                        "tool_calls": complete_native_tool_calls or None
                                    }
                                }
                            ],
                            "created": streaming_metadata.get("created"),
                            "model": streaming_metadata.get("model", llm_model),
                            "usage": streaming_metadata["usage"],  # Always include usage like LiteLLM does
                            "streaming": True,  # Add flag to indicate this was reconstructed from streaming
                        }

                        # Only include response_ms if we have timing data
                        if streaming_metadata.get("response_ms"):
                            assistant_end_content["response_ms"] = streaming_metadata["response_ms"]

                        await self.add_message(
                            type="assistant_response_end",
                            content=assistant_end_content,
                            is_llm_message=False,
                            metadata={"thread_run_id": thread_run_id}
                        )
                        logging.info("Assistant response end saved for stream (before termination)")
                    except Exception as e:
                        logging.error(f"Error saving assistant response end for stream (before termination): {str(e)}")
                        self.trace.event(name="error_saving_assistant_response_end_for_stream_before_termination",
                                         level="ERROR", status_message=(
                                f"Error saving assistant response end for stream (before termination): {str(e)}"))

                # Skip all remaining processing and go to finally block
                return

            # --- Save and Yield assistant_response_end ---
            # Only save assistant_response_end if not auto-continuing (response is actually complete)
            if not should_auto_continue:
                if last_assistant_message_object:  # Only save if assistant message was saved
                    try:
                        # Calculate response time if we have timing data
                        if streaming_metadata["first_chunk_time"] and streaming_metadata["last_chunk_time"]:
                            streaming_metadata["response_ms"] = (streaming_metadata["last_chunk_time"] -
                                                                 streaming_metadata["first_chunk_time"]) * 1000

                        # Create a LiteLLM-like response object for streaming
                        # Check if we have any actual usage data
                        has_usage_data = (
                                streaming_metadata["usage"]["prompt_tokens"] > 0 or
                                streaming_metadata["usage"]["completion_tokens"] > 0 or
                                streaming_metadata["usage"]["total_tokens"] > 0
                        )

                        assistant_end_content = {
                            "choices": [
                                {
                                    "finish_reason": finish_reason or "stop",
                                    "index": 0,
                                    "message": {
                                        "role": "assistant",
                                        "content": accumulated_content,
                                        "tool_calls": complete_native_tool_calls or None
                                    }
                                }
                            ],
                            "created": streaming_metadata.get("created"),
                            "model": streaming_metadata.get("model", llm_model),
                            "usage": streaming_metadata["usage"],  # Always include usage like LiteLLM does
                            "streaming": True,  # Add flag to indicate this was reconstructed from streaming
                        }

                        # Only include response_ms if we have timing data
                        if streaming_metadata.get("response_ms"):
                            assistant_end_content["response_ms"] = streaming_metadata["response_ms"]

                        await self.add_message(
                            type="assistant_response_end",
                            content=assistant_end_content,
                            is_llm_message=False,
                            metadata={"thread_run_id": thread_run_id}
                        )
                        logging.info("Assistant response end saved for stream")
                    except Exception as e:
                        logging.error(f"Error saving assistant response end for stream: {str(e)}")
                        self.trace.event(name="error_saving_assistant_response_end_for_stream", level="ERROR",
                                         status_message=(f"Error saving assistant response end for stream: {str(e)}"))

        except Exception as e:
            logging.error(f"Error processing stream: {str(e)}", exc_info=True)
            self.trace.event(name="error_processing_stream", level="ERROR",
                             status_message=(f"Error processing stream: {str(e)}"))
            # Save and yield error status message

            err_content = {"role": "system", "status_type": "error", "message": str(e)}
            if (not "AnthropicException - Overloaded" in str(e)):
                err_msg_obj = await self.add_message(
                    type="status", content=err_content,
                    is_llm_message=False,
                    metadata={"thread_run_id": thread_run_id if 'thread_run_id' in locals() else None}
                )
                if err_msg_obj: yield format_for_yield(err_msg_obj)  # Yield the saved error message
                # Re-raise the same exception (not a new one) to ensure proper error propagation
                logging.critical(f"Re-raising error to stop further processing: {str(e)}")
                self.trace.event(name="re_raising_error_to_stop_further_processing", level="ERROR",
                                 status_message=(f"Re-raising error to stop further processing: {str(e)}"))
            else:
                logging.error(f"AnthropicException - Overloaded detected - Falling back to OpenRouter: {str(e)}",
                             exc_info=True)
                self.trace.event(name="anthropic_exception_overloaded_detected", level="ERROR", status_message=(
                    f"AnthropicException - Overloaded detected - Falling back to OpenRouter: {str(e)}"))
            raise  # Use bare 'raise' to preserve the original exception with its traceback

        finally:
            # Update continuous state for potential auto-continue
            if should_auto_continue:
                continuous_state['accumulated_content'] = accumulated_content
                continuous_state['sequence'] = __sequence

                logging.info(f"Updated continuous state for auto-continue with {len(accumulated_content)} chars")
            else:
                # Save and Yield the final thread_run_end status (only if not auto-continuing and finish_reason is not 'length')
                try:
                    end_content = {"status_type": "thread_run_end"}
                    end_msg_obj = await self.add_message(
                        type="status", content=end_content,
                        is_llm_message=False,
                        metadata={"thread_run_id": thread_run_id if 'thread_run_id' in locals() else None}
                    )
                    if end_msg_obj: yield format_for_yield(end_msg_obj)
                except Exception as final_e:
                    logging.error(f"Error in finally block: {str(final_e)}", exc_info=True)
                    self.trace.event(name="error_in_finally_block", level="ERROR",
                                     status_message=(f"Error in finally block: {str(final_e)}"))
