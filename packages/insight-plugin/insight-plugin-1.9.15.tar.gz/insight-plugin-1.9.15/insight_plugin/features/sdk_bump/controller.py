import os
from pathlib import Path
from insight_plugin.features.common.common_feature import CommonFeature
from insight_plugin.features.common.plugin_spec_util import PluginSpecUtil
from insight_plugin.features.sdk_bump.util.yaml_util import YamlUtil
from insight_plugin.constants import SubcommandDescriptions
from insight_plugin.features.create import util
from insight_plugin import ROOT_DIR


class SDKController(CommonFeature):
    """
    Controls the subcommand for SDK Bump
    Allows the user to specify the SDK version they want
    to bump to, and will update the plugin version and changelog automatically
    """

    HELP_MSG = SubcommandDescriptions.SDK_BUMP

    def __init__(
        self,
        verbose: bool,
        target_dir: str,
        sdk_num: str,
    ):
        super().__init__(verbose, target_dir)
        self._verbose = verbose
        self.sdk_num = sdk_num

    @classmethod
    def new_from_cli(cls, **kwargs):
        super().new_from_cli(
            **{
                "verbose": kwargs.get("verbose"),
                "target_dir": kwargs.get("target_dir"),
                "sdk_num": kwargs.get("sdk_num"),
            }
        )
        return cls(
            kwargs.get("verbose"),
            kwargs.get("target_dir"),
            kwargs.get("sdk_num"),
        )

    def run(self):
        # Retrieve the current spec & version
        spec = PluginSpecUtil.get_spec_file(self.target_dir)
        spec_version = spec.get("version")

        # Bump the patch version of the plugin
        spec_version_split = spec_version.split(".")
        spec_version_split[-1] = str(int(spec_version_split[-1]) + 1)
        spec_version = ".".join(spec_version_split)

        sdk_util = YamlUtil(
            verbose=self._verbose,
            target_dir=self.target_dir,
            version_num=spec_version,
            changelog_desc=f"Updated SDK to the latest version ({self.sdk_num})",
            sdk_num=self.sdk_num,
        )
        sdk_util.run()
        # Overwrites the prior spec file with the new SDK updates
        spec = PluginSpecUtil.get_spec_file(self.target_dir)

        # Runs the refresh command
        util.handle_refresh_create(
            spec, self.target_dir, is_create=False, ignore=["unit_test"]
        )

        # Stores path of 'pyproject.toml' so it is runnable on any device
        config_path = f'{ROOT_DIR}/black_config.toml'
        os.system(f"black --config {config_path} {self.target_dir} .")  # nosec B605

        util.create_checksum(spec, self.target_dir)

        print("SDK Bump complete!")
