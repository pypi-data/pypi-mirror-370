from os import getenv
from string import Template
from typing import Annotated

from dotenv import load_dotenv
from pydantic import AfterValidator
from pydantic_core.core_schema import ValidationInfo

from backuper.config import ConfigModel


def substitute(incoming_string: str, info: ValidationInfo) -> str:
    if not isinstance(info.context, dict):
        raise RuntimeError

    template = Template(incoming_string)
    return template.substitute(info.context)


SubstitutedStr = Annotated[str, AfterValidator(substitute)]


def load_variable(name: str, default_value: str | None) -> str:
    value = getenv(name, default=default_value)
    if value is None:
        raise EnvironmentError(f"Environment variable '{name}' should be specified")
    return value


def load_variables(config: ConfigModel) -> dict[str, str]:
    if config.dotenv is not None:
        load_dotenv(config.dotenv)

    return {
        name: load_variable(name=name, default_value=default_value)
        for name, default_value in config.variables.items()
    }
