import os
from typing import Optional

from insight_plugin.constants import SubcommandDescriptions
from insight_plugin.features.common.common_feature import CommonFeature
from insight_plugin.features.common.exceptions import InsightException
from insight_plugin.features.common.plugin_spec_util import PluginSpecUtil
from insight_plugin.features.connector_to_plugin import util
from insight_plugin.features.connector_to_plugin.manifest_util import manifest_to_spec


class GenPluginFromConnectorController(CommonFeature):
    """
    Controls the subcommand connector_to_plugin to create a new plugin based on a connector.
    This will use the app file of the connector to generate a plugin spec file, 
    this plugin spec will then be used to create the finished plugin, based on the spec file / contents of the app folder.
    """

    HELP_MSG = SubcommandDescriptions.CONECTOR_TO_PLUGIN_DESCRIPTION

    def __init__(
        self,
        connector_folder: str,
        verbose: bool,
        target_dir: str,
    ):
        super().__init__(verbose, target_dir)
        self.connector_folder = connector_folder

    @classmethod
    def new_from_cli(cls, **kwargs):
        super().new_from_cli(
            **{"verbose": kwargs.get("verbose"), "target_dir": kwargs.get("target_dir")}
        )
        return cls(
            kwargs.get("connector_folder"),
            kwargs.get("verbose"),
            kwargs.get("target_dir"),
        )

    def connector_to_plugin(self) -> None:
        """
        Create samples from spec file.
        Write samples to tests directory
        :return: return code, 0 for success, others for fail
        """
        print("Creating a Surface Command plugin starting!")

        print("Converting a manifest file to a plugin spec file")
        output_dir = os.getcwd()
        try:
            manifest_to_spec(
                connector_folder=self.connector_folder, output_dir=output_dir, 
            )
        except Exception as exception:
            print("Error caused when converting the manifest file... aborting")
            raise InsightException(
                message=f"Error caused when converting the manifest file: {exception}",
                troubleshooting="Verify that the manifest.yaml has all the required fields and is valid",
            )

        print("Starting Connector to Plugin Sequence")

        # Verify that the target directory is real
        target_dir = os.path.abspath(path=self.target_dir)
        if not os.path.isdir(target_dir):
            raise InsightException(
                message=f"The target directory {target_dir} does not exist",
                troubleshooting="Verify that the target path is correct, accessible, and a directory",
            )

        # Load the plugin spec from file
        spec = PluginSpecUtil.get_spec_file(f"{output_dir}/plugin.spec.yaml")

        util.handle_connector_to_plugin_create(
            spec=spec,
            target_dir_name=target_dir,
            source_dir_name=self.connector_folder,
        )

        print("Creating a Surface Command plugin complete!")
