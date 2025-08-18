from insight_plugin.features.common.common_feature import CommonFeature
from insight_plugin.constants import SubcommandDescriptions
import os
from shutil import which


class LinterController(CommonFeature):
    def __init__(self, verbose: bool, target_dir: str):
        super().__init__(verbose=verbose, target_dir=target_dir)
        self._verbose = verbose
        self._target_dir = target_dir

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

    def run(self) -> int:
        if which("black") is None:
            print("Black is not installed.\nInstall via 'pip install black'")
        else:
            return os.system(f"black {self.target_dir}")  # nosec
