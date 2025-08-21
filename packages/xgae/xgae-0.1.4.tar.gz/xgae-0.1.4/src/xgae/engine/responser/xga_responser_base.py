import asyncio
import json
import logging
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple, Union, Literal, Callable,TypedDict,AsyncGenerator
from abc import ABC, abstractmethod

from xgae.engine.xga_base import XGAToolResult, XGAContextMsg, XGAToolBox
# from xgae.utils.setup_env import langfuse
from xgae.utils.json_helpers import (
    safe_json_parse,
    format_for_yield
)
from xgae.utils.xml_tool_parser import XMLToolParser

# Type alias for XML result adding strategy
XmlAddingStrategy = Literal["user_message", "assistant_message", "inline_edit"]

# Type alias for tool execution strategy
ToolExecutionStrategy = Literal["sequential", "parallel"]

class TaskResponseContext(TypedDict, total=False):
    is_stream: bool
    task_id: str
    task_run_id: str
    trace_id: str
    model_name: str
    max_xml_tool_calls: int
    add_context_msg: Callable
    tool_box: XGAToolBox
    tool_execution_strategy: Literal["sequential", "parallel"]
    xml_adding_strategy: Literal["user_message", "assistant_message", "inline_edit"]


class TaskRunContinuousState(TypedDict, total=False):
    accumulated_content: str
    auto_continue_count: int
    auto_continue: bool

class Span:
    def end(self, **kwargs):
        pass

class Trace:
    def event(self, **kwargs):
        pass

    def span(self, **kwargs):
        return Span()



@dataclass
class ToolExecutionContext:
    """Context for a tool execution including call details, result, and display info."""
    tool_call: Dict[str, Any]
    tool_index: int
    result: Optional[XGAToolResult] = None
    function_name: Optional[str] = None
    xml_tag_name: Optional[str] = None
    error: Optional[Exception] = None
    assistant_message_id: Optional[str] = None
    parsing_details: Optional[Dict[str, Any]] = None


@dataclass
class ProcessorConfig:
    """
    Configuration for response processing and tool execution.

    This class controls how the LLM's responses are processed, including how tool calls
    are detected, executed, and their results handled.

    Attributes:
        xml_tool_calling: Enable XML-based tool call detection (<tool>...</tool>)
        native_tool_calling: Enable OpenAI-style function calling format
        execute_tools: Whether to automatically execute detected tool calls
        execute_on_stream: For streaming, execute tools as they appear vs. at the end
        tool_execution_strategy: How to execute multiple tools ("sequential" or "parallel")
        xml_adding_strategy: How to add XML tool results to the conversation
        max_xml_tool_calls: Maximum number of XML tool calls to process (0 = no limit)
    """

    xml_tool_calling: bool = True
    native_tool_calling: bool = False

    execute_tools: bool = True
    execute_on_stream: bool = False
    tool_execution_strategy: ToolExecutionStrategy = "sequential"
    xml_adding_strategy: XmlAddingStrategy = "assistant_message"
    max_xml_tool_calls: int = 0  # 0 means no limit

    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.xml_tool_calling is False and self.native_tool_calling is False and self.execute_tools:
            raise ValueError(
                "At least one tool calling format (XML or native) must be enabled if execute_tools is True")

        if self.xml_adding_strategy not in ["user_message", "assistant_message", "inline_edit"]:
            raise ValueError("xml_adding_strategy must be 'user_message', 'assistant_message', or 'inline_edit'")

        if self.max_xml_tool_calls < 0:
            raise ValueError("max_xml_tool_calls must be a non-negative integer (0 = no limit)")


class TaskResponseProcessor(ABC):
    def __init__(self, response_context: TaskResponseContext):
        self.response_context = response_context

        self.task_id = response_context.get("task_id", "")
        self.task_run_id = response_context.get("task_run_id", "")

        # Initialize the XML parser
        self.trace = Trace()

        self.add_message = response_context.get("add_context_msg")
        self._add_message_with_agent_info =  self.add_message
        self.tool_box = response_context.get("tool_box")

        self.xml_parser = XMLToolParser()

    @abstractmethod
    async def process_response(self,
                               llm_response: AsyncGenerator,
                               prompt_messages: List[Dict[str, Any]],
                               continuous_state: Optional[TaskRunContinuousState] = None
                               ) -> AsyncGenerator[Dict[str, Any], None]:
        pass

    async def _yield_message(self, message_obj: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Helper to yield a message with proper formatting.

        Ensures that content and metadata are JSON strings for client compatibility.
        """
        if message_obj:
            return format_for_yield(message_obj)
        return None



    def _extract_xml_chunks(self, content: str) -> List[str]:
        """Extract complete XML chunks using start and end pattern matching."""
        chunks = []
        pos = 0

        try:
            # First, look for new format <function_calls> blocks
            start_pattern = '<function_calls>'
            end_pattern = '</function_calls>'

            while pos < len(content):
                # Find the next function_calls block
                start_pos = content.find(start_pattern, pos)
                if start_pos == -1:
                    break

                # Find the matching end tag
                end_pos = content.find(end_pattern, start_pos)
                if end_pos == -1:
                    break

                # Extract the complete block including tags
                chunk_end = end_pos + len(end_pattern)
                chunk = content[start_pos:chunk_end]
                chunks.append(chunk)

                # Move position past this chunk
                pos = chunk_end

            # If no new format found, fall back to old format for backwards compatibility
            if not chunks:
                pos = 0
                while pos < len(content):
                    # Find the next tool tag
                    next_tag_start = -1
                    current_tag = None

                    # Find the earliest occurrence of any registered tool function name
                    # Check for available function names
                    #available_functions = self.tool_registry.get_available_functions()
                    available_functions = self.tool_box.get_task_tool_names(self.task_id)
                    for func_name in available_functions:
                        # Convert function name to potential tag name (underscore to dash)
                        tag_name = func_name.replace('_', '-')
                        start_pattern = f'<{tag_name}'
                        tag_pos = content.find(start_pattern, pos)

                        if tag_pos != -1 and (next_tag_start == -1 or tag_pos < next_tag_start):
                            next_tag_start = tag_pos
                            current_tag = tag_name

                    if next_tag_start == -1 or not current_tag:
                        break

                    # Find the matching end tag
                    end_pattern = f'</{current_tag}>'
                    tag_stack = []
                    chunk_start = next_tag_start
                    current_pos = next_tag_start

                    while current_pos < len(content):
                        # Look for next start or end tag of the same type
                        next_start = content.find(f'<{current_tag}', current_pos + 1)
                        next_end = content.find(end_pattern, current_pos)

                        if next_end == -1:  # No closing tag found
                            break

                        if next_start != -1 and next_start < next_end:
                            # Found nested start tag
                            tag_stack.append(next_start)
                            current_pos = next_start + 1
                        else:
                            # Found end tag
                            if not tag_stack:  # This is our matching end tag
                                chunk_end = next_end + len(end_pattern)
                                chunk = content[chunk_start:chunk_end]
                                chunks.append(chunk)
                                pos = chunk_end
                                break
                            else:
                                # Pop nested tag
                                tag_stack.pop()
                                current_pos = next_end + 1

                    if current_pos >= len(content):  # Reached end without finding closing tag
                        break

                    pos = max(pos + 1, current_pos)

        except Exception as e:
            logging.error(f"Error extracting XML chunks: {e}")
            logging.error(f"Content was: {content}")
            self.trace.event(name="error_extracting_xml_chunks", level="ERROR",
                              status_message=(f"Error extracting XML chunks: {e}"), metadata={"content": content})

        return chunks

    def _parse_xml_tool_call(self, xml_chunk: str) -> Optional[Tuple[Dict[str, Any], Dict[str, Any]]]:
        """Parse XML chunk into tool call format and return parsing details.

        Returns:
            Tuple of (tool_call, parsing_details) or None if parsing fails.
            - tool_call: Dict with 'function_name', 'xml_tag_name', 'arguments'
            - parsing_details: Dict with 'attributes', 'elements', 'text_content', 'root_content'
        """
        try:
            # Check if this is the new format (contains <function_calls>)
            if '<function_calls>' in xml_chunk and '<invoke' in xml_chunk:
                # Use the new XML parser
                parsed_calls = self.xml_parser.parse_content(xml_chunk)

                if not parsed_calls:
                    logging.error(f"No tool calls found in XML chunk: {xml_chunk}")
                    return None

                # Take the first tool call (should only be one per chunk)
                xml_tool_call = parsed_calls[0]

                # Convert to the expected format
                tool_call = {
                    "function_name": xml_tool_call.function_name,
                    "xml_tag_name": xml_tool_call.function_name.replace('_', '-'),  # For backwards compatibility
                    "arguments": xml_tool_call.parameters
                }

                # Include the parsing details
                parsing_details = xml_tool_call.parsing_details
                parsing_details["raw_xml"] = xml_tool_call.raw_xml

                logging.debug(f"Parsed new format tool call: {tool_call}")
                return tool_call, parsing_details

            # If not the expected <function_calls><invoke> format, return None
            logging.error(f"XML chunk does not contain expected <function_calls><invoke> format: {xml_chunk}")
            return None

        except Exception as e:
            logging.error(f"Error parsing XML chunk: {e}")
            logging.error(f"XML chunk was: {xml_chunk}")
            self.trace.event(name="error_parsing_xml_chunk", level="ERROR",
                              status_message=(f"Error parsing XML chunk: {e}"), metadata={"xml_chunk": xml_chunk})
            return None

    def _parse_xml_tool_calls(self, content: str) -> List[Dict[str, Any]]:
        """Parse XML tool calls from content string.

        Returns:
            List of dictionaries, each containing {'tool_call': ..., 'parsing_details': ...}
        """
        parsed_data = []

        try:
            xml_chunks = self._extract_xml_chunks(content)

            for xml_chunk in xml_chunks:
                result = self._parse_xml_tool_call(xml_chunk)
                if result:
                    tool_call, parsing_details = result
                    parsed_data.append({
                        "tool_call": tool_call,
                        "parsing_details": parsing_details
                    })

        except Exception as e:
            logging.error(f"Error parsing XML tool calls: {e}", exc_info=True)
            self.trace.event(name="error_parsing_xml_tool_calls", level="ERROR",
                             status_message=(f"Error parsing XML tool calls: {e}"), metadata={"content": content})

        return parsed_data

    # Tool execution methods
    async def _execute_tool(self, tool_call: Dict[str, Any]) -> XGAToolResult:
        """Execute a single tool call and return the result."""
        span = self.trace.span(name=f"execute_tool.{tool_call['function_name']}", input=tool_call["arguments"])
        try:
            function_name = tool_call["function_name"]
            arguments = tool_call["arguments"]

            logging.info(f"Executing tool: {function_name} with arguments: {arguments}")
            self.trace.event(name="executing_tool", level="DEFAULT",
                             status_message=(f"Executing tool: {function_name} with arguments: {arguments}"))

            if isinstance(arguments, str):
                try:
                    arguments = safe_json_parse(arguments)
                except json.JSONDecodeError:
                    arguments = {"text": arguments} # @todo modify

            # Get available functions from tool registry
            #available_functions = self.tool_registry.get_available_functions()
            result = None
            available_function_names = self.tool_box.get_task_tool_names(self.task_id)
            if function_name in available_function_names:
                result = await self.tool_box.call_tool(self.task_id, function_name, arguments)
            else:
                logging.error(f"Tool function '{function_name}' not found in registry")
                result = XGAToolResult(success=False, output=f"Tool function '{function_name}' not found")
            logging.info(f"Tool execution complete: {function_name} -> {result}")
            span.end(status_message="tool_executed", output=result)
            return result
        except Exception as e:
            logging.error(f"Error executing tool {tool_call['function_name']}: {str(e)}", exc_info=True)
            span.end(status_message="tool_execution_error", output=f"Error executing tool: {str(e)}", level="ERROR")
            return XGAToolResult(success=False, output=f"Error executing tool: {str(e)}")

    async def _execute_tools(
            self,
            tool_calls: List[Dict[str, Any]],
            execution_strategy: ToolExecutionStrategy = "sequential"
    ) -> List[Tuple[Dict[str, Any], XGAToolResult]]:
        logging.info(f"Executing {len(tool_calls)} tools with strategy: {execution_strategy}")
        self.trace.event(name="executing_tools_with_strategy", level="DEFAULT",
                         status_message=(f"Executing {len(tool_calls)} tools with strategy: {execution_strategy}"))

        if execution_strategy == "sequential":
            return await self._execute_tools_sequentially(tool_calls)
        elif execution_strategy == "parallel":
            return await self._execute_tools_in_parallel(tool_calls)
        else:
            logging.warning(f"Unknown execution strategy: {execution_strategy}, falling back to sequential")
            return await self._execute_tools_sequentially(tool_calls)

    async def _execute_tools_sequentially(self, tool_calls: List[Dict[str, Any]]) -> List[
        Tuple[Dict[str, Any], XGAToolResult]]:
        """Execute tool calls sequentially and return results.

        This method executes tool calls one after another, waiting for each tool to complete
        before starting the next one. This is useful when tools have dependencies on each other.

        Args:
            tool_calls: List of tool calls to execute

        Returns:
            List of tuples containing the original tool call and its result
        """
        if not tool_calls:
            return []

        try:
            tool_names = [t.get('function_name', 'unknown') for t in tool_calls]
            logging.info(f"Executing {len(tool_calls)} tools sequentially: {tool_names}")
            self.trace.event(name="executing_tools_sequentially", level="DEFAULT",
                             status_message=(f"Executing {len(tool_calls)} tools sequentially: {tool_names}"))

            results = []
            for index, tool_call in enumerate(tool_calls):
                tool_name = tool_call.get('function_name', 'unknown')
                logging.debug(f"Executing tool {index + 1}/{len(tool_calls)}: {tool_name}")

                try:
                    result = await self._execute_tool(tool_call)
                    results.append((tool_call, result))
                    logging.debug(f"Completed tool {tool_name} with success={result.success}")

                    # Check if this is a terminating tool (ask or complete)
                    if tool_name in ['ask', 'complete']:
                        logging.info(f"Terminating tool '{tool_name}' executed. Stopping further tool execution.")
                        self.trace.event(name="terminating_tool_executed", level="DEFAULT", status_message=(
                            f"Terminating tool '{tool_name}' executed. Stopping further tool execution."))
                        break  # Stop executing remaining tools

                except Exception as e:
                    logging.error(f"Error executing tool {tool_name}: {str(e)}")
                    self.trace.event(name="error_executing_tool", level="ERROR",
                                     status_message=(f"Error executing tool {tool_name}: {str(e)}"))
                    error_result = XGAToolResult(success=False, output=f"Error executing tool: {str(e)}")
                    results.append((tool_call, error_result))

            logging.info(f"Sequential execution completed for {len(results)} tools (out of {len(tool_calls)} total)")
            self.trace.event(name="sequential_execution_completed", level="DEFAULT", status_message=(
                f"Sequential execution completed for {len(results)} tools (out of {len(tool_calls)} total)"))
            return results

        except Exception as e:
            logging.error(f"Error in sequential tool execution: {str(e)}", exc_info=True)
            # Return partial results plus error results for remaining tools
            completed_results = results if 'results' in locals() else []
            completed_tool_names = [r[0].get('function_name', 'unknown') for r in completed_results]
            remaining_tools = [t for t in tool_calls if t.get('function_name', 'unknown') not in completed_tool_names]

            # Add error results for remaining tools
            error_results = [(tool, XGAToolResult(success=False, output=f"Execution error: {str(e)}"))
                             for tool in remaining_tools]

            return completed_results + error_results

    async def _execute_tools_in_parallel(self, tool_calls: List[Dict[str, Any]]) -> List[Tuple[Dict[str, Any], XGAToolResult]]:
        if not tool_calls:
            return []

        try:
            tool_names = [t.get('function_name', 'unknown') for t in tool_calls]
            logging.info(f"Executing {len(tool_calls)} tools in parallel: {tool_names}")
            self.trace.event(name="executing_tools_in_parallel", level="DEFAULT",
                             status_message=(f"Executing {len(tool_calls)} tools in parallel: {tool_names}"))

            # Create tasks for all tool calls
            tasks = [self._execute_tool(tool_call) for tool_call in tool_calls]

            # Execute all tasks concurrently with error handling
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results and handle any exceptions
            processed_results = []
            for i, (tool_call, result) in enumerate(zip(tool_calls, results)):
                if isinstance(result, Exception):
                    logging.error(f"Error executing tool {tool_call.get('function_name', 'unknown')}: {str(result)}")
                    self.trace.event(name="error_executing_tool", level="ERROR", status_message=(
                        f"Error executing tool {tool_call.get('function_name', 'unknown')}: {str(result)}"))
                    # Create error result
                    error_result = XGAToolResult(success=False, output=f"Error executing tool: {str(result)}")
                    processed_results.append((tool_call, error_result))
                else:
                    processed_results.append((tool_call, result))

            logging.info(f"Parallel execution completed for {len(tool_calls)} tools")
            self.trace.event(name="parallel_execution_completed", level="DEFAULT",
                             status_message=(f"Parallel execution completed for {len(tool_calls)} tools"))
            return processed_results

        except Exception as e:
            logging.error(f"Error in parallel tool execution: {str(e)}", exc_info=True)
            self.trace.event(name="error_in_parallel_tool_execution", level="ERROR",
                             status_message=(f"Error in parallel tool execution: {str(e)}"))
            # Return error results for all tools if the gather itself fails
            return [(tool_call, XGAToolResult(success=False, output=f"Execution error: {str(e)}"))
                    for tool_call in tool_calls]

    def _add_tool_result(
            self,
            thread_id: str,
            tool_call: Dict[str, Any],
            result: XGAToolResult,
            strategy: Union[XmlAddingStrategy, str] = "assistant_message",
            assistant_message_id: Optional[str] = None,
            parsing_details: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:  # Return the full message object
        try:
            message_obj = None  # Initialize message_obj

            # Create metadata with assistant_message_id if provided
            metadata = {}
            if assistant_message_id:
                metadata["assistant_message_id"] = assistant_message_id
                logging.info(f"Linking tool result to assistant message: {assistant_message_id}")
                self.trace.event(name="linking_tool_result_to_assistant_message", level="DEFAULT",
                                 status_message=(f"Linking tool result to assistant message: {assistant_message_id}"))

            # --- Add parsing details to metadata if available ---
            if parsing_details:
                metadata["parsing_details"] = parsing_details
                logging.info("Adding parsing_details to tool result metadata")
                self.trace.event(name="adding_parsing_details_to_tool_result_metadata", level="DEFAULT",
                                 status_message=(f"Adding parsing_details to tool result metadata"),
                                 metadata={"parsing_details": parsing_details})
            # ---

            # Check if this is a native function call (has id field)
            if "id" in tool_call:
                # Format as a proper tool message according to OpenAI spec
                function_name = tool_call.get("function_name", "")

                # Format the tool result content - tool role needs string content
                if isinstance(result, str):
                    content = result
                elif hasattr(result, 'output'):
                    # If it's a XGAToolResult object
                    if isinstance(result.output, dict) or isinstance(result.output, list):
                        # If output is already a dict or list, convert to JSON string
                        content = json.dumps(result.output)
                    else:
                        # Otherwise just use the string representation
                        content = str(result.output)
                else:
                    # Fallback to string representation of the whole result
                    content = str(result)

                logging.info(f"Formatted tool result content: {content[:100]}...")
                self.trace.event(name="formatted_tool_result_content", level="DEFAULT",
                                 status_message=(f"Formatted tool result content: {content[:100]}..."))

                # Create the tool response message with proper format
                tool_message = {
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "name": function_name,
                    "content": content
                }

                logging.info(f"Adding native tool result for tool_call_id={tool_call['id']} with role=tool")
                self.trace.event(name="adding_native_tool_result_for_tool_call_id", level="DEFAULT", status_message=(
                    f"Adding native tool result for tool_call_id={tool_call['id']} with role=tool"))

                # Add as a tool message to the conversation history
                # This makes the result visible to the LLM in the next turn
                message_obj =  self.add_message(
                    type="tool",  # Special type for tool responses
                    content=tool_message,
                    is_llm_message=True,
                    metadata=metadata
                )
                return message_obj  # Return the full message object

            # For XML and other non-native tools, use the new structured format
            # Determine message role based on strategy
            result_role = "user" if strategy == "user_message" else "assistant"

            # Create two versions of the structured result
            # 1. Rich version for the frontend
            structured_result_for_frontend = self._create_structured_tool_result(tool_call, result, parsing_details,
                                                                                 for_llm=False)
            # 2. Concise version for the LLM
            structured_result_for_llm = self._create_structured_tool_result(tool_call, result, parsing_details,
                                                                            for_llm=True)

            # Add the message with the appropriate role to the conversation history
            # This allows the LLM to see the tool result in subsequent interactions
            result_message_for_llm = {
                "role": result_role,
                "content": json.dumps(structured_result_for_llm)
            }

            # Add rich content to metadata for frontend use
            if metadata is None:
                metadata = {}
            metadata['frontend_content'] = structured_result_for_frontend

            message_obj =  self._add_message_with_agent_info(
                type="tool",
                content=result_message_for_llm,  # Save the LLM-friendly version
                is_llm_message=True,
                metadata=metadata
            )

            # If the message was saved, modify it in-memory for the frontend before returning
            if message_obj:
                # The frontend expects the rich content in the 'content' field.
                # The DB has the rich content in metadata.frontend_content.
                # Let's reconstruct the message for yielding.
                message_for_yield = message_obj.copy()
                message_for_yield['content'] = structured_result_for_frontend
                return message_for_yield

            return message_obj  # Return the modified message object
        except Exception as e:
            logging.error(f"Error adding tool result: {str(e)}", exc_info=True)
            self.trace.event(name="error_adding_tool_result", level="ERROR",
                             status_message=(f"Error adding tool result: {str(e)}"),
                             metadata={"tool_call": tool_call, "result": result, "strategy": strategy,
                                       "assistant_message_id": assistant_message_id,
                                       "parsing_details": parsing_details})
            # Fallback to a simple message
            try:
                fallback_message = {
                    "role": "user",
                    "content": str(result)
                }
                message_obj = self.add_message(
                    type="tool",
                    content=fallback_message,
                    is_llm_message=True,
                    metadata={"assistant_message_id": assistant_message_id} if assistant_message_id else {}
                )
                return message_obj  # Return the full message object
            except Exception as e2:
                logging.error(f"Failed even with fallback message: {str(e2)}", exc_info=True)
                self.trace.event(name="failed_even_with_fallback_message", level="ERROR",
                                 status_message=(f"Failed even with fallback message: {str(e2)}"),
                                 metadata={"tool_call": tool_call, "result": result, "strategy": strategy,
                                           "assistant_message_id": assistant_message_id,
                                           "parsing_details": parsing_details})
                return None  # Return None on error

    def _create_structured_tool_result(self, tool_call: Dict[str, Any], result: XGAToolResult,
                                       parsing_details: Optional[Dict[str, Any]] = None, for_llm: bool = False):
        function_name = tool_call.get("function_name", "unknown")
        xml_tag_name = tool_call.get("xml_tag_name")
        arguments = tool_call.get("arguments", {})
        tool_call_id = tool_call.get("id")

        # Process the output - if it's a JSON string, parse it back to an object
        output = result.output if hasattr(result, 'output') else str(result)
        if isinstance(output, str):
            try:
                # Try to parse as JSON to provide structured data to frontend
                parsed_output = safe_json_parse(output)
                # If parsing succeeded and we got a dict/list, use the parsed version
                if isinstance(parsed_output, (dict, list)):
                    output = parsed_output
                # Otherwise keep the original string
            except Exception:
                # If parsing fails, keep the original string
                pass

        output_to_use = output
        # If this is for the LLM and it's an edit_file tool, create a concise output
        if for_llm and function_name == 'edit_file' and isinstance(output, dict):
            # The frontend needs original_content and updated_content to render diffs.
            # The concise version for the LLM was causing issues.
            # We will now pass the full output, and rely on the ContextManager to truncate if needed.
            output_to_use = output

        # Create the structured result
        structured_result_v1 = {
            "tool_execution": {
                "function_name": function_name,
                "xml_tag_name": xml_tag_name,
                "tool_call_id": tool_call_id,
                "arguments": arguments,
                "result": {
                    "success": result.success if hasattr(result, 'success') else True,
                    "output": output_to_use,  # This will be either rich or concise based on `for_llm`
                    "error": getattr(result, 'error', None) if hasattr(result, 'error') else None
                },
            }
        }

        return structured_result_v1

    def _create_tool_context(self, tool_call: Dict[str, Any], tool_index: int,
                             assistant_message_id: Optional[str] = None,
                             parsing_details: Optional[Dict[str, Any]] = None) -> ToolExecutionContext:
        """Create a tool execution context with display name and parsing details populated."""
        context = ToolExecutionContext(
            tool_call=tool_call,
            tool_index=tool_index,
            assistant_message_id=assistant_message_id,
            parsing_details=parsing_details
        )

        # Set function_name and xml_tag_name fields
        if "xml_tag_name" in tool_call:
            context.xml_tag_name = tool_call["xml_tag_name"]
            context.function_name = tool_call.get("function_name", tool_call["xml_tag_name"])
        else:
            # For non-XML tools, use function name directly
            context.function_name = tool_call.get("function_name", "unknown")
            context.xml_tag_name = None

        return context

    def _yield_and_save_tool_started(self, context: ToolExecutionContext, thread_id: str, thread_run_id: str) -> \
    Optional[Dict[str, Any]]:
        """Formats, saves, and returns a tool started status message."""
        tool_name = context.xml_tag_name or context.function_name
        content = {
            "role": "assistant", "status_type": "tool_started",
            "function_name": context.function_name, "xml_tag_name": context.xml_tag_name,
            "message": f"Starting execution of {tool_name}", "tool_index": context.tool_index,
            "tool_call_id": context.tool_call.get("id")  # Include tool_call ID if native
        }
        metadata = {"thread_run_id": thread_run_id}
        saved_message_obj =  self.add_message(
             type="status", content=content, is_llm_message=False, metadata=metadata
        )
        return saved_message_obj  # Return the full object (or None if saving failed)

    def _yield_and_save_tool_completed(self, context: ToolExecutionContext, tool_message_id: Optional[str],
                                             thread_id: str, thread_run_id: str) -> Optional[Dict[str, Any]]:
        """Formats, saves, and returns a tool completed/failed status message."""
        if not context.result:
            # Delegate to error saving if result is missing (e.g., execution failed)
            return  self._yield_and_save_tool_error(context, thread_id, thread_run_id)

        tool_name = context.xml_tag_name or context.function_name
        status_type = "tool_completed" if context.result.success else "tool_failed"
        message_text = f"Tool {tool_name} {'completed successfully' if context.result.success else 'failed'}"

        content = {
            "role": "assistant", "status_type": status_type,
            "function_name": context.function_name, "xml_tag_name": context.xml_tag_name,
            "message": message_text, "tool_index": context.tool_index,
            "tool_call_id": context.tool_call.get("id")
        }
        metadata = {"thread_run_id": thread_run_id}
        # Add the *actual* tool result message ID to the metadata if available and successful
        if context.result.success and tool_message_id:
            metadata["linked_tool_result_message_id"] = tool_message_id

        # <<< ADDED: Signal if this is a terminating tool >>>
        if context.function_name in ['ask', 'complete']:
            metadata["agent_should_terminate"] = "true"
            logging.info(f"Marking tool status for '{context.function_name}' with termination signal.")
            self.trace.event(name="marking_tool_status_for_termination", level="DEFAULT", status_message=(
                f"Marking tool status for '{context.function_name}' with termination signal."))
        # <<< END ADDED >>>

        saved_message_obj =  self.add_message(
             type="status", content=content, is_llm_message=False, metadata=metadata
        )
        return saved_message_obj

    def _yield_and_save_tool_error(self, context: ToolExecutionContext, thread_id: str, thread_run_id: str) -> \
    Optional[Dict[str, Any]]:
        """Formats, saves, and returns a tool error status message."""
        error_msg = str(context.error) if context.error else "Unknown error during tool execution"
        tool_name = context.xml_tag_name or context.function_name
        content = {
            "role": "assistant", "status_type": "tool_error",
            "function_name": context.function_name, "xml_tag_name": context.xml_tag_name,
            "message": f"Error executing tool {tool_name}: {error_msg}",
            "tool_index": context.tool_index,
            "tool_call_id": context.tool_call.get("id")
        }
        metadata = {"thread_run_id": thread_run_id}
        # Save the status message with is_llm_message=False
        saved_message_obj =  self.add_message(
            type="status", content=content, is_llm_message=False, metadata=metadata
        )
        return saved_message_obj
