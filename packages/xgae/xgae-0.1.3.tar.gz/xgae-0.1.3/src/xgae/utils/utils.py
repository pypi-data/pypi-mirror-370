import logging
import os
import sys
import datetime

from typing import Any, Dict

def handle_error(e: Exception) -> None:
    import traceback

    logging.error("An error occurred: %s", str(e))
    logging.error("Traceback details:\n%s", traceback.format_exc())
    raise (e) from e

def read_file(file_path: str) -> str:
    if not os.path.exists(file_path):
        logging.error(f"File '{file_path}' not found")
        raise Exception(f"File '{file_path}' not found")

    try:
        with open(file_path, "r", encoding="utf-8") as template_file:
            content = template_file.read()
        return content
    except Exception as e:
        logging.error(f"Read file '{file_path}' failed")
        handle_error(e)

def format_file_with_args(file_content:str, args: Dict[str, Any])-> str:
    from io import StringIO

    formated = file_content
    original_stdout = sys.stdout
    buffer = StringIO()
    sys.stdout = buffer
    try:
        code = f"print(f\"\"\"{file_content}\"\"\")"
        exec(code, args)
        formated = buffer.getvalue()
    finally:
        sys.stdout = original_stdout

    return formated