import os
import shutil
from typing import Optional
from insight_plugin import ROOT_DIR, FILE_ENCODING
from insight_plugin.features.common.plugin_spec_util import (
    PluginSpecUtil,
    PluginSpecTypes,
)
from insight_plugin.features.common.common_feature import CommonFeature
from insight_plugin.features.common.template_util import Templates
from insight_plugin.features.common.temp_file_util import SafeTempDirectory
from insight_plugin.features.common.exceptions import InsightException
from insight_plugin.features.create import util
from insight_plugin.constants import SubcommandDescriptions


class CreateController(CommonFeature):
    """
    Controls the subcommand to create a new skeleton plugin file structure.
    Depends on plugin spec dictionary values to fill templates.
    """

    HELP_MSG = SubcommandDescriptions.CREATE_DESCRIPTION

    def __init__(self, spec_path: Optional[str], verbose: bool, target_dir: str):
        super().__init__(verbose, target_dir)
        self._spec_path = spec_path
        self._templates = Templates(os.path.join(ROOT_DIR, "templates"))

    @classmethod
    def new_from_cli(cls, **kwargs):
        super().new_from_cli(
            **{"verbose": kwargs.get("verbose"), "target_dir": kwargs.get("target_dir")}
        )
        return cls(
            kwargs.get("spec_path"),
            kwargs.get("verbose"),
            kwargs.get("target_dir"),
        )

    def spec_to_file(self, spec: PluginSpecTypes.Spec, plugin_dir: str):
        with open(
            os.path.join(plugin_dir, "plugin.spec.yaml"), "w", encoding=FILE_ENCODING
        ) as plugin_spec:
            plugin_spec.write(str(spec))  # This is formatted in JSON not YAML

    def create(self) -> None:
        """
        Create plugin from specfile.
        Write files to temp dir first, if successful moves to target.
        :return: return code, 0 for success, others for fail # TODO
        """

        self.logger.info("Starting Create Sequence")

        # Verify that the target directory is real
        target_dir = os.path.abspath(self.target_dir)
        if not os.path.isdir(target_dir):
            raise InsightException(
                message=f"The target directory {target_dir} does not exist",
                troubleshooting="Verify that the target path is correct, accessible, and a directory",
            )

        # Check if a plugin.spec.yaml file path has been provided as a CLI argument
        if self._spec_path:
            # Load the plugin spec from file
            spec = PluginSpecUtil.get_spec_file(self._spec_path)
        else:
            # TODO
            print("No spec file provided")
            spec = {}

        # The target directory will CONTAIN the top-level directory containing all plugin content.
        # The target directory IS NOT the top-level plugin directory itself.
        # The top-level plugin directory WILL BE CREATED by this tool INSIDE the target directory.
        plugin_dir = os.path.join(target_dir, spec.get("name"))

        if not os.path.exists(plugin_dir):
            # Create the plugin dir from spec in temp dir then move plugin dir to target dir.
            SafeTempDirectory.execute_safe_dir(
                self._safe_create, plugin_dir, False, spec
            )

            # Create a copy of plugin.spec.yaml in the plugin directory
            if self._spec_path:
                # shutil.copy2() preserves file metadata
                shutil.copy2(
                    PluginSpecUtil.ensure_spec_in_path(self._spec_path), plugin_dir
                )
            else:
                # create plugin spec file from interactive user input
                self.spec_to_file(spec, plugin_dir)

            util.create_checksum(spec, plugin_dir)

            print("Create process complete!")

        else:
            self.logger.warning(
                f"Directory for plugin named '{spec['name']}' exists. In order to re-create the plugin, please use "
                f"refresh command or remove the existing folder. "
            )

    def _safe_create(self, target_dir: str, spec: PluginSpecTypes.Spec):
        """
        This method exists to be passed into SafeTempDirectory.execute_safe_dir()
        So that we may first create in the plugin in a temp dir, then execute_safe_dir() will copy it to the target dir
        :param target_dir: The absolute path to the target directory, required by execute_safe_dir()
        :param spec: The plugin spec dictionary, passed through execute_safe_dir() via args*
        :return:
        """
        util.handle_refresh_create(spec, target_dir, is_create=True, ignore="")
