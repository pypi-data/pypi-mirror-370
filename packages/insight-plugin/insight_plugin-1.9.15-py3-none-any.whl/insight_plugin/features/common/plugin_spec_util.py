import yaml
from os.path import isdir, basename, dirname, join
from typing import Optional, Union, Dict, Final
from enum import Enum
from insight_plugin.features.common.exceptions import InsightException


class PluginSpecConstants:
    # There are many magic strings in the plugin spec. If we decide to change any of them, this would be the place to
    # reflect this change in code.
    # TODO: Have a discussion on if this should be its own file with the team
    ACTIONS: Final = "actions"
    CONNECTIONS: Final = "connection"
    DEFAULT: Final = "default"
    DESCRIPTION: Final = "description"
    ENUM: Final = "enum"
    EXAMPLE: Final = "example"
    PLACEHOLDER: Final = "placeholder"
    TOOLTIP: Final = "tooltip"
    FILENAME: Final = "plugin.spec.yaml"
    FILEPATH: Final = "filepath"
    HELP: Final = "help"
    ITEMS: Final = "items"
    INPUT: Final = "input"
    KEY_FEATURES: Final = "key_features"
    LINKS: Final = "links"
    MANIFEST: Final = "bin"
    NAME: Final = "name"
    OUTPUT: Final = "output"
    PLUGIN_DESCRIPTION: Final = "description"
    PLUGIN_TROUBLESHOOTING: Final = "troubleshooting"
    REFERENCES: Final = "references"
    REQUIRED: Final = "required"
    REQUIREMENTS: Final = "requirements"
    SPEC_VERSION: Final = "plugin_spec_version"
    STATE: Final = "state"
    SUPPORTED_VERSIONS: Final = "supported_versions"
    TRIGGERS: Final = "triggers"
    TASKS: Final = "tasks"
    TITLE: Final = "title"
    TYPE: Final = "type"
    TYPES: Final = "types"
    VENDOR: Final = "vendor"
    VERSION: Final = "version"
    VERSION_HISTORY: Final = "version_history"


class PluginSpecVersions(Enum):
    V2 = "v2"
    V3 = "v3"


class PluginComponent(Enum):
    """
    A component is something that runs either on an orchestrator or in the cloud. Components may or may not use
    a connection.
    """

    ACTION = PluginSpecConstants.ACTIONS
    TRIGGER = PluginSpecConstants.TRIGGERS
    TASK = PluginSpecConstants.TASKS


class PluginSpecUtilModes(Enum):
    # Class that would later support alternate ways of getting the spec file
    SPECFILE = f"{PluginSpecConstants.FILEPATH} mode"
    GUI = "gui"


class PluginSpecTypes:
    # Spec is an explicit type alias defining valid plugin spec values
    Spec = Dict[str, Union[str, bool, int, float, dict]]


class PluginSpecUtil:
    def __init__(self, mode: PluginSpecUtilModes):
        # If filepath is passed, use that, otherwise check current dir for spec file
        self.mode = mode
        self._spec_dict = None

    def load(self, **kwargs):
        if self.mode == PluginSpecUtilModes.SPECFILE:
            if PluginSpecConstants.FILEPATH in kwargs:
                # If the user has provided a path, pass it here
                self._load_from_file(kwargs[PluginSpecConstants.FILEPATH])
            else:
                # Otherwise try the default approach, assume we are in plugin dir
                # Worst that happens is they get file not found
                self._load_from_file()

    @staticmethod
    def ensure_spec_in_path(filepath: str = None) -> str:
        # If the passed path is a dir, append spec at the end
        if isdir(filepath):
            filepath = join(filepath, PluginSpecConstants.FILENAME)
        return filepath

    def _load_from_file(self, filepath: Optional[str] = None):
        filepath = (
            self.ensure_spec_in_path(filepath)
            if filepath is not None
            else PluginSpecConstants.FILENAME
        )

        try:
            # open uses cwd if no absolute path is provided
            with open(filepath, "rt", encoding="utf-8") as spec_file:
                self._spec_dict = yaml.safe_load(spec_file)
        except FileNotFoundError as error:
            print(
                f"{basename(filepath)} not found in {dirname(filepath)}. "
                f"Check that the file exists and is accessible in the provided path. "
            )
            raise error
        except PermissionError as error:
            print(
                f"Permission error for file {filepath}. Check that your user has access to this file"
            )
            raise error
        except OSError as error:
            print(f"Operating system could not open file {filepath}")
            raise error
        except yaml.YAMLError as error:
            print(f"Content of {filepath} is not valid YAML")
            raise error

    @staticmethod
    def get_spec_file(spec_path: str) -> Dict[str, str]:
        """
        Load the plugin spec dictionary from a file
        :param spec_path: The filesystem path to the plugin spec file
        :return: The plugin spec as a dictionary
        """
        # These two lines will change (some type of if/else block) is we want to get spec from somewhere else
        spec_util = PluginSpecUtil(PluginSpecUtilModes.SPECFILE)
        if spec_path is not None:
            kwarg = {
                f"{PluginSpecConstants.FILEPATH}": spec_path
            }  # Fill as needed depending on what we need to do
        else:
            kwarg = {}

        spec_util.load(**kwarg)
        spec = spec_util.spec_dictionary

        # Check to make sure the spec has been set properly
        if spec is None:
            raise InsightException(
                message="Could not load plugin.spec.yaml file needed to export the plugin. ",
                troubleshooting="Ensure that a plugin spec file is in the current directory or that"
                " you are passing a directory with containing a plugin.spec.yaml file.",
            )
        return spec

    @property
    def spec_dictionary(self):
        return self._spec_dict

    @staticmethod
    def get_docker_name(spec_dict: dict) -> str:
        """
        Gets the docker name for the current plugin
        :param spec_dict: top-level plugin.spec.yaml parsed into a dictionary
        :return:
        """
        if (
            spec_dict is None
            or spec_dict.get("vendor") is None
            or spec_dict.get("name") is None
            or spec_dict["version"] is None
        ):
            raise InsightException(
                message="Plugin.spec.yaml file is missing either vendor, name, or version fields. ",
                troubleshooting="Add them to plugin.spec.yaml to identify the correct docker image.",
            )
        return f"{spec_dict['vendor']}/{spec_dict['name']}:{spec_dict['version']}"
