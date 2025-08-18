import logging
import os
import traceback

from langfuse import Langfuse


class XGAError(Exception):
    """Custom exception for errors in the XGA system."""
    pass

langfuse: Langfuse = None

def setup_langfuse() -> None:
    env_public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    env_secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    env_host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
    global langfuse
    if env_public_key and env_secret_key:
        langfuse = Langfuse(tracing_enabled=True,
                            public_key=env_public_key,
                            secret_key=env_secret_key,
                            host=env_host)
        logging.info("utils.setup_langfuse: Langfuse initialized!")
    else:
        langfuse = Langfuse(tracing_enabled=False)
        logging.warning("utils.setup_langfuse: Langfuse is disabled!")

def setup_logging() -> None:
    env_log_level = os.getenv("LOG_LEVEL", "INFO")
    env_log_file = os.getenv("LOG_FILE", "log/xga.log")
    log_level = getattr(logging, env_log_level.upper(), logging.INFO)

    log_dir = os.path.dirname(env_log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    else:
        os.remove(env_log_file)

    logger = logging.getLogger()
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    import colorlog

    log_colors = {
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white'
    }

    console_formatter = colorlog.ColoredFormatter('%(log_color)s%(asctime)s - %(levelname)-8s%(reset)s %(white)s%(message)s',
        log_colors=log_colors,
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    file_formatter = logging.Formatter(
        '%(asctime)s -%(levelname)-8s  %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)

    file_handler = logging.FileHandler(env_log_file, encoding='utf-8')
    file_handler.setFormatter(file_formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.setLevel(log_level)

    logging.info(f"Logger is initialized, log_level={env_log_level}, log_file={env_log_file}")


def handle_error(e: Exception) -> None:
    logging.error("An error occurred: %s", str(e))
    logging.error("Traceback details:\n%s", traceback.format_exc())
    raise (e) from e

def read_file(file_path: str) -> str:
    if not os.path.exists(file_path):
        logging.error(f"File '{file_path}' not found")
        raise XGAError(f"File '{file_path}' not found")

    try:
        with open(file_path, "r", encoding="utf-8") as template_file:
            content = template_file.read()
        return content
    except Exception as e:
        logging.error(f"Read file '{file_path}' failed")
        handle_error(e)

def setup_xga_env() -> None:
    from dotenv import load_dotenv
    load_dotenv()
    setup_logging()
    setup_langfuse()

if __name__ == "__main__":
    try:
        setup_xga_env()
        trace_id = langfuse.create_trace_id()
        print(f"trace_id={trace_id}")
    except Exception as e:
        handle_error(e)