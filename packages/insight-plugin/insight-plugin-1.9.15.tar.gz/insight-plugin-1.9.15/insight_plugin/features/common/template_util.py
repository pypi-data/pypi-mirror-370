import os
from re import sub
import json
from jinja2 import (
    Environment,
    FileSystemLoader,
    TemplateNotFound,
    TemplateSyntaxError,
    UndefinedError,
    select_autoescape,
)
from insight_plugin.features.common.plugin_spec_util import (
    PluginSpecTypes,
    PluginSpecConstants,
)
from insight_plugin.features.common.schema_util import SchemaUtil
from insight_plugin.features.common.exceptions import InsightException


class Templates:
    """
    Wrapper class around Jinja for filling in templates and generating JSON schemas.
    """

    def __init__(self, templates_path: str):
        templates_dir = os.path.abspath(templates_path)
        if not os.path.isdir(templates_dir):
            raise InsightException(
                message=f"The templates directory {templates_dir} was not found.",
                troubleshooting="Check that the directory exists on the filesystem, that it's"
                "a directory, that it's accessible, and that the provided path is correct.",
            )
        self._env = Environment(
            loader=FileSystemLoader(templates_dir),
            keep_trailing_newline=True,
            autoescape=select_autoescape(),
        )  # nosec
        # Add methods to the Jinja global environment, allowing us to call these methods in templates
        self._env.globals["camel_case"] = Templates.camel_case
        self._env.globals["upper_camel_case"] = Templates.upper_camel_case
        self._env.globals["json_schema_connection"] = self.json_schema_connection
        self._env.globals["json_schema_trigger_input"] = self.json_schema_trigger_input
        self._env.globals[
            "json_schema_trigger_output"
        ] = self.json_schema_trigger_output
        self._env.globals["json_schema_action_input"] = self.json_schema_action_input
        self._env.globals["json_schema_action_output"] = self.json_schema_action_output
        self._env.globals["json_schema_task_input"] = self.json_schema_task_input
        self._env.globals["json_schema_task_state"] = self.json_schema_task_state
        self._env.globals["json_schema_task_output"] = self.json_schema_task_output

    def fill(self, template_name: str, inputs: {str: str}) -> str:
        """
        Insert the mapped variables' strings into the template, get back the completed file as a string
        :param template_name: Path to the template under templates directory, ex. plugin/connection/connection.py.jinja
        :param inputs: Map where key = variables in the template, value = string to replace template variables with
        :return: String of filled-in complete template file
        """
        try:
            template_file = self._env.get_template(template_name)
            return template_file.render(inputs)
        except TemplateNotFound:
            raise InsightException(
                message=f"The template file {template_name} was not found.",
                troubleshooting="Check that the file exists on the filesystem, that it's accessible,"
                " and that the provided path is correct.",
            )
        except TemplateSyntaxError as error:
            raise InsightException(
                message=f"There was an error parsing the syntax of the template {template_name}.",
                troubleshooting=f"Check line #{error.lineno} for the following issue: {error.message}",
            )
        except UndefinedError as error:
            raise InsightException(
                message=f"There was an error while rendering the {template_name} template.",
                troubleshooting=f"Please check you have provided a valid type for your "
                f"inputs/outputs.\nPlease note that 'Null' is not an accepted type. Please omit"
                f" entirely if it is present.\nError: {error}",
            )

    @staticmethod
    def camel_case(s: str) -> str:
        """
        This function formats the string s into camel case, where the first word is lowercase, the first letter of
        each subsequent word is uppercase, and words have no delimiters between them.
        Source: https://www.educative.io/edpresso/how-do-you-convert-a-string-to-camelcase-format
        :param s: The input string to format into camel case
        :return: The result string formatted in camel case
        """
        # First, we convert any _ and - word delimiters to spaces. All words are now space-separated.
        # Then we use the Python method title() to capitalize the first letter of each word.
        # Then we use replace() to remove all spaces, concatenating all of the words together.
        s = sub(r"(_-)+", " ", s).title().replace(" ", "")
        # Here we make the very first letter lowercase, and rejoin it with the rest of the string.
        return "".join([s[0].lower(), s[1:]])

    @staticmethod
    def upper_camel_case(s: str) -> str:
        """
        This function formats the string s into upper camel case, where the first letter of
        each word is uppercase, and words have no delimiters between them.
        :param s: The input string to format into upper camel case
        :return: The result string formatted in upper camel case
        """
        # First, we find any capital letters and split the word before each capitalisation.
        # Then we check if the list we get is longer than one, meaning it was written in camel case.
        # If it was not in snake case we convert to upper camel case by capitalising the first word.
        # else: we convert any _ and - word delimiters to spaces. All words are now space-separated.
        # Then we use the Python method title() to capitalise the first letter of each word.
        # Then we use replace() to remove all spaces, concatenating all the words together.
        split_s = sub(r"([A-Z])", r" \1", s).split()
        if len(split_s) > 1:
            name = split_s.pop(0).title()
            for section in split_s:
                name += section
            return name
        else:
            return sub(r"(_|-)+", " ", s).title().replace(" ", "")

    def json_schema_connection(self, spec: PluginSpecTypes.Spec) -> str:
        """
        Generate a JSON schema for this plugin connection.
        :param spec: The plugin spec dictionary
        :return:
        """
        result = SchemaUtil.generate_json_schema(
            spec.get(PluginSpecConstants.CONNECTIONS), spec
        )
        return json.dumps(result, indent=2)

    def json_schema_trigger_input(
        self, spec: PluginSpecTypes.Spec, trigger_name: str
    ) -> str:
        """
        Generate a Json schema for the input of this plugin trigger.
        :param spec: The plugin spec_dictionary
        :param trigger_name: The name of the current trigger whose input to process
        :return:
        """
        result = SchemaUtil.generate_json_schema(
            spec.get(PluginSpecConstants.TRIGGERS)
            .get(trigger_name)
            .get(PluginSpecConstants.INPUT),
            spec,
        )
        return json.dumps(result, indent=2)

    def json_schema_trigger_output(
        self, spec: PluginSpecTypes.Spec, trigger_name: str
    ) -> str:
        """
        Generate a Json schema for the output of this plugin trigger.
        :param spec: The plugin spec_dictionary
        :param trigger_name: The name of the current trigger whose input to process
        :return:
        """
        result = SchemaUtil.generate_json_schema(
            spec.get(PluginSpecConstants.TRIGGERS)
            .get(trigger_name)
            .get(PluginSpecConstants.OUTPUT),
            spec,
        )
        return json.dumps(result, indent=2)

    def json_schema_action_input(
        self, spec: PluginSpecTypes.Spec, action_name: str
    ) -> str:
        """
        Generate a Json schema for the input of this plugin action.
        :param spec: The plugin spec_dictionary
        :param action_name: The name of the current action whose input to process
        :return:
        """
        result = SchemaUtil.generate_json_schema(
            spec.get(PluginSpecConstants.ACTIONS)
            .get(action_name)
            .get(PluginSpecConstants.INPUT),
            spec,
        )
        return json.dumps(result, indent=2)

    def json_schema_action_output(
        self, spec: PluginSpecTypes.Spec, action_name: str
    ) -> str:
        """
        Generate a Json schema for the output of this plugin action.
        :param spec: The plugin spec_dictionary
        :param action_name: The name of the current action whose input to process
        :return:
        """
        result = SchemaUtil.generate_json_schema(
            spec.get(PluginSpecConstants.ACTIONS)
            .get(action_name)
            .get(PluginSpecConstants.OUTPUT),
            spec,
        )
        return json.dumps(result, indent=2)

    def json_schema_task_input(self, spec: PluginSpecTypes.Spec, task_name: str) -> str:
        """
        Generate a Json schema for the input of this plugin task.
        :param spec: The plugin spec_dictionary
        :param task_name: The name of the current task whose input to process
        :return:
        """
        inputs = (
            spec.get(PluginSpecConstants.TASKS, {})
            .get(task_name, {})
            .get(PluginSpecConstants.INPUT, {})
        )
        result = SchemaUtil.generate_json_schema(inputs, spec)
        return json.dumps(result, indent=2)

    def json_schema_task_state(self, spec: PluginSpecTypes.Spec, task_name: str) -> str:
        """
        Generate a Json schema for the state of this plugin task.
        :param spec: The plugin spec_dictionary
        :param task_name: The name of the current task whose state to process
        :return:
        """
        result = SchemaUtil.generate_json_schema(
            spec.get(PluginSpecConstants.TASKS)
            .get(task_name)
            .get(PluginSpecConstants.STATE),
            spec,
        )
        return json.dumps(result, indent=2)

    def json_schema_task_output(
        self, spec: PluginSpecTypes.Spec, task_name: str
    ) -> str:
        """
        Generate a Json schema for the output of this plugin task.
        :param spec: The plugin spec_dictionary
        :param task_name: The name of the current task whose output to process
        :return:
        """
        result = SchemaUtil.generate_json_schema(
            spec.get(PluginSpecConstants.TASKS)
            .get(task_name)
            .get(PluginSpecConstants.OUTPUT),
            spec,
            task=True,
        )
        return json.dumps(result, indent=2)
