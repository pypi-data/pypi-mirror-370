import os
from pathlib import Path
from typing import Optional
from insight_plugin import ROOT_DIR, FILE_ENCODING
from insight_plugin.features.common.plugin_spec_util import (
    PluginSpecUtil,
    PluginSpecTypes,
)
from insight_plugin.features.common.common_feature import CommonFeature
from insight_plugin.features.common.template_util import Templates
from insight_plugin.features.common.exceptions import InsightException
from insight_plugin.features.create import util
from insight_plugin.constants import SubcommandDescriptions, VALID_IGNORE_FILES


class RefreshController(CommonFeature):
    """
    Controls the subcommand to refresh plugin file structure.
    Depends on plugin spec dictionary values to fill templates.
    """

    HELP_MSG = SubcommandDescriptions.REFRESH_DESCRIPTION

    def __init__(
        self, spec_path: Optional[str], verbose: bool, target_dir: str, ignore: list
    ):
        super().__init__(verbose, target_dir)
        self._spec_path = spec_path
        self._templates = Templates(os.path.join(ROOT_DIR, "templates"))
        ignore = [item.lower() for item in ignore]
        self.ignore = ignore

    def spec_to_file(self, spec: PluginSpecTypes.Spec, plugin_dir: str):
        with open(
            os.path.join(plugin_dir, "plugin.spec.yaml"), "w", encoding=FILE_ENCODING
        ) as plugin_spec:
            plugin_spec.write(str(spec))  # This is formatted in JSON not YAML

    def refresh(self) -> None:
        """
        Refresh plugin from specfile.
        Write files to temp dir first, if successful moves to target.
        :return: return code, 0 for success, others for fail
        """
        # Verify that the target directory is real
        target_dir = os.path.abspath(self.target_dir)

        if not os.path.isdir(target_dir):
            raise InsightException(
                message=f"The target directory {target_dir} does not exist",
                troubleshooting="Verify that the target path is correct, accessible, and a directory",
            )
        # Load the plugin spec from file
        spec = PluginSpecUtil.get_spec_file(self._spec_path)

        # List of valid file names for the 'ignore' param
        valid = VALID_IGNORE_FILES

        # Raises an exception when an invalid file name is used for the 'ignore' param
        ignore = self.ignore

        for item in ignore:
            if item not in valid:
                raise InsightException(
                    message=f"File name not recognised: '{item}',",
                    troubleshooting="Please enter any of the following files to ignore: help.md, Dockerfile or unit_test",
                )

        util.handle_refresh_create(spec, target_dir, is_create=False, ignore=ignore)

        # Stores path of 'pyproject.toml' so it is runnable on any device
        config_path = f'{ROOT_DIR}/black_config.toml'
        os.system(f"black --config {config_path} {self.target_dir} .")  # nosec B605

        util.create_checksum(spec, target_dir)

        print("Refresh process complete!")

    @classmethod
    def new_from_cli(cls, **kwargs):
        super().new_from_cli(
            **{
                "verbose": kwargs.get("verbose"),
                "target_dir": kwargs.get("target_dir"),
                "ignore": kwargs.get("ignore"),
            }
        )
        return cls(
            kwargs.get("spec_path"),
            kwargs.get("verbose"),
            kwargs.get("target_dir"),
            kwargs.get("ignore"),
        )
