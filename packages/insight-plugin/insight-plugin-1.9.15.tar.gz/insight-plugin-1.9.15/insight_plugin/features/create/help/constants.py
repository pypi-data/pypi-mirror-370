from enum import Enum
from insight_plugin.features.common.plugin_spec_util import PluginSpecConstants


class HelpTypes(Enum):
    # types for help file. Only use markdown now but possible to use other in the future
    MARKDOWN = 0


class HelpMappings:
    # Please keep alphabetized (by key) for easy lookups here
    SECTION_TITLES = {
        PluginSpecConstants.ACTIONS: "Actions",
        PluginSpecConstants.PLUGIN_DESCRIPTION: "Description",
        PluginSpecConstants.INPUT: "Input",
        PluginSpecConstants.KEY_FEATURES: "Key Features",
        PluginSpecConstants.OUTPUT: "Output",
        PluginSpecConstants.PLUGIN_TROUBLESHOOTING: "Troubleshooting",
        PluginSpecConstants.REFERENCES: "References",
        PluginSpecConstants.LINKS: "Links",
        PluginSpecConstants.REQUIREMENTS: "Requirements",
        PluginSpecConstants.SUPPORTED_VERSIONS: "Supported Product Versions",
        PluginSpecConstants.TASKS: "Tasks",
        PluginSpecConstants.TRIGGERS: "Triggers",
        PluginSpecConstants.VERSION_HISTORY: "Version History",
    }
    EXAMPLE_INPUT = "Example input:"
    EXAMPLE_OUTPUT = "Example output:"


class TableHeaders:
    INPUT_HEADERS = [
        "Name",
        "Type",
        "Default",
        "Required",
        "Description",
        "Enum",
        "Example",
        "Placeholder",
        "Tooltip",
    ]
    OUTPUT_HEADERS = [
        "Name",
        "Type",
        "Required",
        "Description",
        "Example",
    ]
    CUSTOM_TYPE_HEADERS = [
        "Name",
        "Type",
        "Default",
        "Required",
        "Description",
        "Example",
    ]
