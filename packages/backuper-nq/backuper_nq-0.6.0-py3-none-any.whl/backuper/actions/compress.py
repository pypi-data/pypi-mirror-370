from collections.abc import Iterator
from enum import StrEnum
from typing import Literal, assert_never

from backuper.actions.abstract import SubShellAction
from backuper.variables import SubstitutedStr


class CompressMode(StrEnum):
    ADD = "add"
    UPDATE = "update"
    SYNC = "sync"


class CompressAction(SubShellAction):
    type: Literal["compress"]
    source: SubstitutedStr
    archive_name: SubstitutedStr
    archive_type: Literal["7z", "zip", "gzip", "bzip2", "tar"] = "7z"
    mode: CompressMode = CompressMode.SYNC
    password: SubstitutedStr | None = None

    def collect_command(self) -> Iterator[str]:
        yield "7za"

        match self.mode:
            case CompressMode.ADD:
                yield "a"
            case CompressMode.UPDATE:
                yield "u"
            case CompressMode.SYNC:
                yield "u"
                yield "-uq0"
            case _:
                assert_never(self.mode)

        yield f"{self.archive_name}.{self.archive_type}"

        if self.archive_type != "7z":
            yield f"-t{self.archive_type}"

        if self.password:
            yield f"-p{self.password}"
            if self.archive_type == "7z":
                yield "-mhe"

        yield self.source

    def is_failed(self, return_code: int) -> bool:
        return return_code != 0
