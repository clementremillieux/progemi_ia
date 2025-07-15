"""Handle config and logger"""

import os

import logging

import platform

import configparser

from dotenv import load_dotenv

load_dotenv("config/.env")

config = configparser.ConfigParser()

config.read("config/app.ini")


class CustomFormatter(logging.Formatter):
    """Custom logger with colored output, aligned messages, and relative paths"""

    RED = "\033[31m"

    GREEN = "\033[92m"

    RESET = "\033[0m"

    ORANGE = "\033[33m"

    def format(self, record):
        """Format log records with color, alignment, and additional context"""

        if record.levelno == logging.INFO:
            level_name = self.GREEN + record.levelname + self.RESET

        elif record.levelno == logging.ERROR:
            level_name = self.RED + record.levelname + self.RESET

        elif record.levelno == logging.WARNING:
            level_name = self.ORANGE + record.levelname + self.RESET

        else:
            level_name = record.levelname

        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

        relative_path = os.path.relpath(record.pathname, project_root)

        module = record.module

        function_name = record.funcName

        line_no = record.lineno

        timestamp = self.formatTime(record, "%Y-%m-%d %H:%M:%S")

        dynamic_part = (
            f"{level_name} -> [{relative_path}.{module}.{function_name}.{line_no}]"
        )

        # Calculate the padding for alignment
        max_dynamic_length = 140

        padding = max(
            0, max_dynamic_length - len(dynamic_part) - len(timestamp) - 1
        )  # -1 for the space after timestamp

        # Format the message
        message = super(CustomFormatter, self).format(record)

        return f"{timestamp} {dynamic_part}:{' ' * padding} {message}"


def setup_logging():
    """setup the logging logger"""

    logger = logging.getLogger(EnvParam.LOGGER_NAME)

    if logger.hasHandlers():
        logger.handlers.clear()

    handler = logging.StreamHandler()

    handler.setFormatter(CustomFormatter("%(message)s"))

    if platform.system() == "Darwin":
        logger.setLevel(logging.DEBUG)

    else:
        logger.setLevel(logging.INFO)

    logger.addHandler(handler)

    logger.propagate = False


def load_param_str_config(section: str, param_name: str) -> str:
    """Load env param from .ini"""

    param: str = config.get(section, param_name)

    return param


def load_param_env_file(name: str) -> str:
    """Load env param from .env"""

    return str(os.getenv(name))


class EnvParam:
    """Handling all the env param in a class"""

    LOGGER_NAME: str = str(
        load_param_str_config(section="app", param_name="LOGGER_NAME")
    )

    VERSION: str = str(load_param_str_config(section="app", param_name="VERSION"))

    APP_NAME: str = str(load_param_str_config(section="app", param_name="APP_NAME"))

    GPT_O1: str = str(load_param_str_config(section="llm", param_name="GPT_O1"))

    GPT_O3: str = str(load_param_str_config(section="llm", param_name="GPT_O3"))

    GPT_4_1: str = str(load_param_str_config(section="llm", param_name="GPT_4_1"))

    GPT_4_1_MINI: str = str(
        load_param_str_config(section="llm", param_name="GPT_4_1_MINI")
    )

    GPT_4_MODEL_RESUME: str = str(
        load_param_str_config(section="llm", param_name="GPT_4_MODEL_RESUME")
    )

    GPT_3_MODEL: str = str(
        load_param_str_config(section="llm", param_name="GPT_3_MODEL")
    )

    GPT_4_OUTPUT: str = str(
        load_param_str_config(section="llm", param_name="GPT_4_OUTPUT")
    )

    GPT_4_MODEL_ANSWER: str = str(
        load_param_str_config(section="llm", param_name="GPT_4_MODEL_ANSWER")
    )

    GPT_REAL_TIME_AUDIO: str = str(
        load_param_str_config(section="llm", param_name="GPT_REAL_TIME_AUDIO")
    )

    GPT_4O_MINI: str = str(
        load_param_str_config(section="llm", param_name="GPT_4O_MINI")
    )

    EMBEDDINGS_MODEL: str = str(
        load_param_str_config(section="llm", param_name="EMBEDDINGS_MODEL")
    )

    MAX_TOKEN_CONTEXT: int = int(
        load_param_str_config(section="llm", param_name="MAX_TOKEN_CONTEXT")
    )

    RETRY: int = int(load_param_str_config(section="llm", param_name="RETRY"))

    TEMPERATURE: float = float(
        load_param_str_config(section="llm", param_name="TEMPERATURE")
    )

    TIMEOUT_GPT_3: int = int(
        load_param_str_config(section="llm", param_name="TIMEOUT_GPT_3")
    )

    TIMEOUT_GPT_4: int = int(
        load_param_str_config(section="llm", param_name="TIMEOUT_GPT_4")
    )

    OPENAI_API_KEY: str = str(load_param_env_file(name="OPENAI_API_KEY"))

    META_APP_ID: str = str(load_param_env_file(name="META_APP_ID"))

    META_APP_SECRET: str = str(load_param_env_file(name="META_APP_SECRET"))

    META_APP_ACCESS_TOKEN: str = str(load_param_env_file(name="META_APP_ACCESS_TOKEN"))

    AZURE_DI_URL: str = str(load_param_env_file(name="AZURE_DI_URL"))

    AZURE_DI_KEY: str = str(load_param_env_file(name="AZURE_DI_KEY"))

    MONGO_DB_URI: str = str(load_param_env_file(name="MONGO_DB_URI"))

    USER_DB_NAME: str = str(load_param_env_file(name="USER_DB_NAME"))


env_param = EnvParam()
