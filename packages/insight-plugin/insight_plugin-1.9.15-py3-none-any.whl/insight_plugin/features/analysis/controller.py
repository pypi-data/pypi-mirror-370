from insight_plugin.features.common.common_feature import CommonFeature
from insight_plugin.constants import SubcommandDescriptions
import os
from shutil import which
from typing import Union

DEFAULT_PROFILE = (
    "prospector --profile --tool bandit --tool mccabe --tool pylint --tool pyflakes"
)


class AnalysisController(CommonFeature):
    HELP_MSG = SubcommandDescriptions.ANALYSIS_DESCRIPTION

    def __init__(self, verbose: bool, target_dir: str):
        super().__init__(verbose=verbose, target_dir=target_dir)
        self._verbose = verbose
        self._target_dir = target_dir
        self.default_profile = (
            "prospector --tool bandit --tool mccabe --tool pylint --tool pyflakes"
        )
        self.current_dir = os.path.abspath(self.target_dir)

    @classmethod
    def new_from_cli(cls, **kwargs):
        super().new_from_cli(
            **{
                "verbose": kwargs.get("verbose"),
                "target_dir": kwargs.get("target_dir"),
            }
        )
        return cls(
            kwargs.get("verbose"),
            kwargs.get("target_dir"),
        )

    def run(self) -> Union[None, int]:
        if which("prospector") is None:
            print("Prospector is not installed.\nInstall via 'pip install prospector'")
            return

        # If its an official plugins repo
        if "plugins" in self.current_dir:
            self.run_prospector(
                self.current_dir.split("/plugins")[0] + "/prospector.yaml"
            )
        else:
            # If not in any plugins repo, run default prospector (no profile)
            return self.run_prospector()

    def run_prospector(self, prospector_path: str = None) -> int:
        """
        Helper method to generate the os.system run command depending on prospector used.

        :param prospector_path: Path to the prospector.yaml file
        """
        if prospector_path:
            return os.system(  # nosec
                f"prospector --profile {prospector_path} {self.target_dir} --tool bandit --tool "
                f"mccabe --tool pylint --tool pyflakes "
            )

        return os.system(self.default_profile)  # nosec
