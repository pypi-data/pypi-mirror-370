from typing import Annotated

from pydantic import ValidationError
from typer import Argument, FileText, Typer
from yaml import safe_load as safe_load_yaml

from backuper.config import ConfigModel
from backuper.runner import ActionsModel, run_actions
from backuper.variables import load_variables

cli = Typer()


@cli.command()
def main(config_file: Annotated[FileText, Argument(encoding="utf-8")]) -> None:
    # TODO defaults for filename

    loaded_config = safe_load_yaml(config_file)

    try:
        config = ConfigModel.model_validate(loaded_config)
    except ValidationError as e:  # noqa: WPS329 WPS440
        raise e  # TODO error handling for parsing

    variables = load_variables(config)

    try:
        actions = ActionsModel.model_validate(config.actions, context=variables)
    except ValidationError as e:  # noqa: WPS329 WPS440
        raise e  # TODO error handling for parsing

    run_actions(actions=actions)


if __name__ == "__main__":
    cli()
