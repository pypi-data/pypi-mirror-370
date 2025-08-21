from frogml.core.inner.build_logic.interface.step_inteface import Step

from frogml_cli import __version__ as frogml_cli_version
from frogml_cli import __name__ as frogml_cli_name


class SdkVersionStep(Step):
    def description(self) -> str:
        return "Getting SDK Version"

    def execute(self) -> None:
        self.build_logger.debug(
            "Getting sdk version"
        )
        self.context.frogml_cli_version = f"{frogml_cli_name}/{frogml_cli_version}"
