from typing import Union, Dict, Literal, Optional
from insight_plugin.features.samples.util.constants import SpecTypeDefaults
from insight_plugin.features.common.logging_util import BaseLoggingFeature
from insight_plugin.features.create import util
import os
import json
from insight_plugin.features.common.exceptions import InsightException
from insight_plugin.features.common.plugin_spec_util import (
    PluginSpecUtil,
    PluginSpecTypes,
    PluginSpecConstants,
)


class SamplesUtil(BaseLoggingFeature):
    def __init__(
        self,
        verbose: bool,
        target_dir: str,
        target_component: Optional[str],
    ):
        super().__init__(verbose=verbose)
        self.target_dir = target_dir
        self.target_component = target_component

    def run(self):
        """
        Main run function.
        :return:
        """
        self.create_samples()

    def create_samples(self):
        """
        Generate all the sample files based on the spec input.
        :return: Generated sample files.
        """
        self.logger.info("Starting Create Samples Sequence")

        # Get spec dict
        spec = PluginSpecUtil.get_spec_file(self.target_dir + "/plugin.spec.yaml")

        # Get list of triggers and actions
        triggers = list(spec.get(PluginSpecConstants.TRIGGERS, {}).keys())
        actions = list(spec.get(PluginSpecConstants.ACTIONS, {}).keys())
        tasks = list(spec.get(PluginSpecConstants.TASKS, {}).keys())

        # Create tests dir
        test_dir = self.create_tests_dir()

        # Create connection inputs
        connection_inputs = self.create_connection_inputs(spec=spec)

        # Create action, trigger & task samples multiple
        if not self.target_component:
            for trigger in triggers:
                self.logger.info(f"Creating sample for trigger: {trigger}")
                self.generate_sample(
                    spec=spec,
                    action_trigger_task_name=trigger,
                    connection=connection_inputs,
                    tests_dir=test_dir,
                    action_trigger_task="trigger",
                )
            for action in actions:
                self.logger.info(f"Creating sample for action: {action}")
                self.generate_sample(
                    spec=spec,
                    action_trigger_task_name=action,
                    connection=connection_inputs,
                    tests_dir=test_dir,
                    action_trigger_task="action",
                )
            for task in tasks:
                self.logger.info(f"Creating sample for task: {task}")
                self.generate_sample(
                    spec=spec,
                    action_trigger_task_name=task,
                    connection=connection_inputs,
                    tests_dir=test_dir,
                    action_trigger_task="task",
                )
        else:
            if self.target_component in triggers:
                self.logger.info(
                    f"Creating sample for trigger: {self.target_component}"
                )
                self.generate_sample(
                    spec=spec,
                    action_trigger_task_name=self.target_component,
                    connection=connection_inputs,
                    tests_dir=test_dir,
                    action_trigger_task="trigger",
                )
            elif self.target_component in actions:
                self.logger.info(f"Creating sample for action: {self.target_component}")
                self.generate_sample(
                    spec=spec,
                    action_trigger_task_name=self.target_component,
                    connection=connection_inputs,
                    tests_dir=test_dir,
                    action_trigger_task="action",
                )
            elif self.target_component in tasks:
                self.logger.info(f"Creating sample for task: {self.target_component}")
                self.generate_sample(
                    spec=spec,
                    action_trigger_task_name=self.target_component,
                    connection=connection_inputs,
                    tests_dir=test_dir,
                    action_trigger_task="task",
                )
            else:
                raise InsightException(
                    message=f"The target component {self.target_component} does not exist",
                    troubleshooting="Verify that the target component is correctly spelled "
                    "and defined in the spec",
                )

        self.logger.info("Create Samples process complete!")

    def create_tests_dir(self) -> str:
        """
        Create the tests directory and return the result to be used for other functions.
        :return: Path to new test directory.
        """

        # Verify that the target directory is real
        target_dir = os.path.abspath(self.target_dir)
        if not os.path.isdir(target_dir):
            raise InsightException(
                message=f"The target directory {target_dir} does not exist",
                troubleshooting="Verify that the target path is correct, accessible, and a directory",
            )

        # Create tests directory
        tests_dir = os.path.join(target_dir, "tests")
        util.create_directory(tests_dir)
        return tests_dir

    @staticmethod
    def create_connection_inputs(spec: dict) -> Dict[str, str]:
        """
        Create the connection inputs to be appended to the trigger or action sample.
        :param spec: Spec dictionary to read.
        :return: Connection inputs mapped to be placed in sample.
        """
        connection_all = spec.get("connection")
        connection_inputs = {}
        if connection_all:
            for aspect in connection_all:
                connection_inputs[aspect] = SamplesUtil.detect_default_value(
                    connection_all[aspect]
                )
        if not connection_inputs:
            connection_inputs = None
        return connection_inputs

    def generate_sample(  # pylint: disable=too-many-positional-arguments
        self,
        spec: PluginSpecTypes.Spec,
        action_trigger_task_name: str,
        connection: Dict[str, str],
        tests_dir: str,
        action_trigger_task: Literal["action", "trigger", "task"],
    ):
        """
        Create and generate a sample file.
        :param spec: Spec dictionary to read actions and triggers.
        :param action_trigger_task_name: Name of the action or trigger to generate a sample for.
        :param connection: Our connection inputs to add to the sample file.
        :param tests_dir: Path to the 'tests/' directory.
        :param action_trigger_task: Literal to differentiate functionality between action, trigger & task generation.
        :return: Generated sample file.
        """
        filename = self.create_filename(tests_dir, action_trigger_task_name)

        if action_trigger_task == "action":
            input_all = (
                spec.get(PluginSpecConstants.ACTIONS)
                .get(action_trigger_task_name)
                .get("input")
            )
        elif action_trigger_task == "trigger":
            input_all = (
                spec.get(PluginSpecConstants.TRIGGERS)
                .get(action_trigger_task_name)
                .get("input")
            )
        else:
            input_all = (
                spec.get(PluginSpecConstants.TASKS)
                .get(action_trigger_task_name)
                .get("input")
            )

        inputs = {}
        if input_all:
            for aspect in input_all:
                inputs[aspect] = self.detect_default_value(input_all[aspect])
        if not inputs:
            inputs = None

        action_sample = self.generate_json_body(
            action_trigger_task=action_trigger_task,
            action_trigger_task_name=action_trigger_task_name,
            connection=connection,
            inputs=inputs,
        )

        if os.path.exists(filename):
            self.logger.warning(
                f"tests/{action_trigger_task_name}.json already exists, overwriting.."
            )

        try:
            with open(filename, "w+", encoding="utf-8") as file:
                json.dump(action_sample, file, indent=2)
        except FileNotFoundError as error:
            self.logger.debug(error)
            raise InsightException(
                message=f"File could not be written for {filename}",
                troubleshooting=f"Check {filename} action/trigger exists in plugin spec",
            )

    @staticmethod
    def create_filename(tests_dir: str, action_trigger_name: str) -> str:
        """
        Create the filename for the json test file based on the action or trigger name
        :param tests_dir: Name of the test directory, {icon_plugin}/tests
        :param action_trigger_name: Name of the action or trigger
        :return: String file path, {icon__plugin}/tests/{action/trigger}.json
        """
        filename = tests_dir + "/" + action_trigger_name + ".json"
        return filename

    @staticmethod
    def detect_default_value(dict_value: Union[dict, str]):
        """
        Function to determine the type or default value from the plugin spec
        to be inserted into the generated sample.
        :param dict_value:
        :return:
        """
        schema_default = dict_value.get("default")
        schema_type = dict_value.get("type")
        default_value = {}

        # Use default first
        if schema_default:
            default_value = schema_default

        # Handle arrays specifically because they can vary e.g. '[]integer', '[]string', '[]customType'
        elif "[]" in schema_type:
            default_value = []

        # Else assign default based on type
        else:
            for key, value in SpecTypeDefaults.TYPE_DEFAULTS.items():
                if schema_type == key:
                    default_value = value

        return default_value

    @staticmethod
    def generate_json_body(
        action_trigger_task: Literal["action", "trigger", "task"],
        action_trigger_task_name: str,
        connection: Dict[str, str],
        inputs: Dict[str, any],
    ) -> dict:
        """
        Factory function to generate the sample based on whether it is a trigger or action, and whether connection exists
        or not
        :param action_trigger_task: Literal to indicate whether it is an action, trigger or task
        :param action_trigger_task_name: The name of the action, trigger or task
        :param connection: Dictionary containing connection inputs
        :param inputs: Inputs for action or trigger
        :return: A dictionary containing all the information needed for generating the sample.
        """
        sample = {}
        if action_trigger_task == "action":
            sample = {
                "body": {
                    "action": action_trigger_task_name,
                    "connection": connection,
                    "input": inputs,
                    "meta": {},
                },
                "type": "action_start",
                "version": "v1",
            }

        elif action_trigger_task == "trigger":
            sample = {
                "body": {
                    "connection": connection,
                    "dispatcher": {"url": "http://localhost:8000", "webhook_url": ""},
                    "input": inputs,
                    "meta": {},
                    "trigger": action_trigger_task_name,
                },
                "type": "trigger_start",
                "version": "v1",
            }
        elif action_trigger_task == "task":
            sample = {
                "body": {
                    "connection": connection,
                    "input": inputs,
                    "state": {},
                    "meta": {},
                    "task": action_trigger_task_name,
                },
                "type": "task_start",
                "version": "v1",
            }
        return sample
