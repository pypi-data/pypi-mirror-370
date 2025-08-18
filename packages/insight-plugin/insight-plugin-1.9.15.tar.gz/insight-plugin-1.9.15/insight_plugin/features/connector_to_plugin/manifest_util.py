import yaml
import os
from typing import Tuple, Optional
from copy import deepcopy

from insight_plugin import FILE_ENCODING
from insight_plugin.features.connector_to_plugin.help.constants import TYPE_MAP
from insight_plugin.features.common.plugin_spec_util import (
    PluginSpecUtil,
    PluginSpecTypes,
)
from icon_validator.rules.lists.lists import title_validation_list

def spec_to_file(spec: PluginSpecTypes.Spec, plugin_dir: str) -> None:
    """
    Takes the spec file object and will write it to the plugin.spec.yaml file

    :param PluginSpecTypes.Spec spec: The yaml data to be written to the file
    :param str plugin_dir: The path of the directory where the plugin.spec.yaml will be saved
    """
    with open(
        os.path.join(plugin_dir, "plugin.spec.yaml"), "w", encoding=FILE_ENCODING
    ) as plugin_spec:
        plugin_spec.write(spec)  # This is formatted in JSON not YAML


def manifest_to_spec(connector_folder: str, output_dir: str) -> str:
    """
    Takes the file path to a connectors manifest file, reads in and converts this
    to a plugin.spec.yaml format and will save this to a file

    :param str manifest_file: The file path to the manifest.yaml file
    :param str output_dir: The directory were the newly created plugin.spec.yaml file will be saved
    :return str: The name of the function that is used as the test connect method from within the connector code
    """

    manifest_file = f"{connector_folder}/manifest.yaml"

    # read in the manifest file
    try:
        connector_manifest = PluginSpecUtil.get_spec_file(spec_path=manifest_file)
    except Exception as error_message:
        print(f"Error caused when reading in the manifest file - {error_message}")
        raise error_message

    try:
        actions = get_actions(
            connector_manifest=deepcopy(connector_manifest)
        )
    except Exception as error_message:
        print(
            f"Error caused when converting the functions to actions  - {error_message}"
        )
        raise error_message
    try:
        version, connection_version = get_versions(
            connector_manifest=deepcopy(connector_manifest)
        )
    except Exception as error_message:
        print(
            f"Error caused when converting the manifest version number to a plugin version number  - {error_message}"
        )
        raise error_message

    try:
        name, title = get_plugin_name(connector_manifest=deepcopy(connector_manifest))

    except Exception as error_message:
        print(f"Error caused when creating the spec file - {error_message}")
        raise error_message

    try:
        user_needed = get_user_type(connector_folder)
    except Exception as error_message:
        print(f"Error caused when fetching the user type to use - {error_message}")
        raise error_message

    try:
        new_spec_file = format_spec_file(
            connector_manifest=connector_manifest,
            name=name,
            title=title,
            version=version,
            connection_version=connection_version,
            actions=actions,
            user_needed=user_needed
        )
    except Exception as error_message:
        print(
            f"Error caused when formatting the spec file into a json format - {error_message}"
        )
        raise error_message

    try:
        yaml.Dumper.ignore_aliases = lambda *args: True
        new_spec_file = yaml.dump(
            new_spec_file, sort_keys=False, default_flow_style=False, width=256
        )

        # generate the new spec file
        spec_to_file(spec=new_spec_file, plugin_dir=output_dir)

    except Exception as error_message:
        print(
            f"Error caused when writing the spec file object to a file - {error_message}"
        )
        raise error_message


def get_plugin_name(connector_manifest: str) -> Tuple[str, str]:
    """
    This will look in the manifest.yaml for the name that is used by used by the connector
    This will then be formatted to the plugin name and title scheme, with SC prefixed to show its a connector conversion

    :param str connector_folder: the name of the folder the connector is in
    :return Tuple[str, str]: The plugin name nad title that has been generated from the manifests name field
    """

    plugin_name = connector_manifest.get("id", "").replace(".", "_")


    # appending Surface Command for now to all the new plugins
    title = f"SC:{plugin_name}"


    # remove any mention of beta from title and
    title = title.replace("(Beta)", "")
    title = title.strip()

    # make sure only all the title is correct capital format
    title_string = ""
    for value in title.split(" "):
        if len(value) > 1:
            title_string = f"{title_string} {value[0].upper() + value[1:]}"
        else:
            title_string = f"{title_string} {value.capitalize()}"

    title = title_string.strip()

    # our names need are lowercase with no spaces
    name = title.lower()
    name = name.replace(" ", "_")
    name = name.replace(":", "_")

    return name, title


def get_actions(connector_manifest: dict) -> dict:
    """
    To generate the actions section of the plugin.spec.yaml file based on the connector manifest file

    :param dict connector_manifest: A dict object created from reading in the manifest.yaml file
    :return dict: The parsed action object that will be added to the plugin.spec.yaml file
    """

    actions = {}

    # This is a common param for the actions
    execution_id_param = {
        "name": "execution_id",
        "schema": {
            "type": "string",
        },
    }
    # This is a common return for both starting an import function and retrieving its status
    import_function_status_return = {
        'name': 'import_function_status',
        'type': 'string',
        'enum': [
            'running',
            'completed',
            'failed',
            'stopped',
        ],
        'nullable': False,
    }

    functions = connector_manifest.get("functions", [])
    # Add the status check function for import functions
    functions.append({
        "id": "get_orchestrator_update",
        "name": "Get Orchestrator Update",
        "description": "Get the status of a running import function",
        "parameters": [
            execution_id_param,
        ],
        "returns": [
            import_function_status_return,
        ],
        "entrypoint": "get_orchestrator_update",
    })
    # Add the stop function for import functions
    functions.append({
        "id": "stop_import_function",
        "name": "Stop Import Function",
        "description": "Stop a running import function",
        "parameters": [
            execution_id_param,
        ],
        "returns": [
            import_function_status_return,
        ],
        "entrypoint": "stop_import_function",
    })

    for action in functions:
        dict_of_inputs = {}
        if action.get('type') == 'import':
            # import functions all have the same inputs
            action['parameters'] = [
                {
                    'name': 'settings',
                    'schema': {
                        'type': 'object',
                    },
                },
                {
                    'name': 'high_water_mark',
                    'schema': {
                        'type': 'object',
                    },
                },
                {
                    'name': 'import_configuration_items',
                    'schema': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                        },
                    },
                },
                {
                    'name': 'custom_import_parameters',
                    'schema': {
                        'type': 'object',
                    },
                },
                {
                    'name': 'execution_id',
                    'schema': {
                        'type': 'string',
                    },
                    'nullable': False,
                }
            ]
            # and outputs
            action['returns'] = [
                import_function_status_return,
            ]

        for input_item in action.get("parameters", []):
            if input_item.get("name"):
                parameter_name = input_item.get("name")
                parameter_name, action_parameter_values = process_action(
                    parameter_name=parameter_name,
                    action_parameter_values=input_item
                )
            else:
                parameter_name = process_parameter_name(input_item)
                parameter_name, action_parameter_values = process_action(
                    connector_manifest=deepcopy(connector_manifest),
                    parameter_name=parameter_name,
                )

            dict_of_inputs[parameter_name] = action_parameter_values
        dict_of_outputs = {}
        for output_item in action.get("returns", []):
            parameter_name = process_parameter_name(output_item)
            if not parameter_name and output_item.get("name") == "unspecified":
                dict_of_outputs = {
                    "output": {
                        "type": "object",
                        "description": "PLACEHOLDER",
                        "required": False,
                        "example": {},
                    }
                }
                break

            # similar handling to inputs, we need to check if the output item has a name
            # if it does, we will use that as the name, if not we will use the
            # name that is in the action_parameter_values object
            # this is because some of the output items are not named in the manifest file
            # so we need to use the name that is in the action_parameter_values object
            if output_item.get("name"):
                parameter_name = output_item.get("name")
                parameter_name, action_parameter_values = process_action(
                    parameter_name=parameter_name,
                    action_parameter_values=output_item,
                )
            else:
                parameter_name, action_parameter_values = process_action(
                    connector_manifest=deepcopy(connector_manifest),
                    parameter_name=parameter_name,
                )

            dict_of_outputs[parameter_name] = action_parameter_values

        # we need to take the name foe the action from the entrypoint section of the manifest file and not the id section
        # there are some cases where the name of the function in the manifest file and the python method are not the same
        # so the entrypoint will be required to ensure we call the correct function
        action_name = action.get("entrypoint").split(".")[-1]

        actions[action_name] = {
            "title": action.get("name"),
            "description": action.get("description", "test_description").removesuffix("."),
            "input": dict_of_inputs,
            "output": dict_of_outputs,
            "action_type": action.get("type"),
        }

    return actions


def process_parameter_name(action_parameter: dict) -> str:
    """
    The names of the parameter are in the format of
    - $ref: '#/components/parameters/UserParameter'
    This will strip out the just name we need of the function

    :param dict action_parameter: The object containing the action information
    :return str: The parsed name of the action
    """

    action_parameter_reference = action_parameter.get("$ref", "")
    action_parameter_name = action_parameter_reference.split("/")[-1]

    return action_parameter_name


def format_action_parameter_values(
    connector_manifest: dict, parameter_name: str
) -> dict:
    """
    The manifest will contain references to other object within the manifest file,
    This will take a reference that action section is referencing and return the object itself

    :param dict connector_manifest: A dict object created from reading in the manifest.yaml file
    :param str parameter_name: The name of the parameter that will be fetched
    :return dict: The info of the object that was being referenced
    """
    return (
        connector_manifest.get("components", {})
        .get("parameters", {})
        .get(parameter_name, {})
    )


def process_action(
    connector_manifest: Optional[dict] = None,
    parameter_name: str = "",
    action_parameter_values: Optional[dict] = None,
) -> Tuple[str, dict]:
    """
    To take the raw parameter info that was extracted formated he manifest.yaml file and
    convert it to a format that will be used by the plugin.spec.yaml file

    :param dict connector_manifest: A dict object created from reading in the manifest.yaml file
    :param str parameter_name: The name of the parameter within the action that is being formatted
    :param dict action_parameter_values: The raw action parameter values that are being formatted
    :return Tuple[str, dict]: The formatted name of the action parameter, The formatted contents of the action parameter
    """
    connector_manifest = connector_manifest or {}
    if not action_parameter_values:
        action_parameter_values = format_action_parameter_values(
            connector_manifest=deepcopy(connector_manifest),
            parameter_name=parameter_name,
        )
    else:
        action_parameter_values = deepcopy(action_parameter_values)

    # connectors use the key of nullable rather than required so we need to swap that
    # as nullable true means its not required we need the inverse of this field
    action_parameter_values["required"] = not action_parameter_values.pop("nullable", True)
    # check if there is more than just this
    has_schema = False
    if action_parameter_values.get("schema"):
        has_schema = True
        action_parameter_values["type"] = action_parameter_values.get("schema", {}).get(
            "type", "object"
        )
    _type = action_parameter_values.get("type")
    items_location = action_parameter_values
    if has_schema:
        items_location = action_parameter_values.get("schema", {})
        _type = action_parameter_values.get("schema", {}).get("type")
    if _type == "array":
        item_type = items_location.get("items", {}).get("type", "string")
        action_parameter_values["type"] = f"[]{item_type}"

    if action_parameter_values["type"] == "string" and action_parameter_values.get("format", "") == "password":
        action_parameter_values["type"] = "password"

    for key, value in action_parameter_values.items():
        if key not in ["name", "description"] and value == "number":
            action_parameter_values[key] = "float"

    # removing an full stops from descriptions
    if action_parameter_values.get("description"):
        action_parameter_values["description"] = action_parameter_values.get(
            "description", ""
        ).removesuffix(".")

    if action_parameter_values.get("title"):
        # shorten titles to 6 words or less
        action_parameter_values["title"] = action_parameter_values.get(
            "title", ""
        ).removesuffix(".")

    if action_parameter_values.get("examples"):
        action_parameter_values["example"] = action_parameter_values.get("examples", ["PLACEHOLDER EXAMPLE"])[0]

    # adding in placeholder examples if none exist
    if not action_parameter_values.get("example") and not action_parameter_values.get("examples"):
        action_parameter_values["example"] = TYPE_MAP.get(action_parameter_values["type"], "PLACEHOLDER EXAMPLE")

    # we need to clean up the names of the action input/output parameters
    # as all parameters have the suffix of Parameter
    if parameter_name == "QueryParameter":
        parameter_name = "query"
    else:
        parameter_name = action_parameter_values.pop("name", None)
        parameter_name = parameter_name.lower().replace(" ", "_")

    action_parameter_values.pop("schema", None)
    action_parameter_values.pop("format", None)
    action_parameter_values.pop("offload", None)
    action_parameter_values.pop("examples", None)
    action_parameter_values.pop("items", None)

    # cdodge: default values are applied by SurfaceCommand before the function
    # is invoked. Also, as default values, we expose secret key names (not the
    # actual secret values themselves). So preferably, we'd rather not have
    # the key names show up in our plugin generated code.
    action_parameter_values.pop("default", None)

    return parameter_name, action_parameter_values


def get_versions(connector_manifest: dict) -> Tuple[str, int]:
    """
    To take the version that is used in the manifest.yaml file and convert it
    to the format that is needed by the plugin.spec.yaml file for both the plugin version and connection version

    :param dict connector_manifest: A dict object created from reading in the manifest.yaml file
    :return Tuple[str, int]: The version and connection version that will be used in the plugin.spec.yaml file
    """
    # connectors do version numbers as (major.minor.build_number)
    # we need to drop the build number to not make a new plugin release each build
    version = connector_manifest.get("version")

    # we need to make sure that we are not using a version with a leading 0
    if version[0] == "0":
        connection_version = 1
    else:
        connection_version = int(version[0])

    return version, connection_version


def format_title(title: str) -> str:
    """
    Within the plugin the tile of each object needs to be in a certain format for our validation,
    This method will take a tile in the manifest.yaml format and convert it to the plugin.spec.yaml format

    :param str title: Raw title of object that is taken form the manifest.yaml file
    :return str: Parsed title in the plugin.spec.yaml format
    """

    title = title.split(" ")

    # titles can only be 6 words long
    if len(title) > 6:
        title = title[:6]

    title_string = ""

    # make sure that each work is a capital unless its at the end
    # or else if the word in title_validation_list we need to leave it as lower case
    for index, value in enumerate(title):

        if index == 0:
            if len(value) > 1:
                title_string = f"{title_string} {value[0].upper() + value[1:]}"
            else:
                title_string = f"{title_string} {value.capitalize()}"

        elif value.capitalize() in title_validation_list:
            low_value = value.lower()

            if (index + 1) == len(title) and low_value in ["by", "of"]:
                title_string = f"{title_string} {low_value.capitalize()}"
            else:
                title_string = f"{title_string} {low_value}"
        elif len(value) > 1:
            title_string = f"{title_string} {value[0].upper() + value[1:]}"
        else:
            title_string = f"{title_string} {value.capitalize()}"

    # make sure there no whitespace and not full stops
    title_string = title_string.strip()
    title_string = title_string.removesuffix(".")

    return title_string


def get_user_type(connector_folder: str) -> str:
    """
    If there is json files, they need to be modified, so making the user root to have permissions

    :param str connector_folder: The path to the source folder of the connector
    :return str: The user that will be used
    """

    app_folder = ""
    for directory in os.listdir(connector_folder):
        if directory.endswith('_app'):
            app_folder = os.path.join(connector_folder, directory)
            break

    if not app_folder:

        # if there is no app folder, this is a Surcom Connector and
        # check if there is a 'functions' folder
        functions_folder = os.path.join(connector_folder, "functions")

        if os.path.exists(functions_folder):
            app_folder = functions_folder

        else:
            # If there is no app folder or functions folder, we can't proceed
            # so we will raise an error
            raise SystemError(f"No app_folder or functions_folder were found in {connector_folder}")


    # cdodge: this hard coded servicenow path seems wrong and throws an
    # error if we try to convert any other connector. So, just do
    # a path.exists() and skip this, until this is fixed
    if os.path.exists(app_folder):
        for filename in os.listdir(app_folder):
            print(f"app - {filename = }")
            if filename.endswith('.json'):
                return "root"

    # check the types folder
    types_folder = os.path.join(connector_folder, "types")
    if os.path.exists(types_folder):
        for filename in os.listdir(types_folder):
            print(f"types - {filename = }")
            if filename.endswith('.json'):
                return "root"

    return "nobody"


def format_spec_file( # pylint: disable=too-many-positional-arguments
    connector_manifest: dict,
    name: str,
    title: str,
    version: str,
    connection_version: int,
    actions: dict,
    user_needed: str
) -> dict:
    """
    To take all of the objects that have been extracted then parsed form the manifest file,
    and add them to the template for our plugin spec

    :param dict connector_manifest: A dict object created from reading in the manifest.yaml file
    :param str name: The parsed name that will be used in the plugin spec
    :param str title: The parsed title that will be used in the plugin spec
    :param str version: The parsed version that will be used in the plugin spec
    :param int connection_version: The parsed connection version that will be used in the plugin spec
    :param dict actions: The parsed action object that will be used in the plugin spec
    :param str user_needed: If the plugin will require root to be run or not
    :return dict: The formatted spec file object
    """

    new_spec_file = {}
    new_spec_file["plugin_spec_version"] = "v2"
    new_spec_file["extension"] = "plugin"
    new_spec_file["products"] = ["insightconnect"]
    new_spec_file["name"] = name
    new_spec_file["title"] = title
    new_spec_file["description"] = "PLACEHOLDER"
    new_spec_file["version"] = version
    new_spec_file["connection_version"] = connection_version
    new_spec_file["supported_versions"] = ["PLACEHOLDER"]
    new_spec_file["vendor"] = "rapid7"
    new_spec_file["support"] = "rapid7"
    new_spec_file["status"] = ["PLACEHOLDER"]
    new_spec_file["resources"] = {
        "source_url": "PLACEHOLDER",
        "license_url": "PLACEHOLDER",
        "vendor_url": "PLACEHOLDER",
    }
    new_spec_file["tags"] = ["PLACEHOLDER", "PLACEHOLDER2"]
    new_spec_file["sdk"] = {"type": "slim", "version": "6.2.2", "user": user_needed}
    new_spec_file["hub_tags"] = {
        "use_cases": ["data_enrichment"],
        "keywords": ["PLACEHOLDER"],
        "features": ["PLACEHOLDER"],
    }
    new_spec_file["key_features"] = ["PLACEHOLDER"]
    new_spec_file["requirements"] = ["PLACEHOLDER"]
    new_spec_file["troubleshooting"] = "PLACEHOLDER"
    new_spec_file["version_history"] = [
        f"{version} - conversion of the {name} plugin",
        "1.0.0 - Initial plugin",
    ]
    new_spec_file["links"] = [f"[{name}] https://extensions.rapid7.com/extension/"]
    new_spec_file["references"] = [f"[{name}] https://extensions.rapid7.com/extension/"]

    new_spec_file["is_connector"] = True
    new_spec_file["actions"] = actions

    new_spec_file["original_connector_name"] = f"{connector_manifest.get('id')}"
    new_spec_file["original_connector_version"] = f"v{connector_manifest.get('version')}"
    new_spec_file["enable_cache"] = True

    return new_spec_file
