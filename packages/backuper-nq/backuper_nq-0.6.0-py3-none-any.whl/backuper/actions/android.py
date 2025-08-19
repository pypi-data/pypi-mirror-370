import re
from collections.abc import Iterator
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Literal

from backuper.actions.abstract import Action, ActionError, SubShellAction
from backuper.utils import run_sub_shell
from backuper.variables import SubstitutedStr


@dataclass()
class AndroidFile:
    is_dir: bool


class FromAndroidMode(StrEnum):
    ADD = "add"
    SYNC = "sync"


class FromAndroidAction(Action):
    type: Literal["from-android"]
    source: SubstitutedStr
    target: SubstitutedStr
    mode: FromAndroidMode = FromAndroidMode.SYNC
    filename_regex: re.Pattern[str] | None = None
    keep_timestamps_and_mode: bool = True

    def is_filename_skipped(self, filename: str) -> bool:
        return (
            self.filename_regex is not None
            and self.filename_regex.fullmatch(filename) is None
        )

    def collect_ls_command(self, sub_path: Path) -> Iterator[str]:
        yield "adb"
        yield "shell"
        yield "ls"
        yield "-a"
        yield "-l"
        yield f'"{(self.source / sub_path).as_posix()}"'

    def iter_android_directory(
        self, sub_path: Path
    ) -> Iterator[tuple[str, AndroidFile]]:
        print("Listing files on android...")

        ls_result = run_sub_shell(
            list(self.collect_ls_command(sub_path)),
            capture_output=True,
        )
        if ls_result.returncode != 0:
            print(ls_result.stdout)
            print(ls_result.stderr)
            raise ActionError(ls_result.returncode, step_name="listing")

        for line in ls_result.stdout.split("\n"):
            if line == "":
                continue
            filename = line.split(maxsplit=7)[-1]
            if self.is_filename_skipped(filename):
                continue
            # TODO parsing modified date:
            #   `date_raw, time_raw, filename = line.split(maxsplit=7)[5:]`
            #   `last_modified=datetime.fromisoformat(f"{date_raw}T{time_raw}")`
            file_type = line[0]
            match file_type:
                case "-":
                    yield filename, AndroidFile(is_dir=False)
                case "d":
                    yield filename, AndroidFile(is_dir=True)

    def iter_host_directory(self, sub_path: Path) -> Iterator[tuple[str, Path]]:
        print("Listing files on host...")

        for host_file in (self.target / sub_path).iterdir():
            if self.is_filename_skipped(host_file.name):
                continue
            if not host_file.is_dir() and not host_file.is_file():
                continue
            yield host_file.name, host_file

    def iter_sorted_file_couples(
        self, sub_path: Path
    ) -> Iterator[tuple[str, AndroidFile | None, Path | None]]:
        android_files = dict(self.iter_android_directory(sub_path))
        host_files = dict(self.iter_host_directory(sub_path))

        for filename in sorted(android_files | host_files):
            yield filename, android_files.get(filename), host_files.get(filename)

    def collect_pull_command(self, sub_path: Path) -> Iterator[str]:
        yield "adb"
        yield "pull"
        yield "-p"

        if self.keep_timestamps_and_mode:
            yield "-a"

        yield (self.source / sub_path).as_posix()

        yield str(self.target / sub_path)

    def pull_path_from_android(self, sub_path: Path) -> None:
        pull_result = run_sub_shell(list(self.collect_pull_command(sub_path)))
        if pull_result.returncode != 0:
            raise ActionError(pull_result.returncode, step_name="pulling")

    def backup_directory(self, sub_path: Path) -> None:
        for filename, android_file, host_file in self.iter_sorted_file_couples(
            sub_path
        ):
            android_file_path = (self.source / sub_path / filename).as_posix()
            host_file_path = self.target / sub_path / filename

            if host_file is None:
                self.pull_path_from_android(sub_path / filename)
            elif android_file is None:
                if self.mode is not FromAndroidMode.SYNC:
                    print(f"{host_file_path}: skipping extra file/dir")
                    continue
                if host_file.is_dir():
                    raise NotImplementedError  # TODO RMTREE
                else:
                    print(f"{host_file_path}: deleting extra file")
                    host_file.unlink()
            elif host_file.is_dir() and android_file.is_dir:
                print(f"\n{android_file_path}: backing up directory")
                self.backup_directory(sub_path / filename)
            elif host_file.is_file() and not android_file.is_dir:
                print(f"{android_file_path}: skipping existing file")
                # TODO compare modified timestamp:
                #   IF modified(android) > modified(host) -> pull file
                #   ELSE -> nothing
                continue
            else:
                print(f"{android_file_path}: conflicting state")
                input("Press enter to continue execution")

    def run(self) -> None:
        Path(self.target).mkdir(parents=True, exist_ok=True)
        self.backup_directory(sub_path=Path("."))


class ToAndroidAction(SubShellAction):
    type: Literal["to-android"]
    source: SubstitutedStr
    target: SubstitutedStr
    keep_timestamps_and_mode: bool = True

    def collect_command(self) -> Iterator[str]:
        yield "adb"
        yield "push"
        yield "-p"

        if self.keep_timestamps_and_mode:
            yield "-a"

        yield str(self.source)
        yield str(self.target)

    def is_failed(self, return_code: int) -> bool:
        return return_code != 0
