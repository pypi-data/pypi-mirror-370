class SubcommandDescriptions:
    ANALYSIS_DESCRIPTION = "Run static code analysis on the plugin"
    CHECKS_DESCRIPTION = "Run Linter, code analysis & validate on the plugin"
    CREATE_DESCRIPTION = (
        "Create a new plugin."
        + " This command will generate the skeleton folder structure and "
        "code for a new plugin, based on the provided plugin.spec.yaml file"
    )
    SERVER_DESCRIPTION = (
        "Run the plugin in HTTP mode."
        + " This allows an external API testing program to be "
        "used to test a plugin "
    )
    SAMPLES_DESCRIPTION = (
        "Create test samples for actions and triggers."
        + " This command will create new files under the 'tests' folder "
        "which can be used to test each new action/trigger. "
        "Note if a file already exists for a particular action/trigger, it will not be overwritten"
    )
    REFRESH_DESCRIPTION = (
        "Refresh the plugin."
        + " This command will update the current plugin code, when updates are made in the "
        "plugin.spec.yaml file"
    )
    RUN_DESCRIPTION = (
        "Run an action/trigger from a json test file"
        + " (created during sample generation)"
    )
    SHELL_DESCRIPTION = (
        "Run the plugin via the docker shell" + " to enable advanced debugging"
    )
    EXPORT_DESCRIPTION = (
        "Export a plugin Docker image to a tarball."
        + " This tarball can be uploaded as a custom plugin via the import "
        "functionality in the InsightConnect UI"
    )
    VALIDATE_DESCRIPTION = (
        "Validate / Run checks against the plugin."
        + " This command performs quality control checks on the current "
        "state of the plugin. This should be run before finalizing any new updates"
    )
    SDK_BUMP = (
        "Bump's the SDK within the plugin to a selected version."
        + "This command will be ran whenever a plugin needs an SDK update. "
        "It will include updating the help.md, Dockerfile and versions across "
        "relevant files"
    )
    CONECTOR_TO_PLUGIN_DESCRIPTION = (
        "Create a new plugin."
        + " This command will generate the skeleton folder structure and "
        "code for a new plugin, based on the provided Surface Command connector folder"
    )
    CONVERT_EVENT_SOURCE_DESCRIPTION = (
        "Convert a RapidKit event source to a plugin."
        + " This command will generate the skeleton folder structure and "
        "code for a new plugin, based on the provided RapidKit event source folder"
    )


VALID_IGNORE_FILES = ["help.md", "dockerfile", "unit_test"]


class Color:
    BOLD = "\033[1m"
    END = "\033[0m"
