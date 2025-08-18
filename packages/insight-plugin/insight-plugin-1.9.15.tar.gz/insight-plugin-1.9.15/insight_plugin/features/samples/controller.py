from typing import Optional
from insight_plugin.features.common.common_feature import CommonFeature
from insight_plugin.constants import SubcommandDescriptions
from insight_plugin.features.samples.util.util import SamplesUtil


class GenSampleController(CommonFeature):
    """
    Controls the subcommand to create samples for testing.
    Depends on plugin spec dictionary values to fill templates.
    """

    HELP_MSG = SubcommandDescriptions.SAMPLES_DESCRIPTION

    def __init__(
        self,
        verbose: bool,
        target_dir: str,
        target_component: Optional[str],
    ):
        super().__init__(verbose, target_dir)
        self._target_component = target_component
        self._verbose = verbose

    @classmethod
    def new_from_cli(cls, **kwargs):
        super().new_from_cli(
            **{"verbose": kwargs.get("verbose"), "target_dir": kwargs.get("target_dir")}
        )
        return cls(
            kwargs.get("verbose"),
            kwargs.get("target_dir"),
            kwargs.get("target_component"),
        )

    def samples(self) -> None:
        """
        Create samples from spec file.
        Write samples to tests directory
        :return: return code, 0 for success, others for fail
        """

        samples_util = SamplesUtil(
            verbose=self._verbose,
            target_dir=self.target_dir,
            target_component=self._target_component,
        )
        samples_util.run()

        print("Samples process complete!")
