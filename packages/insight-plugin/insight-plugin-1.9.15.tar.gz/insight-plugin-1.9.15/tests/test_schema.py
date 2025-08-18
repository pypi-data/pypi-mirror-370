import os
import unittest
from typing import Dict, Optional
import sys

sys.path.append(os.path.abspath("../"))
import jsonschema
from jsonschema.exceptions import SchemaError, ValidationError

from insight_plugin.features.common.plugin_spec_util import (
    PluginSpecConstants,
    PluginSpecUtil,
)
from insight_plugin.features.common.schema_util import SchemaUtil
from tests import TEST_RESOURCES
from tests.resources.schema_tests.json_schema_instances import *


class TestSchema(unittest.TestCase):
    @staticmethod
    def validate(json_schema: Dict, json_instance: Dict) -> Optional[str]:
        """Returns None if successful, and the error message if failed."""
        try:
            jsonschema.validate(instance=json_instance, schema=json_schema)
            return None
        except SchemaError as error:
            return str(error)
        except ValidationError as error:
            return str(error)

    @staticmethod
    def get_schema(
        plugin_dir_name: str, section_name: str, component_name: str, in_or_out: str
    ) -> Dict:
        plugin_dir = os.path.join(TEST_RESOURCES, plugin_dir_name)
        plugin_spec_filename = os.path.join(plugin_dir, PluginSpecConstants.FILENAME)
        plugin_spec = PluginSpecUtil.get_spec_file(plugin_spec_filename)
        section_spec = plugin_spec.get(section_name).get(component_name).get(in_or_out)
        return SchemaUtil.generate_json_schema(section_spec, plugin_spec)

    def test_base64_action_decode_input(self):
        result = TestSchema.get_schema(
            "export_test_base64",
            PluginSpecConstants.ACTIONS,
            "decode",
            PluginSpecConstants.INPUT,
        )
        self.assertIsNone(TestSchema.validate(result, BASE64_DECODE_INPUT_INSTANCE))

    def test_base64_action_decode_output(self):
        result = TestSchema.get_schema(
            "export_test_base64",
            PluginSpecConstants.ACTIONS,
            "decode",
            PluginSpecConstants.OUTPUT,
        )
        self.assertIsNone(TestSchema.validate(result, BASE64_DECODE_OUTPUT_INSTANCE))

    def test_jira_action_create_issue_input(self):
        result = TestSchema.get_schema(
            "test_jira/jira",
            PluginSpecConstants.ACTIONS,
            "create_issue",
            PluginSpecConstants.INPUT,
        )
        self.assertIsNone(
            TestSchema.validate(result, JIRA_ACTION_CREATE_ISSUE_INPUT_INSTANCE)
        )

    def test_jira_action_create_issue_output(self):
        result = TestSchema.get_schema(
            "test_jira/jira",
            PluginSpecConstants.ACTIONS,
            "create_issue",
            PluginSpecConstants.OUTPUT,
        )
        self.assertIsNone(
            TestSchema.validate(result, JIRA_ACTION_CREATE_ISSUE_OUTPUT_INSTANCE)
        )

    def test_jira_action_get_issue_input(self):
        result = TestSchema.get_schema(
            "test_jira/jira",
            PluginSpecConstants.ACTIONS,
            "get_issue",
            PluginSpecConstants.INPUT,
        )
        self.assertIsNone(
            TestSchema.validate(result, JIRA_ACTION_GET_ISSUE_INPUT_INSTANCE)
        )

    def test_jira_action_get_issue_output(self):
        result = TestSchema.get_schema(
            "test_jira/jira",
            PluginSpecConstants.ACTIONS,
            "get_issue",
            PluginSpecConstants.OUTPUT,
        )
        self.assertIsNone(
            TestSchema.validate(result, JIRA_ACTION_GET_ISSUE_OUTPUT_INSTANCE)
        )

    def test_carbon_black_action_get_details_for_specific_event_output(self):
        result = TestSchema.get_schema(
            "test_carbon_black/carbon_black_defense",
            PluginSpecConstants.ACTIONS,
            "get_details_for_specific_event",
            PluginSpecConstants.OUTPUT,
        )
        self.assertIsNone(
            TestSchema.validate(
                result,
                CARBON_BLACK_ACTION_GET_DETAILS_FOR_SPECIFIC_EVENT_OUTPUT_INSTANCE,
            )
        )

    def test_carbon_black_action_find_event_output(self):
        result = TestSchema.get_schema(
            "test_carbon_black/carbon_black_defense",
            PluginSpecConstants.ACTIONS,
            "find_event",
            PluginSpecConstants.OUTPUT,
        )
        self.assertIsNone(
            TestSchema.validate(result, CARBON_BLACK_ACTION_FIND_EVENT_OUTPUT_INSTANCE)
        )
