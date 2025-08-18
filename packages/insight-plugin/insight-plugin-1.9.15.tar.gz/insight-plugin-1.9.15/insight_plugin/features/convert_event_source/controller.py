import os

from insight_plugin.constants import SubcommandDescriptions
from insight_plugin.features.common.common_feature import CommonFeature
from insight_plugin.features.common.exceptions import InsightException
from insight_plugin.features.common.plugin_spec_util import PluginSpecTypes
from insight_plugin.features.common.temp_file_util import SafeTempDirectory
from insight_plugin.features.convert_event_source import util
from insight_plugin.features.create.util import handle_refresh_create
from insight_plugin.features.create import util as create_util


def _safe_create(target_dir: str, spec: PluginSpecTypes.Spec):
    handle_refresh_create(spec, target_dir, is_create=True, ignore="", _type="event_source")


class ConvertEventSourceController(CommonFeature):
    """
    Controls the subcommand convert_event_source to create a new plugin based on a RapidKit event source.
    """

    HELP_MSG = SubcommandDescriptions.CONVERT_EVENT_SOURCE_DESCRIPTION

    def __init__(
        self,
        event_source_folder: str,
        verbose: bool,
        target_dir: str,
    ):
        super().__init__(verbose, target_dir)
        self.event_source_folder = event_source_folder

    @classmethod
    def new_from_cli(cls, **kwargs):
        super().new_from_cli(**{"verbose": kwargs.get("verbose"), "target_dir": kwargs.get("target_dir")})
        return cls(
            kwargs.get("event_source_folder"),
            kwargs.get("verbose"),
            kwargs.get("target_dir"),
        )

    def convert_event_source(self) -> None:
        """
        Create samples from spec file.
        Write samples to tests directory
        :return: return code, 0 for success, others for fail
        """
        print("Conversion of RapidKit Event Source starting!")

        # Verify that the target directory is real
        target_dir = os.path.abspath(path=self.target_dir)
        if not os.path.isdir(target_dir):
            raise InsightException(
                message=f"The target directory {target_dir} does not exist",
                troubleshooting="Verify that the target path is correct, accessible, and a directory",
            )

        print("Converting a config file to a plugin spec file")
        try:
            spec = util.config_to_dict(event_source_folder=self.event_source_folder)
        except Exception as exception:
            print("Error caused when converting the config file... aborting")
            raise InsightException(
                message=f"Error caused when converting the config file: {exception}",
                troubleshooting="Verify that the manifest.yaml has all the required fields and is valid",
            )
        try:
            print("Starting Event Source to Plugin Sequence")
            # Load the plugin spec from file
            plugin_dir = os.path.join(target_dir, spec.get("name"))

            # Create the plugin dir from spec in temp dir then move plugin dir to target dir.
            SafeTempDirectory.execute_safe_dir(_safe_create, plugin_dir, True, spec)
            util.save_spec_to_yaml(spec, plugin_dir)
            create_util.create_checksum(spec, plugin_dir)
            print("Creating an event source Plugin complete!")
        except Exception as e:
            print("Error when attempting to convert an event source to a Plugin")
            raise InsightException(e)
