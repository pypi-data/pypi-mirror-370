from collections.abc import Iterator

from backuper.utils import BaseModelForbidExtra, run_sub_shell


class ActionError(RuntimeError):
    def __init__(self, return_code: int, step_name: str | None = None) -> None:
        self.return_code = return_code
        self.step_name = step_name

    def build_message(self, action_name: str) -> str:
        if self.step_name is None:
            return f"Action '{action_name}' failed with code {self.return_code}"
        return f"Action '{action_name}' failed at step '{self.step_name}' with code {self.return_code}"


class Action(BaseModelForbidExtra):
    def run(self) -> None:
        raise NotImplementedError


class SubShellAction(Action):
    def collect_command(self) -> Iterator[str]:
        raise NotImplementedError

    def is_failed(self, return_code: int) -> bool:
        raise NotImplementedError

    def run(self) -> None:
        result = run_sub_shell(list(self.collect_command()))
        if self.is_failed(result.returncode):
            raise ActionError(result.returncode)
