import datetime

from typing import Optional, List

from xga_base import XGAToolSchema
from xgae.utils.setup_env import read_file, XGAError


class XGAPromptBuilder():
    def __init__(self,
                 prompt_template: Optional[str] = None,
                 prompt_template_file: Optional[str] = None):
        self.system_prompt_template = None
        if prompt_template:
            self.system_prompt_template = prompt_template
        elif prompt_template_file:
            self.system_prompt_template = read_file(prompt_template_file)
        else:
            _system_prompt_template = read_file("templates/system_prompt_template.txt")
            self.system_prompt_template = _system_prompt_template.format(
                current_date=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d'),
                current_time=datetime.datetime.now(datetime.timezone.utc).strftime('%H:%M:%S'),
                current_year=datetime.datetime.now(datetime.timezone.utc).strftime('%Y')
            )


    def build_system_prompt(self, model_name:str, prompt_template: Optional[str]=None)-> str:
        system_prompt = prompt_template if prompt_template else self.system_prompt_template

        return system_prompt


    def build_general_tool_prompt(self, model_name:str, prompt_template: str, tool_schemas:List[XGAToolSchema])-> str:
        pass


    def build_custom_tool_prompt(self, model_name:str, prompt_template: str, tool_schemas:List[XGAToolSchema])-> str:
        pass
