import json
import os
from insight_plugin.features.common.plugin_spec_util import (
    PluginSpecUtil,
    PluginSpecConstants,
    PluginSpecUtilModes,
)
from insight_plugin.features.common.exceptions import InsightException
from insight_plugin.features.common.temp_file_util import SafeTempDirectory
from insight_plugin.features.common.logging_util import BaseLoggingFeature
from enum import Enum


class BaseTypes:
    """
    Based on the "Base Types" section available at https://docs.rapid7.com/insightconnect/plugin-spec/
    """

    base_types = {
        "boolean": "true",
        "bool": "true",  # not technically in the spec but in here for compatability?
        "integer": 0,
        "number": 0,  # again not technically in the spec but compatability
        "int": 0,
        "float": 0.0,
        "string": "",
        "date": "",
        "bytes": "",
        "object": {},
        "file": {"filename": "string", "content": "bytes"},
        "password": "",
        "python": "",
        "credential_username_password": {"username": "", "password": ""},
        "credential_asymmetric_key": {"key": ""},
        "credential_secret_key": {"secretKey": ""},
        "credential_token": {"token": "", "domain": ""},
    }


class JSONFormatting:
    INDENT = 2


class SECTION(Enum):
    # Wrapper so we can make this an enum, each section is one of these types
    ACTIONS = PluginSpecConstants.ACTIONS
    TRIGGERS = PluginSpecConstants.TRIGGERS
    CONNECTION = PluginSpecConstants.CONNECTIONS
    TASK = PluginSpecConstants.TASKS


class JSONInstruction:
    """
    Holder class for writing instructions
    """

    def __init__(self, filename: str, json_object: dict):
        self.filename = filename
        self.json_object = json_object


class JsonGenerator:
    """
    Class to generate the JSON test files based on a JSON object passed in
    """

    def __init__(self, json_obj: dict):
        self.json_obj = json_obj

    def generate_json(self) -> str:
        """
        :return: JSON string representation of JSON object
        """
        return json.dumps(
            self.json_obj, indent=JSONFormatting.INDENT, sort_keys=True, default=str
        )


class JsonWriter(BaseLoggingFeature):
    """
    Class for writing JSON test files based on JSON objects passed in
    """

    def __init__(
        self,
        instructions: [JSONInstruction],
        target_dir_name: str = None,
        tmpdirname: str = None,
    ):
        """
        Instructions must be a dict of filenames and corresponding json objects to write to each file
        ex: {'tests/encode.json': ({'description': ...}, 'action'
        :param instructions:
        """
        super().__init__()
        self.instructions = instructions
        self.tmp_dir_name = tmpdirname
        self.target_dir_name = target_dir_name

    def write(self, overwrite: bool = False):
        """
        :param overwrite: determines if existing files be overwritten with new json data
        :return: None
        """
        temp_dir_tests_folder = ""
        if self.tmp_dir_name:
            temp_dir_tests_folder = os.path.join(
                self.tmp_dir_name, TestFileCreator.TEST_FILE_DIR
            )
            os.mkdir(temp_dir_tests_folder)

        for instruction in self.instructions:
            final_file_dest = os.path.join(self.target_dir_name, instruction.filename)
            if self.tmp_dir_name:
                instruction.filename = os.path.join(
                    temp_dir_tests_folder, instruction.filename
                )
            else:
                instruction.filename = os.path.join(
                    self.target_dir_name, instruction.filename
                )
            if os.path.exists(final_file_dest):
                if overwrite:
                    self.logger.debug(
                        f"Overwrite set, overwriting at {final_file_dest}"
                    )
                else:
                    self.logger.debug(
                        f"Overwrite not set, skipping {instruction.filename}"
                    )
                    continue
            JsonWriter.write_file(instruction.json_object, instruction.filename)

    @staticmethod
    def write_file(json_object: dict, filename: str):
        try:
            with open(filename, "wt", encoding="utf-8") as fp:
                json_gen = JsonGenerator(json_object)
                fp.write(json_gen.generate_json())
        except OSError:
            raise InsightException(
                message=f"Could not create test file {filename}.",
                troubleshooting="Check permissions to write to this directory",
            )


class TestFileCreator:
    """
    Create json test files in the proper directories
    """

    TEST_FILE_DIR = "tests/"

    def __init__(self, spec: dict, filepath: str):
        """
        :param spec: spec dictionary of the plugin
        :param filepath: filepath of the plugin directory
        """
        self.spec = spec
        self.filepath = filepath
        self._connection = None

    @classmethod
    def new_from_cli(cls, filepath: str = None):
        spec_util = PluginSpecUtil(PluginSpecUtilModes.SPECFILE)
        if filepath:
            spec_util.load(**{PluginSpecConstants.FILEPATH: filepath})
        else:
            filepath = "."
            spec_util.load()
        return cls(spec_util.spec_dictionary, filepath)

    def create_test_files(
        self, specific_test_file: str = None, overwrite: bool = False
    ):
        """
        Create the test file(s), all the test files
        :param specific_test_file: a specific action/trigger is specified when command to gen test files is used
        :param overwrite: true if existing test files be overwritten
        :return: None
        """
        filepath_test_dir = os.path.join(self.filepath, TestFileCreator.TEST_FILE_DIR)
        SafeTempDirectory.execute_safe_dir(
            self._safe_create_test_files,
            self.filepath,
            overwrite,
            filepath_test_dir,
            specific_test_file,
            overwrite,
        )

    def _safe_create_test_files(
        self,
        tmpdirname: str,
        target_dir_name: str,
        specific_test_file: str = None,
        overwrite: bool = False,
    ) -> None:
        instructions = self.generate_instructions(
            self.spec.get(PluginSpecConstants.ACTIONS),
            self.spec.get(PluginSpecConstants.TRIGGERS),
            self.spec.get(PluginSpecConstants.TASKS),
            specific_test_file,
        )
        # Fill in the spec sections as needed
        json_writer = JsonWriter(instructions, target_dir_name, tmpdirname)
        json_writer.write(overwrite)

    def generate_instructions(
        self, actions: dict, triggers: dict, tasks: dict, specific_test_file: str
    ) -> [JSONInstruction]:
        """
        Generate the instructions to write the test files
        :param actions: actions for the plugin
        :param triggers: triggers for the plugin
        :param specific_test_file: a specific action/trigger to test
        :param filepath: filepath to write the test files to
        :return:
        """
        instructions = []
        if actions is not None:
            self.iterate_and_generate_instruction(
                specific_test_file, actions, SECTION.ACTIONS, instructions
            )
        if triggers is not None:
            self.iterate_and_generate_instruction(
                specific_test_file, triggers, SECTION.TRIGGERS, instructions
            )

        if tasks is not None:
            self.iterate_and_generate_instruction(
                specific_test_file, tasks, SECTION.TASK, instructions
            )

        if len(instructions) == 0:
            if specific_test_file:
                raise InsightException(
                    message=f"{specific_test_file} not found",
                    troubleshooting=f"Ensure {specific_test_file} is in the plugin.spec.yaml file.",
                )
            raise InsightException(
                message="No tests to generate",
                troubleshooting="Add items to the plugin.spec.yaml file that require tests:"
                "actions, triggers, or tasks.",
            )

        return instructions

    def iterate_and_generate_instruction(
        self,
        specific_test_file: str,
        dictionary: dict,
        dictionary_type: SECTION,
        instructions: [JSONInstruction],
    ) -> None:
        """
        Fill the instructions parameter with any needed instructions for JSON generation
        :param specific_test_file: if we are looking for a specific action/trigger
        :param filepath: filepath to append our more specific *.json to
        :param dictionary: section of the plugin spec
        :param dictionary_type: type of section we are looking at in the plugin spec
        :param instructions: list to add any generated instructions to
        :return: None
        """
        if specific_test_file:
            # locate the specific action or trigger in the spec
            for key, val in dictionary.items():
                if specific_test_file == key:
                    file_name = f"{key}.json"
                    instructions.append(
                        JSONInstruction(
                            file_name, self.make_json(key, val, dictionary_type)
                        )
                    )
                    break
        else:
            # if not specific .json file, just iterate over all of them!
            for key, val in dictionary.items():
                file_name = f"{key}.json"
                instructions.append(
                    JSONInstruction(
                        file_name, self.make_json(key, val, dictionary_type)
                    )
                )

    def make_json(self, key: str, val: dict, dict_type: SECTION) -> dict:
        """
        Given an action/trigger input, fill in json info
        :param key: action/trigger name
        :param val: The individual section of the spec (action, trigger)
        :param dict_type: Type of section this is
        :return: dictionary with the initial dict entry for this object including: input, [action|trigger], meta
        """
        # This method is very convention specific. Lots of handcoded values...
        json_obj_body = {}
        json_obj = {"body": json_obj_body}

        json_obj_body["meta"] = {}
        if "input" in val:
            json_obj_body["input"] = self.fill_fields(val["input"])
        else:
            json_obj_body["input"] = {}
        if dict_type == SECTION.ACTIONS:
            json_obj_body["action"] = key
            json_obj["type"] = "action_start"
        elif dict_type == SECTION.TRIGGERS:
            json_obj_body["trigger"] = key
            json_obj_body["dispatcher"] = {
                "url": "http://localhost:8000",
                "webhook_url": "",
            }
            json_obj["type"] = "trigger_start"
        elif dict_type == SECTION.TASK:
            json_obj_body["task"] = key
            json_obj_body["state"] = {"last_event_time": ""}
            json_obj["type"] = "task_start"

        json_obj["version"] = "v1"
        json_obj_body["connection"] = self.get_connection()
        return json_obj

    def fill_fields(self, section: dict) -> dict:
        """
        Fill in fields for the test file according to their types (and possible "defaults" in the spec)
        :param section: input section from the spec to turn into test input
        :return: modified input
        """
        for field in section:
            # if there is a default value, put it in
            if PluginSpecConstants.DEFAULT in section[field]:
                section[field] = section[field][PluginSpecConstants.DEFAULT]

            elif (
                PluginSpecConstants.ENUM in section[field]
                and len(section[field][PluginSpecConstants.ENUM]) > 0
            ):
                section[field] = section[field][PluginSpecConstants.ENUM][0]

            # if there is no default/enum value, check for "type" next. If no type for this field, raise an exception
            elif PluginSpecConstants.TYPE not in section[field]:
                raise InsightException(
                    message=f"No type specified for the {section} field.",
                    troubleshooting=f"Please fill in the type for the {section} field in the plugin.spec.yaml file.",
                )
            else:
                # fill in with the proper type template
                section[field] = self.get_type_template(
                    section[field][PluginSpecConstants.TYPE], []
                )
        return section

    def get_type_template(self, type_in: str, prev_types_discovered: [str]):
        """
        Get the template for this field based on the type_in parameter
        :param type_in: type coming in that we want the blank template for
        :param prev_types_discovered: list of types we have seen to prevent circular dependencies
        :return: full template of base or complex type passed in
        """
        # case 1: this is a custom type we have already seen/discovered in this traversal. Only want empty object now
        if type_in in prev_types_discovered:
            return {}
        # case 2: newly seen (in this traversal) custom type. Use title : get_type_template() for each type listed
        elif type_in in self.spec[PluginSpecConstants.TYPES]:
            # use the title as the key and recurse on the value
            type_info = self.spec[PluginSpecConstants.TYPES][type_in]
            template = {}
            for _, subtype in type_info.items():
                try:
                    type_title = subtype[PluginSpecConstants.TITLE]
                    type_inner_type = subtype[PluginSpecConstants.TYPE]
                except KeyError:
                    raise InsightException(
                        message=f"Type '{subtype}' must have both title and type as fields.",
                        troubleshooting=f"Add title and type to '{subtype}' type.",
                    )
                prev_types_discovered.append(type_in)
                template[type_title] = self.get_type_template(
                    type_inner_type, prev_types_discovered
                )
            return template
        # case 3: a base type. Use the lookup table
        elif type_in in BaseTypes.base_types:
            return BaseTypes.base_types[type_in]
        # case 4: a list of some other type. strip off the first 2 chars ([]) and wrap next call to get_type in a list
        elif len(type_in) >= 2 and type_in[0:2] == "[]":
            return [self.get_type_template(type_in[2:], prev_types_discovered)]
        # else this type does not exist as far as we can tell. Throw exception
        else:
            raise InsightException(
                message=f"Type '{type_in}' not found in the plugin.spec.yaml file and is not a base type.",
                troubleshooting="See https://docs.rapid7.com/insightconnect/plugin-spec/#base-types"
                " or add this type to the types section in the plugin.spec.yaml file.",
            )

    def get_connection(self) -> dict:
        if self._connection is None:
            # generate the connection section if it does not exist yet
            connection_spec = self.spec.get(PluginSpecConstants.CONNECTIONS)
            # if there is no spec, this may have been called by mistake, but maybe not, so its safest to just ret empty
            if connection_spec is None:
                return {}
            self._connection = self.fill_fields(connection_spec)
        return self._connection
