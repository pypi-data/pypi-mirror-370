from insight_plugin.features.common.common_feature import CommonFeature
from icon_validator.validate import validate as icon_validate
from insight_plugin.constants import SubcommandDescriptions


class ValidateController(CommonFeature):
    """
    Controls the subcommand for validate
    Allows the user to run validation checks against the plugin
    """

    HELP_MSG = SubcommandDescriptions.VALIDATE_DESCRIPTION

    def __init__(self, target_dir: str):
        super().__init__()
        self._target_dir = target_dir

    @classmethod
    def new_from_cli(cls, **kwargs):
        super().new_from_cli(**{"target_dir": kwargs.get("target_dir")})
        return cls(
            kwargs.get("target_dir"),
        )

    def run(self):
        return icon_validate(self.target_dir, run_all=True)
