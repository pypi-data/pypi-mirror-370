import os
from os.path import exists
from typing import List, Dict, Optional

import logging
import re

from insight_plugin import (
    ROOT_DIR,
    FILE_ENCODING,
    BASE_PREFIX,
    BASE_MODULE,
    BASE_PACKAGE,
    KOMAND_PREFIX,
)
from insight_plugin.features.common.checksum_util import ChecksumUtil
from insight_plugin.features.common.plugin_spec_util import PluginSpecTypes
from insight_plugin.features.common.plugin_spec_util import (
    PluginSpecConstants as Constants,
)
from insight_plugin.features.connector_to_plugin.help.help_util import copy_images
from insight_plugin.features.convert_event_source.util import get_rapid_kit_version
from insight_plugin.features.common.exceptions import InsightException
from insight_plugin.features.create.plugin_to_helpmd import ConvertPluginToHelp
from insight_plugin.features.common.template_util import Templates
from insight_plugin.constants import VALID_IGNORE_FILES


def strip_newline(sub_desc: dict) -> str:
    return re.sub("[\n]", "", sub_desc)


def create_checksum(spec: PluginSpecTypes.Spec, target_dir_name: str):
    """
    Creates the .CHECKSUM for the plugin.
    :param spec: The plugin spec dictionary
    :param target_dir_name: The absolute path to the target directory
    :return:
    """
    logger = logging.getLogger("CreateUtil")
    logger.info("Writing .CHECKSUM")
    prefix = get_prefix(spec=spec, target_dir_name=target_dir_name)
    output_filename = os.path.join(target_dir_name, ".CHECKSUM")
    with open(output_filename, "w", encoding=FILE_ENCODING) as output_file:
        output_sum = ChecksumUtil.create_checksums(target_dir_name, spec, prefix)
        output_file.write(output_sum)

    logger.info("Created .CHECKSUM")


def create_file_from_template(template_filename: str, inputs: Dict[str, str], output_filename: str):
    """
    Input the template, the values to fill the template in with, and the output file.
    Handles exceptions for missing values and file IO.
    :param template_filename: The name of the template file to be filled in
    :param inputs: The values to populate the template with
    :param output_filename: The name of the resulting file the populated template will be written to
    :return:
    """
    logger = logging.getLogger("CreateUtil")
    templates = Templates(os.path.join(ROOT_DIR, "templates"))
    try:
        logger.info(f"Filling {template_filename}")
        file_content = templates.fill(template_filename, inputs)
        logger.info(f"Writing {output_filename}")
        with open(output_filename, "w", encoding=FILE_ENCODING) as output_file:
            output_file.write(file_content)
        logger.info(f"Created {output_file.name}")
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


def create_directory(output_dir_name: str):
    """
    Safely creates directory and handles exceptions for missing values and disk IO.
    :param output_dir_name: The name of the directory to create
    :return: whether file created
    """
    logger = logging.getLogger("CreateUtil")
    try:
        if not exists(output_dir_name):
            logger.info(f"Writing {output_dir_name}/")
            os.mkdir(output_dir_name)
            logger.info(f"Created {output_dir_name}/")
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


def create_help_md(spec: PluginSpecTypes.Spec, target_dir_name: str):
    """
    Creates the help.md for the plugin.
    :param spec: The plugin spec dictionary
    :param target_dir_name: The absolute path to the target directory
    :return:
    """
    logger = logging.getLogger("CreateUtil")
    logger.info("Writing help.md")
    # new_for_markdown() will create a help.md file in the directory path provided
    help_md = ConvertPluginToHelp.new_for_markdown(spec, target_dir_name)
    help_md.convert_function()
    logger.info("Created help.md")


def create_requirements_txt(target_dir_name: str, _type: str = "plugin"):
    """
    Creates the requirements.txt for the plugin.
    :param _type: If plugin or event source
    :param target_dir_name: The absolute path to the target directory
    :return:
    """
    output_file = os.path.join(target_dir_name, "requirements.txt")
    inputs = {}
    if _type == "event_source":
        rapidkit_version = get_rapid_kit_version()
        template_filename = "event_source/requirements.txt.jinja"
        if rapidkit_version:
            inputs["rapidkit_version"] = f"=={rapidkit_version}"
    else:
        template_filename = "requirements.txt.jinja"
    if not exists(output_file):
        create_file_from_template(
            template_filename=template_filename,
            inputs=inputs,
            output_filename=output_file,
        )


def create_makefile(target_dir_name: str):
    """
    Creates the Makefile for the plugin.
    :param target_dir_name: The absolute path to the target directory
    :return:
    """
    output_file = os.path.join(target_dir_name, "Makefile")
    if not exists(output_file):
        create_file_from_template(template_filename="Makefile.jinja", inputs={}, output_filename=output_file)


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
        template_filename="setup.py.jinja",
        inputs={
            "name": spec.get("name"),
            "vendor": spec.get("vendor"),
            "version": spec.get("version"),
            "description": strip_newline(spec.get("description")),
            "base_package": BASE_PACKAGE,
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
    sdk_custom_cmd = spec.get(sdk_field_name, {}).get("custom_cmd")
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
        template_filename="Dockerfile.jinja",
        inputs={
            "sdk_type": sdk_types[sdk_type]["name"],
            "sdk_version": sdk_types[sdk_type]["version"],
            "vendor": spec["vendor"],
            "packages": sdk_packages,
            "install_package_command": sdk_types[sdk_type]["install_package_command"],
            "custom_cmd": sdk_custom_cmd,
            "user": sdk_user,
            "plugin_name": spec["name"],
            "prefix": prefix,
        },
        output_filename=output_file,
    )


def create_dockerignore(target_dir_name: str):
    """
    Creates the .dockerignore for the plugin.
    :param target_dir_name: The absolute path to the target directory
    :return:
    """
    output_file = os.path.join(target_dir_name, ".dockerignore")
    if not exists(output_file):
        create_file_from_template(
            template_filename=".dockerignore.jinja",
            inputs={},
            output_filename=output_file,
        )


def create_manifest(spec: PluginSpecTypes.Spec, bin_dir_name: str, prefix: Optional[str] = "icon"):
    """
    Creates the bin directory and creates the
    executable manifest binary of this plugin.
    :param prefix: Plugin prefix, either icon or komand.
    :param bin_dir_name: Path to the bin directory: {plugin}/bin
    :param spec: The plugin spec with values to fill in to the manifest
    :return:
    """
    create_directory(bin_dir_name)
    output_file = os.path.join(bin_dir_name, f'{prefix}_{spec.get("name")}')
    create_file_from_template(
        template_filename="bin/plugin.jinja",
        inputs={
            "base_module": BASE_MODULE,
            "base_prefix": prefix,
            "name": spec.get(Constants.NAME, ""),
            "title": spec.get(Constants.TITLE, ""),
            "vendor": spec.get(Constants.VENDOR, ""),
            "version": spec.get(Constants.VERSION, ""),
            "description": strip_newline(spec.get("description")),
            "triggers": list(spec.get(Constants.TRIGGERS, {}).keys()),
            "actions": list(spec.get(Constants.ACTIONS, {}).keys()),
            "tasks": list(spec.get(Constants.TASKS, {}).keys()),
        },
        output_filename=output_file,
    )


def create_util(util_dir_name: str):
    """
    Creates the util directory and creates
    the __init__.py in the util directory.
    :param util_dir_name: The absolute path to the icon_{plugin}/util directory
    :return:
    """
    create_directory(util_dir_name)

    output_file = os.path.join(util_dir_name, "__init__.py")
    if not exists(output_file):
        create_file_from_template(
            template_filename="plugin/util/__init__.py.jinja",
            inputs={},
            output_filename=output_file,
        )


def create_triggers_init(triggers: List[str], triggers_dir_name: str):
    """
    Creates the __init__.py for the plugin triggers directory.
    :param triggers: List of the names of the triggers in the spec
    :param triggers_dir_name: The absolute path to the icon_{plugin}/triggers directory
    :return:
    """
    output_file = os.path.join(triggers_dir_name, "__init__.py")
    create_file_from_template(
        template_filename="plugin/triggers/__init__.py.jinja",
        inputs={"triggers": triggers},
        output_filename=output_file,
    )


def create_trigger_init(trigger_name: str, trigger_dir_name: str):
    """
    Creates the __init__.py for a plugin trigger.
    :param trigger_name: The name of this current trigger
    :param trigger_dir_name: The absolute path to the icon_{plugin}/triggers/{trigger} directory
    :return:
    """
    output_file = os.path.join(trigger_dir_name, "__init__.py")
    create_file_from_template(
        template_filename="plugin/triggers/trigger/__init__.py.jinja",
        inputs={
            "trigger": trigger_name,
        },
        output_filename=output_file,
    )


def create_trigger_py(
    spec: PluginSpecTypes.Spec,
    trigger_name: str,
    trigger_description: str,
    trigger_dir_name: str,
):
    """
    Creates the trigger.py for a plugin trigger.
    :param trigger_name: The name of this current trigger
    :param trigger_description: The description of this current trigger
    :param trigger_dir_name: The absolute path to the icon_{plugin}/triggers/{trigger} directory
    :return:
    """
    output_file = os.path.join(trigger_dir_name, "trigger.py")

    trigger_spec_input = spec.get(Constants.TRIGGERS, {}).get(trigger_name, "").get(Constants.INPUT)
    trigger_spec_output = spec.get(Constants.TRIGGERS, {}).get(trigger_name, "").get(Constants.OUTPUT)

    if trigger_spec_input is None:
        trigger_spec_input = {}

    if trigger_spec_output is None:
        trigger_spec_output = {}

    if not exists(output_file):
        create_file_from_template(
            template_filename="plugin/triggers/trigger/trigger.py.jinja",
            inputs={
                "base_module": BASE_MODULE,
                "trigger": trigger_name,
                "description": trigger_description,
                "inputs": trigger_spec_input,
                "outputs": trigger_spec_output,
            },
            output_filename=output_file,
        )


def create_trigger_schema(spec: PluginSpecTypes.Spec, trigger_name: str, trigger_dir_name: str):
    """
    Creates the schema.py for a plugin trigger.
    :param spec: The plugin spec dictionary
    :param trigger_name: The name of this trigger
    :param trigger_dir_name: The absolute path to the icon_{plugin}/triggers/{trigger} directory
    :return:
    """
    output_file = os.path.join(trigger_dir_name, "schema.py")
    trigger_spec = spec.get(Constants.TRIGGERS, {}).get(trigger_name, {})
    create_file_from_template(
        template_filename="plugin/triggers/trigger/schema.py.jinja",
        inputs={
            "base_module": BASE_MODULE,
            "trigger": trigger_name,
            "description": strip_newline(trigger_spec.get(Constants.DESCRIPTION, "")),
            "input": trigger_spec.get(Constants.INPUT, {}),
            "output": trigger_spec.get(Constants.OUTPUT, {}),
            "spec": spec,
        },
        output_filename=output_file,
    )


def create_triggers(spec: PluginSpecTypes.Spec, triggers_dir_name: str):
    """
    Creates the triggers directory and __init__.py and calls the functions
    to create the __init__.py, schema.py, and trigger.py for each trigger.
    :param spec: The plugin spec dictionary
    :param triggers_dir_name: The absolute path to the icon_{plugin}/triggers directory
    :return:
    """
    create_directory(triggers_dir_name)

    create_triggers_init(spec.get(Constants.TRIGGERS, {}).keys(), triggers_dir_name)

    # Create subdirectories for each trigger under the triggers directory
    for trigger_name in spec.get(Constants.TRIGGERS, {}):
        trigger_dir_name = os.path.join(triggers_dir_name, trigger_name)
        create_directory(trigger_dir_name)

        # Create __init__.py, trigger.py, and schema.py under each trigger directory
        create_trigger_init(trigger_name, trigger_dir_name)
        create_trigger_py(
            spec,
            trigger_name,
            spec.get(Constants.TRIGGERS, {}).get(trigger_name, {}).get(Constants.DESCRIPTION, {}),
            trigger_dir_name,
        )
        create_trigger_schema(spec, trigger_name, trigger_dir_name)


def create_connection_init(connection_dir_name: str):
    """
    Creates the __init__.py for the plugin connection.
    :param connection_dir_name: The absolute path to the icon_{plugin}/connection directory
    :return:
    """
    output_file = os.path.join(connection_dir_name, "__init__.py")
    create_file_from_template(
        template_filename="plugin/connection/__init__.py.jinja",
        inputs={},
        output_filename=output_file,
    )


def create_connection_py(spec: PluginSpecTypes.Spec, connection_dir_name: str, _type: str, name: str):
    """
    Creates the connection.py for the plugin connection.
    :param name: Plugin name
    :param spec: The plugin spec dictionary
    :param connection_dir_name: The absolute path to the icon_{plugin}/connection directory
    :return:
    """
    output_file = os.path.join(connection_dir_name, "connection.py")
    connection_spec = spec.get(Constants.CONNECTIONS, {})
    if connection_spec is None:
        connection_spec = {}
    inputs = {"base_module": BASE_MODULE, "inputs": connection_spec}
    if _type == "event_source":
        inputs["event_source_name"] = name
        template_filename = "event_source/connection/connection.py.jinja"
    else:
        template_filename = "plugin/connection/connection.py.jinja"

    if not exists(output_file):
        create_file_from_template(
            template_filename=template_filename,
            inputs=inputs,
            output_filename=output_file,
        )


def create_connection_schema(spec: PluginSpecTypes.Spec, connection_dir_name: str):
    """
    Creates the schema.py for the plugin connection.
    :param spec: The plugin spec dictionary
    :param connection_dir_name: The absolute path to the icon_{plugin}/connection directory
    :return:
    """
    output_file = os.path.join(connection_dir_name, "schema.py")
    connection_spec = spec.get(Constants.CONNECTIONS, {})
    create_file_from_template(
        template_filename="plugin/connection/schema.py.jinja",
        inputs={
            "base_module": BASE_MODULE,
            "connection": connection_spec,
            "input": connection_spec.get(Constants.INPUT, {}),
            "spec": spec,
        },
        output_filename=output_file,
    )


def create_connection(spec: PluginSpecTypes.Spec, connection_dir_name: str, _type: str = "plugin"):
    """
    Calls the functions to create the __init__.py, connection.py,
    and schema.py for the plugin connection.
    Note that a plugin may have only no or one connection.
    :param spec: The plugin spec dictionary
    :param connection_dir_name: The absolute path to the icon_{plugin}/connection directory
    :param _type: The type of of plugin / event source
    :return:
    """
    logger = logging.getLogger("CreateUtil")
    logger.info("Writing connection")
    plugin_name = spec.get(Constants.NAME, "")
    create_directory(connection_dir_name)
    # Create __init__.py, connection.py, and schema.py under the new connection directory
    create_connection_init(connection_dir_name)
    # Removes 'rk_' prefix to prevent errors when importing connection from pre-converted plugin
    if _type == "event_source":
        plugin_name = plugin_name.removeprefix("rk_")
    create_connection_py(spec, connection_dir_name, _type, plugin_name)
    create_connection_schema(spec, connection_dir_name)
    logger.info("Created connection")


def create_actions_init(actions_list: List[str], actions_dir_name: str):
    """
    Creates the __init__.py for the plugin actions directory.
    :param actions_list: List of the names of the actions in the spec
    :param actions_dir_name: The absolute path to the icon{plugin}/actions directory
    :return:
    """
    output_file = os.path.join(actions_dir_name, "__init__.py")
    create_file_from_template(
        template_filename="plugin/actions/__init__.py.jinja",
        inputs={"actions": actions_list},
        output_filename=output_file,
    )


def create_action_init(action_name: str, action_dir_name: str):
    """
    Creates the __init__.py for a plugin action.
    :param action_name: The name of this current action
    :param action_dir_name: The absolute path to the icon_{plugin}/actions/{action} directory
    :return:
    """
    output_file = os.path.join(action_dir_name, "__init__.py")
    create_file_from_template(
        template_filename="plugin/actions/action/__init__.py.jinja",
        inputs={"action": action_name},
        output_filename=output_file,
    )


def create_action_py(
    spec: PluginSpecTypes.Spec,
    action_name: str,
    action_description: str,
    action_dir_name: str,
):
    """
    Creates the action.py for a plugin action.
    :param spec: The plugin spec dictionary
    :param action_name: The name of this current action
    :param action_description: The description of this current action
    :param action_dir_name: The absolute path to the icon_{plugin}/actions/{action} directory
    :return:
    """
    output_file = os.path.join(action_dir_name, "action.py")

    action_spec_input = spec.get(Constants.ACTIONS, {}).get(action_name, "").get(Constants.INPUT)
    action_spec_output = spec.get(Constants.ACTIONS, {}).get(action_name, "").get(Constants.OUTPUT)

    if action_spec_input is None:
        action_spec_input = {}

    if action_spec_output is None:
        action_spec_output = {}

    if not exists(output_file):
        create_file_from_template(
            template_filename="plugin/actions/action/action.py.jinja",
            inputs={
                "base_module": BASE_MODULE,
                "action": action_name,
                "description": action_description,
                "inputs": action_spec_input,
                "outputs": action_spec_output,
            },
            output_filename=output_file,
        )


def create_action_schema(spec: PluginSpecTypes.Spec, action_name: str, action_dir_name: str):
    """
    Creates the schema.py for a plugin action.
    :param spec: The plugin spec dictionary
    :param action_name: The name of the current action
    :param action_dir_name: The absolute path to the icon_{plugin}/actions/{action} directory
    :return:
    """
    output_file = os.path.join(action_dir_name, "schema.py")
    action_spec = spec.get(Constants.ACTIONS, {}).get(action_name, {})
    create_file_from_template(
        template_filename="plugin/actions/action/schema.py.jinja",
        inputs={
            "base_module": BASE_MODULE,
            "action": action_name,
            "description": strip_newline(action_spec.get(Constants.DESCRIPTION, "")),
            "input": action_spec.get(Constants.INPUT, {}),
            "output": action_spec.get(Constants.OUTPUT, {}),
            "spec": spec,
        },
        output_filename=output_file,
    )


def create_actions(spec: PluginSpecTypes.Spec, actions_dir_name: str):
    """
    Creates the __init__.py for the plugin actions directory and calls the functions
    to create the __init__.py, schema.py, and action.py for each action.
    :param spec: The plugin spec dictionary
    :param actions_dir_name: The absolute path to the icon_{plugin}/actions directory
    :return:
    """
    logger = logging.getLogger("CreateUtil")
    logger.info("Writing actions")
    create_directory(actions_dir_name)
    create_actions_init(spec.get(Constants.ACTIONS, {}).keys(), actions_dir_name)
    # Create subdirectories for each action under the actions directory
    for action_name in spec.get(Constants.ACTIONS, {}):
        action_dir_name = os.path.join(actions_dir_name, action_name)
        create_directory(action_dir_name)
        # Create __init__.py, action.py, and schema.py under each action directory
        create_action_init(action_name, action_dir_name)
        create_action_py(
            spec,
            action_name,
            spec.get(Constants.ACTIONS, {}).get(action_name, {}).get(Constants.DESCRIPTION, ""),
            action_dir_name,
        )
        create_action_schema(spec, action_name, action_dir_name)
    logger.info("Created actions")


def create_tasks_init(tasks_list: List[str], tasks_dir_name: str):
    """
    Creates the __init__.py for the plugin tasks directory.
    :param tasks_list: List of the names of the tasks in the spec
    :param tasks_dir_name: The absolute path to the icon{plugin}/tasks directory
    :return:
    """
    output_file = os.path.join(tasks_dir_name, "__init__.py")
    create_file_from_template(
        template_filename="plugin/tasks/__init__.py.jinja",
        inputs={"tasks": tasks_list},
        output_filename=output_file,
    )


def create_task_init(task_name: str, task_dir_name: str):
    """
    Creates the __init__.py for a plugin task.
    :param task_name: The name of this current task
    :param task_dir_name: The absolute path to the icon_{plugin}/tasks/{task} directory
    :return:
    """
    output_file = os.path.join(task_dir_name, "__init__.py")
    create_file_from_template(
        template_filename="plugin/tasks/task/__init__.py.jinja",
        inputs={"task": task_name},
        output_filename=output_file,
    )


def create_task_py(task_name: str, task_description: str, task_dir_name: str, _type: str, name: str):
    """
    Creates the task.py for a plugin task.
    :param name: Name of the plugin
    :param task_name: The name of this current task
    :param task_description: The description of this current task
    :param task_dir_name: The absolute path to the icon_{plugin}/tasks/{task} directory
    :param _type: The type of this plugin task
    :return:
    """
    output_file = os.path.join(task_dir_name, "task.py")
    inputs = {
        "base_module": BASE_MODULE,
        "task": task_name,
        "description": task_description,
    }
    if _type == "event_source":
        template_filename = "event_source/tasks/task/task.py.jinja"
        inputs["event_source_name"] = name
    else:
        template_filename = "plugin/tasks/task/task.py.jinja"
    if not exists(output_file):
        create_file_from_template(
            template_filename=template_filename,
            inputs=inputs,
            output_filename=output_file,
        )


def create_task_schema(spec: PluginSpecTypes.Spec, task_name: str, task_dir_name: str):
    """
    Creates the schema.py for a plugin task.
    :param spec: The plugin spec dictionary
    :param task_name: The name of the current task
    :param task_dir_name: The absolute path to the icon_{plugin}/task/{task} directory
    :return:
    """
    output_file = os.path.join(task_dir_name, "schema.py")
    task_spec = spec.get(Constants.TASKS, {}).get(task_name, {})
    create_file_from_template(
        template_filename="plugin/tasks/task/schema.py.jinja",
        inputs={
            "base_module": BASE_MODULE,
            "task": task_name,
            "description": strip_newline(task_spec.get(Constants.DESCRIPTION, "")),
            "input": task_spec.get(Constants.INPUT, {}),
            "state": task_spec.get(Constants.STATE, {}),
            "output": task_spec.get(Constants.OUTPUT, {}),
            "spec": spec,
        },
        output_filename=output_file,
    )


def create_tasks(spec: PluginSpecTypes.Spec, tasks_dir_name: str, _type: str = "plugin"):
    """
    Creates the __init__.py for the plugin tasks directory and calls the functions
    to create the __init__.py, schema.py, and task.py for each task.
    :param spec: The plugin spec dictionary
    :param tasks_dir_name: The absolute path to the icon_{plugin}/tasks directory
    :param _type: The type of this plugin / event source
    :return:
    """
    logger = logging.getLogger("CreateUtil")
    logger.info("Writing tasks")
    create_directory(tasks_dir_name)

    create_tasks_init(spec.get(Constants.TASKS, {}).keys(), tasks_dir_name)
    plugin_name = spec.get(Constants.NAME, "")
    # Create subdirectories for each task under the tasks directory
    for task_name in spec.get(Constants.TASKS, {}):
        task_dir_name = os.path.join(tasks_dir_name, task_name)
        create_directory(task_dir_name)
        # Create __init__.py, task.py, and schema.py under each task directory
        create_task_init(task_name, task_dir_name)
        # Removes 'rk_' prefix to prevent errors when importing task from pre-converted plugin
        name = plugin_name.removeprefix("rk_") if _type == "event_source" else plugin_name
        create_task_py(
            task_name,
            spec.get(Constants.TASKS, {}).get(task_name, {}).get(Constants.DESCRIPTION, ""),
            task_dir_name,
            _type=_type,
            name=name,
        )
        create_task_schema(spec, task_name, task_dir_name)
    logger.info("Created tasks")


def create_unit_tests(spec: PluginSpecTypes.Spec, test_dir_name: str, prefix: str):
    """
    Creates the unit_test directory and
    creates the test_{action}.py for each action.
    :param spec: The plugin spec dictionary
    :param test_dir_name: The absolute path to the unit_test directory
    :param prefix: The prefix, either icon or komand
    :return:
    """
    create_directory(test_dir_name)

    # There is no __init__.py file under the unit_test directory
    for action_name in spec.get(Constants.ACTIONS, {}):
        output_file = os.path.join(test_dir_name, f"test_{action_name}.py")
        if not exists(output_file):
            create_file_from_template(
                template_filename="unit_test/test_action.py.jinja",
                inputs={
                    "plugin_dir_prefix": prefix,
                    "plugin_name": spec["name"],
                    "action_name": action_name,
                },
                output_filename=output_file,
            )


def create_unit_test_init(unit_test_dir_name: str):
    """
    Creates the __init__.py for the unit_test directory.
    :param unit_test_dir_name: The absolute path to the icon{plugin}/ directory
    :return:
    """
    output_file = os.path.join(unit_test_dir_name, "__init__.py")
    if not exists(output_file):
        create_file_from_template(
            template_filename="unit_test/__init__.py.jinja",
            inputs={},
            output_filename=output_file,
        )


def create_plugin_init(source_dir_name: str):
    """
    Creates the __init__.py for the icon{plugin}/plugin directory.
    :param source_dir_name: The absolute path to the icon{plugin}/plugin directory
    :return:
    """
    output_file = os.path.join(source_dir_name, "__init__.py")
    if not exists(output_file):
        create_file_from_template(
            template_filename="plugin/__init__.py.jinja",
            inputs={},
            output_filename=output_file,
        )


def get_prefix(spec: PluginSpecTypes.Spec, target_dir_name: str) -> str:
    """
    Method to detect the current prefix used in the directories of existing plugins
    :param spec: Spec file
    :param target_dir_name: Path to the target directory
    :return:
    """

    prefix = (
        BASE_PREFIX
        if os.path.isdir(os.path.join(target_dir_name, f'{BASE_PREFIX}_{spec.get(Constants.NAME, "")}'))
        else KOMAND_PREFIX
    )

    return prefix


def create_files_create(spec: PluginSpecTypes.Spec, dir_name: str, prefix: str, _type: str = "plugin"):
    """
    This handles all the other 'create_{file}' functions and merges them into one.
    :param spec: The plugin spec dictionary
    :param dir_name: The absolute path to the target
    :param prefix: The prefix, either icon or komand
    :param _type: The type of plugin, either 'plugin' or 'event_source' to determine file templates
    :return:
    """

    create_directory(dir_name)
    create_help_md(spec, dir_name)
    create_dockerfile(spec, dir_name, prefix)
    create_unit_tests(spec, os.path.join(dir_name, "unit_test"), prefix)
    create_unit_test_init(os.path.join(dir_name, "unit_test"))
    create_manifest(spec, os.path.join(dir_name, Constants.MANIFEST), prefix)
    create_setup_py(spec, dir_name, prefix)
    create_requirements_txt(dir_name, _type)
    create_makefile(dir_name)
    create_dockerignore(dir_name)
    source_dir_name = os.path.join(dir_name, f'{prefix}_{spec.get(Constants.NAME, "")}')
    create_directory(source_dir_name)
    create_plugin_init(source_dir_name)
    create_util(os.path.join(source_dir_name, "util"))
    create_connection(spec, os.path.join(source_dir_name, Constants.CONNECTIONS), _type)
    create_triggers(spec, os.path.join(source_dir_name, Constants.TRIGGERS))
    create_actions(spec, os.path.join(source_dir_name, Constants.ACTIONS))
    create_tasks(spec, os.path.join(source_dir_name, Constants.TASKS), _type)
    if _type == "event_source":
        copy_images(target_dir=dir_name, file_location="event_source")


def create_files_refresh(spec: PluginSpecTypes.Spec, dir_name: str, prefix: str, ignore: list):
    """
    This handles all the other 'create_{file}' functions and merges them into one.
    :param spec: The plugin spec dictionary
    :param dir_name: The absolute path to the target
    :param prefix: The prefix, either icon or komand
    :param ignore: List containing files to not overwrite/refresh
    :return:
    """

    # The only difference between create and refresh is that we need to create the root plugin directory
    # with create. In refresh, we re-create everything else within the existing plugin folder.

    if VALID_IGNORE_FILES[0] not in ignore:
        create_help_md(spec, dir_name)
    if VALID_IGNORE_FILES[1] not in ignore:
        create_dockerfile(spec, dir_name, prefix)
    if VALID_IGNORE_FILES[2] not in ignore:
        create_unit_tests(spec, os.path.join(dir_name, "unit_test"), prefix)
        create_unit_test_init(os.path.join(dir_name, "unit_test"))
    create_directory(dir_name)
    create_manifest(spec, os.path.join(dir_name, Constants.MANIFEST), prefix)
    create_setup_py(spec, dir_name, prefix)
    create_requirements_txt(dir_name)
    create_makefile(dir_name)
    create_dockerignore(dir_name)
    source_dir_name = os.path.join(dir_name, f'{prefix}_{spec.get(Constants.NAME, "")}')
    create_directory(source_dir_name)
    create_plugin_init(source_dir_name)
    create_util(os.path.join(source_dir_name, "util"))
    create_connection(spec, os.path.join(source_dir_name, Constants.CONNECTIONS))
    create_triggers(spec, os.path.join(source_dir_name, Constants.TRIGGERS))
    create_actions(spec, os.path.join(source_dir_name, Constants.ACTIONS))
    create_tasks(spec, os.path.join(source_dir_name, Constants.TASKS))

def handle_refresh_create(
    spec: PluginSpecTypes.Spec, target_dir_name: str, is_create: bool, ignore: list, _type: str = "plugin"
):
    """
    This function runs the create_files function based on whether the user is creating
    or refreshing
    :param spec: The plugin spec dictionary
    :param target_dir_name: The absolute path to the target directory
    :param is_create: Boolean value to indicate whether it is create or refresh
    :param ignore: optional string value specifying a file to not be overwritten when refreshing
    :param _type: type "plugin" or "event_source" determines file templates to use
    :return:
    """
    # Get the currently used prefix - This fixes issues related to komand_{plugin}
    prefix = get_prefix(spec, target_dir_name)

    # Establish directory name - By default we want it to be 'target_dir_name'
    dir_name = target_dir_name

    # In the event of create command, establish prefix as 'icon' and change directory name
    # to one level lower, e.g. base64 -> icon_base64
    if is_create:
        prefix = BASE_PREFIX
        dir_name = os.path.join(target_dir_name, spec.get(Constants.NAME, ""))
        create_files_create(spec=spec, dir_name=dir_name, prefix=prefix, _type=_type)
    else:
        create_files_refresh(spec=spec, dir_name=dir_name, prefix=prefix, ignore=ignore)
