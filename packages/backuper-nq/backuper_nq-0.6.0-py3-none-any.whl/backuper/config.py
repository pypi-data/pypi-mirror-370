from pathlib import Path
from typing import Any

from backuper.utils import BaseModelForbidExtra


class ConfigModel(BaseModelForbidExtra):
    dotenv: Path | None = None
    variables: dict[str, str | None] = {}
    actions: Any
