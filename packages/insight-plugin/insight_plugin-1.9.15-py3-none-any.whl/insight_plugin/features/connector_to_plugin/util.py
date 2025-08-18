import ast
import os
from functools import singledispatch
from typing import Dict, List, Union

from insight_plugin import (
    ROOT_DIR,
    FILE_ENCODING,
    BASE_PREFIX,
    BASE_MODULE,
    BASE_PACKAGE,
)
from insight_plugin.features.connector_to_plugin.help.constants import (
    FileExtensionsConstants,
)
from insight_plugin.features.common.exceptions import InsightException
from insight_plugin.features.common.plugin_spec_util import (
    PluginSpecConstants as Constants,
)
from insight_plugin.features.common.plugin_spec_util import PluginSpecTypes
from insight_plugin.features.common.template_util import Templates
from insight_plugin.features.create.util import (
    create_manifest,
    create_makefile,
    create_triggers,
    create_tasks,
    create_help_md,
    create_checksum,
)
from insight_plugin.features.connector_to_plugin.help.help_util import (
    copy_archived_packages,
    copy_app_folder_to_utils,
    copy_types_folder,
    copy_images,
    copy_spec_file,
)
from insight_plugin.features.connector_to_plugin.models import (
    CreateInitBase,
    SchemaSpec,
)
from insight_plugin.features.connector_to_plugin.models.actions_schema import (
    CreateActionInit,
    CreateActionsInit,
    ActionSchemaSpec,
)
from insight_plugin.features.connector_to_plugin.models.connection_schema import (
    CreateConnectionInit,
    ConnectionSchemaSpec,
)
from insight_plugin.features.connector_to_plugin.models.util_schema import (
    CreateUtilInit,
)
from insight_plugin.features.connector_to_plugin.models.plugin_schem import (
    CreatePluginInit,
)

list_of_archived_packages = []
_ACTION_TYPE_TO_TEMPLATE = {
    None: 'connector/actions/action/action.py.jinja',
    'import': 'connector/actions/action/action_import.py.jinja',
}


def create_action_py( # pylint: disable=too-many-positional-arguments
    spec: PluginSpecTypes.Spec,
    action_name: str,
    action_description: str,
    action_dir_name: str,
    connector_name: str,
    source_dir_name: str,
    template_filename: str,
) -> None:
    """
    Creates the action.py for a plugin action.
    :param spec: The plugin spec dictionary
    :param action_name: The name of this current action
    :param action_description: The description of this current action
    :param action_dir_name: The absolute path to the icon_{plugin}/actions/{action} directory
    :param connector_name: The plugin name
    :param source_dir_name: The path to the connector folder
    :return:
    """
    output_file = os.path.join(action_dir_name, "action.py")
    action_custom_import = find_function_import(
        function_name=action_name,
        connector_name=connector_name,
        source_dir_name=source_dir_name,
    )
    action_spec_input = (
        spec.get(Constants.ACTIONS, {}).get(action_name, {}).get(Constants.INPUT)
    )

    if action_spec_input is None:
        action_spec_input = {}

    create_file_from_template(
        template_filename=template_filename,
        inputs={
            "base_module": BASE_MODULE,
            "action": action_name,
            "description": action_description,
            "inputs": action_spec_input,
            "action_custom_import": action_custom_import,
        },
        output_filename=output_file,
    )


@singledispatch
def create_schema(spec: SchemaSpec, directory_path: str) -> None:
    raise NotImplementedError("Unsupported spec type")


@create_schema.register
def create_connection_schema(spec: ConnectionSchemaSpec, directory_path: str) -> None:
    """
    Creates the schema.py for the plugin connection.
    :param spec: The plugin schema ConnectionSchemaSpec
    :param directory_path: The absolute path to the icon_{plugin}/connection directory
    :return:
    """
    output_file = os.path.join(directory_path, "schema.py")
    create_file_from_template(
        template_filename="connector/connection/schema.py.jinja",
        inputs={
            "base_module": BASE_MODULE,
            "connection": spec.connection,
            "input": spec.input,
            "spec": spec.spec,
        },
        output_filename=output_file,
    )


@create_schema.register
def create_action_schema(spec: ActionSchemaSpec, directory_path: str) -> None:
    """
    Creates the schema.py for a plugin action.
    :param spec: The plugin schema ActionSchemaSpec
    :param directory_path: The absolute path to the icon_{plugin}/actions/{action} directory
    :return:
    """
    output_file = os.path.join(directory_path, "schema.py")
    create_file_from_template(
        template_filename="connector/actions/action/schema.py.jinja",
        inputs={
            "base_module": BASE_MODULE,
            "action": spec.action,
            "description": spec.description,
            "input": spec.input,
            "output": spec.output,
            "spec": spec.spec,
        },
        output_filename=output_file,
    )


def create_actions(
    spec: PluginSpecTypes.Spec,
    actions_dir_name: str,
    connector_name: str,
    source_dir_name: str,
) -> None:
    """
    Creates the __init__.py for the plugin actions directory and calls the functions
    to create the __init__.py, schema.py, and action.py for each action.
    :param spec: The plugin spec dictionary
    :param actions_dir_name: The absolute path to the icon_{plugin}/actions directory
    :param connector_name: The Connector name
    :param source_dir_name: The path to the connector folder
    :return:
    """
    print("Writing actions")
    create_directory(output_dir_name=actions_dir_name)
    create_init(
        CreateActionsInit(
            inputs={"actions": spec.get(Constants.ACTIONS, {}).keys()},
            target_dir_name=actions_dir_name,
            template_filename="connector/actions/__init__.py.jinja",
        )
    )
    # Create subdirectories for each action under the actions directory
    for action_name in spec.get(Constants.ACTIONS, {}):
        action_dir_name = os.path.join(actions_dir_name, action_name)
        create_directory(output_dir_name=action_dir_name)
        action_spec = spec.get(Constants.ACTIONS, {}).get(action_name, {})
        # Create __init__.py, action.py, and schema.py under each action directory
        create_init(
            CreateActionInit(
                inputs={"action": action_name},
                template_filename="connector/actions/action/__init__.py.jinja",
                target_dir_name=action_dir_name,
            )
        )
        action_type = spec.get(Constants.ACTIONS, {}).get(action_name, {}).get('action_type')
        create_action_py(
            spec=spec,
            action_name=action_name,
            action_description=spec.get(Constants.ACTIONS, {})
            .get(action_name, {})
            .get(Constants.DESCRIPTION, ""),
            action_dir_name=action_dir_name,
            connector_name=connector_name,
            source_dir_name=source_dir_name,
            template_filename=_ACTION_TYPE_TO_TEMPLATE[action_type],
        )
        create_schema(
            ActionSchemaSpec(
                input=action_spec.get(Constants.INPUT, {}),
                output=action_spec.get(Constants.OUTPUT, {}),
                description=action_spec.get(Constants.DESCRIPTION, ""),
                spec=spec,
                action=action_name,
            ),
            action_dir_name,
        )
    print("Created actions")


def create_file_from_template(
    template_filename: str,
    inputs: Dict[str, Union[str, List[str]]],
    output_filename: str,
) -> None:
    """
    Input the template, the values to fill the template in with, and the output file.
    Handles exceptions for missing values and file IO.
    :param template_filename: The name of the template file to be filled in
    :param inputs: The values to populate the template with
    :param output_filename: The name of the resulting file the populated template will be written to
    :return:
    """
    templates = Templates(os.path.join(ROOT_DIR, "templates"))
    try:
        print(f"Filling {template_filename}")
        file_content = templates.fill(template_name=template_filename, inputs=inputs)
        print(f"Writing {output_filename}")
        with open(output_filename, "w", encoding=FILE_ENCODING) as output_file:
            output_file.write(file_content)
        print(f"Created {output_file.name}")
    except KeyError as error:
        raise InsightException(
            message=f"The plugin spec is missing the setting for {error.args[0]}",
            troubleshooting=f'Add the line "{error.args[0]}: <VALUE>" to your plugin spec.',
        )
    except PermissionError:
        raise InsightException(
            message=f"Lacking permission to write the file {output_filename} to the filesystem",
            troubleshooting="Verify that this user is permitted to write to disk here, "
            "or run this command with elevated privileges.",
        )
    except BrokenPipeError:
        raise InsightException(
            message=f"Writing {output_filename} to filesystem was interrupted by a broken pipe",
            troubleshooting="Try running the command again, with full access to the disk.",
        )


def create_init(source_init: CreateInitBase):
    """
    Creates the __init__.py for the icon{plugin}/{source_dir_name} directory.
    :param source_init: CreateInitBase
    :return:
    """
    output_file = os.path.join(source_init.target_dir_name, "__init__.py")
    create_file_from_template(
        template_filename=source_init.template_filename,
        inputs=source_init.inputs,
        output_filename=output_file,
    )


def create_directory(output_dir_name: str) -> None:
    """
    Safely creates directory and handles exceptions for missing values and disk IO.
    :param output_dir_name: The name of the directory to create
    :return: whether file created
    """
    try:
        print(f"Writing {output_dir_name}/")
 
        os.mkdir(f"{output_dir_name}")
        print(f"Created {output_dir_name}/")
    except FileExistsError:
        return 0
    except PermissionError:
        raise InsightException(
            message=f"Lacking permission to write the file {output_dir_name} to the filesystem",
            troubleshooting="Verify that this user is permitted to write to disk here, "
            "or run this command with elevated privileges.",
        )
    except BrokenPipeError:
        raise InsightException(
            message=f"Writing {output_dir_name} to filesystem was interrupted by a broken pipe",
            troubleshooting="Try running the command again, with full access to the disk.",
        )


def create_util(target_dir_name: str, source_dir_name: str) -> None:
    """
    Creates the util directory and creates
    the __init__.py in the util directory.
    :param target_dir_name: The absolute path to the icon_{plugin}/util directory
    :param source_dir_name: The path to the connector file
    :return:
    """
    create_directory(output_dir_name=target_dir_name)
    create_init(
        CreateUtilInit(
            target_dir_name=target_dir_name,
            template_filename="connector/util/__init__.py.jinja",
        ),
    )

    output_file = os.path.join(target_dir_name, "icon_plugin_wrapper.py")
    create_file_from_template(
        template_filename="connector/util/icon_plugin_wrapper.py.jinja",
        inputs={},
        output_filename=output_file,
    )

    copy_app_folder_to_utils(source_dir=source_dir_name, target_dir=target_dir_name)


def create_setup_py(spec: PluginSpecTypes.Spec, target_dir_name: str, prefix: str):
    """
    Creates the setup.py for the plugin.
    :param spec: The plugin spec dictionary
    :param target_dir_name: The absolute path to the target directory
    :param prefix: The prefix, either icon or komand
    :return:
    """
    output_file = os.path.join(target_dir_name, "setup.py")
    create_file_from_template(
        template_filename="connector/setup.py.jinja",
        inputs={
            "name": spec.get("name"),
            "vendor": spec.get("vendor"),
            "version": spec.get("version"),
            "description": spec.get("description"),
            "base_package": BASE_PACKAGE,
            "prefix": prefix,
        },
        output_filename=output_file,
    )


def find_function_import(
    function_name: str, connector_name: str, source_dir_name: str
) -> str:
    """
    Search python modules in a util_path for a function and generate an import statement.
    :param function_name: The action function's name to look up
    :param connector_name: The plugin name
    :param source_dir_name: The path to the connector folder
    :return:
    """

    app_folder_path = ""

    for root, dirs, _ in os.walk(source_dir_name):
        # Check if any subdirectory starts with the given prefix
        for dir_name in dirs:
            if dir_name.endswith("_app"):
                app_folder_path = (os.path.join(root, dir_name))
                break

    if not app_folder_path:
        # if there is no app folder, this is a Surcom Connector and
        # check if there is a 'functions' folder
        functions_folder = os.path.join(source_dir_name, "functions")
        function_source_file = f"fn_{function_name}"
        function_source_path = os.path.join(functions_folder, f"{function_source_file}.py")

        if os.path.exists(functions_folder) and os.path.exists(function_source_path):
            return f"from {connector_name}.util.functions.{function_source_file} import {function_name}"

    if app_folder_path:
        init_file = os.path.join(app_folder_path, "__init__.py")

        print(f"{init_file = }")

        with open(init_file, "r", encoding="utf-8") as file:
            file_content = file.read()

        # Parse the content of the file to an Abstract Syntax Tree (AST)
        tree = ast.parse(file_content)

        # Iterate through all nodes in the AST
        for node in ast.walk(tree):
            # Check if the node is a 'from ... import ...' statement
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if function_name == alias.name:
                        return f"from {connector_name}.util.{node.module.rstrip('.py')} import {alias.name}"

    return ""


def create_connection_py(
    spec: PluginSpecTypes.Spec,
    connection_dir_name: str,
) -> None:
    """
    Creates the connection.py for the plugin connection.
    :param spec: The plugin spec dictionary
    :param connection_dir_name: The absolute path to the icon_{plugin}/connection directory
    :return:
    """
    output_file = os.path.join(connection_dir_name, "connection.py")
    connection_spec = spec.get(Constants.CONNECTIONS, {})

    if connection_spec is None:
        connection_spec = {}

    create_file_from_template(
        template_filename="connector/connection/connection.py.jinja",
        inputs={"base_module": BASE_MODULE, "inputs": connection_spec},
        output_filename=output_file,
    )


def create_connection(
    spec: PluginSpecTypes.Spec,
    connection_dir_name: str,
) -> None:
    """
    Calls the functions to create the __init__.py, connection.py,
    and schema.py for the plugin connection.
    Note that a plugin may have only no or one connection.
    :param spec: The plugin spec dictionary
    :param connection_dir_name: The absolute path to the icon_{plugin}/connection directory
    :return:
    """
    print("Writing connection")
    create_directory(output_dir_name=connection_dir_name)
    # Create __init__.py, connection.py, and schema.py under the new connection directory
    create_init(
        CreateConnectionInit(
            target_dir_name=connection_dir_name,
            template_filename="connector/connection/__init__.py.jinja",
        )
    )
    create_connection_py(
        spec=spec,
        connection_dir_name=connection_dir_name,
    )
    connection_spec = spec.get(Constants.CONNECTIONS, {})
    create_schema(
        ConnectionSchemaSpec(
            connection=connection_spec,
            input=connection_spec.get(Constants.INPUT, {}),
            spec=spec,
        ),
        connection_dir_name,
    )
    print("Created connection")


def create_requirements_txt(target_dir_name: str, source_dir_name: str) -> None:
    """
    Creates the requirements.txt for the plugin, based on the source plugin requirements.txt
    :param target_dir_name: The absolute path to the target directory
    :param source_dir_name: The absolute path to the connector zip file
    :return:
    """
    output_file = os.path.join(target_dir_name, "requirements.txt")
    source_requirements = os.path.join(source_dir_name, "requirements.txt")

    with open(source_requirements, "r", encoding="utf-8") as file:
        content = ""
        for line in file:
            package = line.rstrip("\n")
            if package.endswith(FileExtensionsConstants.GZ) or package.endswith(
                FileExtensionsConstants.ZIP
            ):
                copy_archived_packages(
                    source_dir=source_dir_name,
                    target_dir=target_dir_name,
                    package=package,
                )
                list_of_archived_packages.append(package)
            else:
                content += line

        create_file_from_template(
            template_filename="connector/requirements.txt.jinja",
            inputs={
                "packages": content,
            },
            output_filename=output_file,
        )


def create_dockerignore(target_dir_name: str, connector_name_prefixed: str):
    """
    Creates the .dockerignore for the plugin.
    :param target_dir_name: The absolute path to the target directory
    :param connector_name_prefixed: The name of the connector with prefix
    :return:
    """
    output_file = os.path.join(target_dir_name, ".dockerignore")
    create_file_from_template(
        template_filename="connector/.dockerignore.jinja",
        inputs={
            "connector_name_prefixed": connector_name_prefixed,
            "archived_packages": list_of_archived_packages,
        },
        output_filename=output_file,
    )


def create_entrypoint(
    spec: PluginSpecTypes.Spec,
    target_dir_name: str,
    prefix: str,
):
    """
    Creates the entrypoint.sh for the plugin.
    :param spec: The plugin spec with values to fill in to the Dockerfile
    :param target_dir_name: The absolute path to the target directory
    :param prefix: The prefix, either icon or komand
    :return:
    """
    output_file = os.path.join(target_dir_name, "entrypoint.sh")
    create_file_from_template(
        template_filename="connector/entrypoint.sh.jinja",
        inputs={
            "plugin_name": spec["name"],
            "prefix": prefix,
        },
        output_filename=output_file,
    )


def create_dockerfile(spec: PluginSpecTypes.Spec, target_dir_name: str, prefix: str):
    """
    Creates the Dockerfile for the plugin.
    :param spec: The plugin spec with values to fill in to the Dockerfile
    :param target_dir_name: The absolute path to the target directory
    :param prefix: The prefix, either icon or komand
    :return:
    """
    sdk_field_name = "sdk"
    sdk_type = spec.get(sdk_field_name, {}).get("type", "full")
    sdk_version = spec.get(sdk_field_name, {}).get("version", "latest")
    sdk_user = spec.get(sdk_field_name, {}).get("user", "nobody")
    sdk_packages = spec.get(sdk_field_name, {}).get("packages")
    sdk_types = {
        "full": {
            "name": "rapid7/insightconnect-python-3-plugin",
            "version": sdk_version,
            "install_package_command": "apk update && apk add --no-cache --virtual",
        },
        "slim": {
            "name": "rapid7/insightconnect-python-3-slim-plugin",
            "version": sdk_version,
            "install_package_command": "apt-get update && apt-get install",
        },
    }
    output_file = os.path.join(target_dir_name, "Dockerfile")
    create_file_from_template(
        template_filename="connector/Dockerfile.jinja",
        inputs={
            "sdk_type": sdk_types[sdk_type]["name"],
            "sdk_version": sdk_types[sdk_type]["version"],
            "vendor": spec["vendor"],
            "packages": sdk_packages,
            "install_package_command": sdk_types[sdk_type]["install_package_command"],
            "user": sdk_user,
            "plugin_name": spec["name"],
            "prefix": prefix,
            "archived_packages": list_of_archived_packages,
        },
        output_filename=output_file,
    )


def handle_connector_to_plugin_create(
    spec: PluginSpecTypes.Spec,
    target_dir_name: str,
    source_dir_name: str,
) -> None:
    """
    This function runs the create_files_connector_to_plugin function based on whether the user is creating
    :param spec: The plugin spec dictionary
    :param target_dir_name: The absolute path to the target directory
    :return:
    """
    prefix = BASE_PREFIX

    # Establish directory name - By default we want it to be 'target_dir_name'
    dir_name = target_dir_name

    create_files_connector_to_plugin(
        spec=spec,
        dir_name=dir_name,
        prefix=prefix,
        source_dir_name=source_dir_name,
    )


def create_files_connector_to_plugin(
    spec: PluginSpecTypes.Spec,
    dir_name: str,
    prefix: str,
    source_dir_name: str,
) -> None:
    """
    This handles all the other 'create_{file}' functions and merges them into one.
    :param spec: The plugin spec dictionary
    :param dir_name: The absolute path to the target
    :param prefix: The prefix, either icon or kommand
    :return:
    """

    connector_name = spec.get(Constants.NAME, "")
    connector_name_prefixed = f"{prefix}_{connector_name}"

    target_dir_name = f'{dir_name}/{spec["name"]}'
    target_dir_name_icon = os.path.join(target_dir_name, connector_name_prefixed)
    util_dir_name = os.path.join(target_dir_name_icon, "util")

    for output_dir_name in [target_dir_name, target_dir_name_icon]:
        create_directory(output_dir_name=output_dir_name)

    create_requirements_txt(
        target_dir_name=target_dir_name,
        source_dir_name=source_dir_name,
    )
    create_dockerignore(
        target_dir_name=target_dir_name, connector_name_prefixed=connector_name_prefixed
    )
    create_entrypoint(
        spec=spec,
        target_dir_name=target_dir_name,
        prefix=prefix,
    )
    create_dockerfile(spec=spec, target_dir_name=target_dir_name, prefix=prefix)
    create_init(
        source_init=CreatePluginInit(
            target_dir_name=target_dir_name_icon,
            template_filename="connector/__init__.py.jinja",
        ),
    )

    create_util(target_dir_name=util_dir_name, source_dir_name=source_dir_name)

    create_connection(
        spec=spec,
        connection_dir_name=os.path.join(target_dir_name_icon, Constants.CONNECTIONS),
    )

    create_actions(
        spec=spec,
        actions_dir_name=os.path.join(target_dir_name_icon, Constants.ACTIONS),
        connector_name=connector_name_prefixed,
        source_dir_name=source_dir_name,
    )

    # to keep validators happy we need to add in some images
    copy_images(target_dir=target_dir_name)

    copy_spec_file(target_dir_name=target_dir_name)

    # these following methods should not require any changes from the standard create method
    create_manifest(
        spec=spec,
        bin_dir_name=os.path.join(target_dir_name, Constants.MANIFEST),
        prefix=prefix,
    )
    create_setup_py(spec=spec, target_dir_name=target_dir_name, prefix=prefix)
    create_makefile(target_dir_name=target_dir_name)
    create_triggers(
        spec=spec,
        triggers_dir_name=os.path.join(target_dir_name_icon, Constants.TRIGGERS),
    )
    create_tasks(
        spec=spec, tasks_dir_name=os.path.join(target_dir_name_icon, Constants.TASKS)
    )
    create_help_md(spec=spec, target_dir_name=target_dir_name)
    create_checksum(spec=spec, target_dir_name=target_dir_name)

    # copying across the type files for the plugin to use
    types_dir = os.path.join(target_dir_name_icon, "types")
    create_directory(output_dir_name=types_dir)
    copy_types_folder(source_dir=source_dir_name, target_dir=types_dir)

    # run black to try and format the code to our normal standards
    os.system(f"black {target_dir_name}")  # nosec
