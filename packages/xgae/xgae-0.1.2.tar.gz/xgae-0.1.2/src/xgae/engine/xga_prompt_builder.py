import datetime
import sys
import json

from typing import Optional, List
from io import StringIO

from xga_base import XGAToolSchema
from xgae.utils.setup_env import read_file, XGAError


class XGAPromptBuilder():
    def __init__(self, system_prompt_template: Optional[str] = None):
        self.system_prompt = None
        if system_prompt_template:
            self.system_prompt = system_prompt_template

    def build_system_prompt(self, model_name: str, system_prompt: Optional[str]=None)-> str:
        task_system_prompt = system_prompt if system_prompt else self.system_prompt
        if task_system_prompt is None:
            task_system_prompt = self._load_default_system_prompt(model_name)
        return task_system_prompt

    def build_general_tool_prompt(self, tool_schemas:List[XGAToolSchema])-> str:
        tool_prompt = ""
        tool_schemas = tool_schemas or []
        if len(tool_schemas) > 0:
            tool_prompt = read_file("templates/general_tool_prompt_template.txt")
            example_prompt = ""
            openai_schemas = []
            for tool_schema in tool_schemas:
                openai_schema = {}
                openai_schema["type"] = "function"
                openai_function = {}
                openai_schema["function"] = openai_function

                openai_function["name"] = tool_schema.tool_name
                openai_function["description"] = tool_schema.description if tool_schema.description else 'No description available'

                openai_parameters = {}
                input_schema = tool_schema.input_schema
                openai_function["parameters"] = openai_parameters
                openai_parameters["type"] = input_schema["type"]
                openai_parameters["properties"] = input_schema.get("properties", [])
                openai_parameters["required"] = input_schema["required"]

                openai_schemas.append(openai_schema)

                metadata = tool_schema.metadata or {}
                example = metadata.get("example", None)
                if example:
                    example_prompt += f"\n{example}\n"

            schema_prompt = json.dumps(openai_schemas, ensure_ascii=False, indent=2)
            tool_prompt = tool_prompt.format(tool_schemas=schema_prompt, tool_examples=example_prompt)
        return tool_prompt


    def build_custom_tool_prompt(self, tool_schemas:List[XGAToolSchema])-> str:
        tool_prompt = ""
        tool_schemas = tool_schemas or []
        if len(tool_schemas) > 0:
            tool_prompt = read_file("templates/custom_tool_prompt_template.txt")
            tool_info = ""
            for tool_schema in tool_schemas:
                description = tool_schema.description if tool_schema.description else 'No description available'
                tool_info += f"- **{tool_schema.tool_name}**: {description}\n"
                tool_info += f"  Parameters: {tool_schema.input_schema}\n"
            tool_prompt = tool_prompt.replace("{tool_schemas}", tool_info)

        return tool_prompt

    def _load_default_system_prompt(self, model_name) -> Optional[str]:
        if "gemini-2.5-flash" in model_name.lower() and "gemini-2.5-pro" not in model_name.lower():
            org_prompt_template = read_file("templates/gemini_system_prompt_template.txt")
        else:
            org_prompt_template = read_file("templates/system_prompt_template.txt")

        original_stdout = sys.stdout
        buffer = StringIO()
        sys.stdout = buffer
        try:
            namespace = {
                "datetime": datetime,
                "__builtins__": __builtins__
            }
            code = f"print(f\"\"\"{org_prompt_template}\"\"\")"
            exec(code, namespace)
            system_prompt_template = buffer.getvalue()
        finally:
            sys.stdout = original_stdout

        system_prompt = system_prompt_template.format(
            current_date=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d'),
            current_time=datetime.datetime.now(datetime.timezone.utc).strftime('%H:%M:%S'),
            current_year=datetime.datetime.now(datetime.timezone.utc).strftime('%Y')
        )

        if "anthropic" not in model_name.lower():
            sample_response = read_file("templates/system_prompt_response_sample.txt")
            system_prompt = system_prompt + "\n\n <sample_assistant_response>" + sample_response + "</sample_assistant_response>"

        return system_prompt

if __name__ == "__main__":

    prompt_builder = XGAPromptBuilder()
    prompt = prompt_builder.build_system_prompt("openai/qwen3-235b-a22b")

    # system_prompt = read_file("templates/scp_test_prompt.txt")
    # prompt = prompt_builder.build_system_prompt("openai/qwen3-235b-a22b", system_prompt=system_prompt)

    print(prompt)


