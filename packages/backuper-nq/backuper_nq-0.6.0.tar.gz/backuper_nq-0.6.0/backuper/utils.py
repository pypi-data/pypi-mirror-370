import subprocess
from typing import Any

from pydantic import BaseModel, ConfigDict


class BaseModelForbidExtra(BaseModel):
    model_config = ConfigDict(extra="forbid")


def run_sub_shell(
    command: list[str],
    capture_output: bool = False,
    encoding: str | None = "utf-8",
) -> subprocess.CompletedProcess[Any]:
    return subprocess.run(
        command,
        capture_output=capture_output,
        shell=True,
        encoding=encoding,
    )
