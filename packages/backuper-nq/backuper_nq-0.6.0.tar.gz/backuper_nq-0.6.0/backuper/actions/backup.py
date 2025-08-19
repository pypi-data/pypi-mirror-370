from collections.abc import Iterator
from typing import Literal

from backuper.actions.abstract import SubShellAction
from backuper.utils import BaseModelForbidExtra
from backuper.variables import SubstitutedStr


class BackupExcludeSchema(BaseModelForbidExtra):
    directory_names: list[SubstitutedStr] = []
    filename_patterns: list[SubstitutedStr] = []


class BackupAction(SubShellAction):
    type: Literal["backup"]
    source: SubstitutedStr
    target: SubstitutedStr
    override_permissions: bool = False
    exclude: BackupExcludeSchema = BackupExcludeSchema()

    def collect_command(self) -> Iterator[str]:
        yield "robocopy"
        yield str(self.source)
        yield str(self.target)

        yield "/mir"

        if self.override_permissions:
            yield "/b"

        if self.exclude.directory_names:
            yield "/xd"
            yield from self.exclude.directory_names

        if self.exclude.filename_patterns:
            yield "/xf"
            yield from self.exclude.filename_patterns

    def is_failed(self, return_code: int) -> bool:
        return return_code > 7
