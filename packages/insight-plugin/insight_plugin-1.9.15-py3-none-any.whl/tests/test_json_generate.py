import os
import shutil
import unittest
import sys

sys.path.append(os.path.abspath("../"))
from insight_plugin.features.common.exceptions import InsightException
from insight_plugin.features.create.json_generation_util import TestFileCreator
from tests import TEST_RESOURCES


class TestJsonGenerate(unittest.TestCase):
    TEST_JSON_GENERATE_DIR = f"{TEST_RESOURCES}/create_json_tests/"

    @staticmethod
    def get_dir(dir_in):
        return os.path.join(TestJsonGenerate.TEST_JSON_GENERATE_DIR, dir_in)

    def test_json_create_one_action(self):
        specific_dir = "json_generate_r7_metasploit"
        specific_action = "search_for_exploit"

        test_creator = TestFileCreator.new_from_cli(
            TestJsonGenerate.get_dir(specific_dir)
        )
        test_creator.create_test_files(specific_action)
        resultant_path = TestJsonGenerate.get_dir(
            f"{specific_dir}/tests/{specific_action}.json"
        )

        # Test and cleanup
        self.assertTrue(os.path.exists(resultant_path))
        shutil.rmtree(os.path.dirname(resultant_path))

    def test_json_create_one_task(self):
        specific_dir = "json_generate_w_task"
        specific_task = "monitor_incident_events"

        test_creator = TestFileCreator.new_from_cli(
            TestJsonGenerate.get_dir(specific_dir)
        )
        test_creator.create_test_files(specific_task)
        resultant_path = TestJsonGenerate.get_dir(
            f"{specific_dir}/tests/{specific_task}.json"
        )

        # Test and cleanup
        self.assertTrue(os.path.exists(resultant_path))
        shutil.rmtree(os.path.dirname(resultant_path))

    def test_json_create_all(self):
        specific_dir = "json_generate_r7_metasploit"
        names = ["search_for_exploit", "new_modules", "execute_exploit"]

        test_creator = TestFileCreator.new_from_cli(
            TestJsonGenerate.get_dir(specific_dir)
        )
        test_creator.create_test_files()
        resultant_path = TestJsonGenerate.get_dir(f"{specific_dir}/tests/")

        # Test and then cleanup
        for name in names:
            self.assertTrue(os.path.exists(f"{resultant_path}{name}.json"))
        shutil.rmtree(resultant_path)

    def test_type_templating_should_pass(self):
        test_creator = TestFileCreator.new_from_cli(
            TestJsonGenerate.get_dir("json_type_cases_good")
        )
        # base type
        self.assertEqual(test_creator.get_type_template("string", []), "")
        # base type with dict
        self.assertEqual(
            test_creator.get_type_template("credential_username_password", []),
            {"username": "", "password": ""},
        )
        # list of base type
        self.assertEqual(test_creator.get_type_template("[]string", []), [""])
        # list of custom type
        self.assertEqual(
            test_creator.get_type_template("[]simple_custom_type", []),
            [{"Simple1": "", "Simple2": 0.0}],
        )
        # custom type in the spec (top level)
        self.assertEqual(
            test_creator.get_type_template("simple_custom_type", []),
            {"Simple1": "", "Simple2": 0.0},
        )
        # nested custom type (custom type referring to another custom type)
        self.assertEqual(
            test_creator.get_type_template("nested_custom_type", []),
            {"Nested Type": {"Simple1": "", "Simple2": 0.0}, "SimpleInCustom": ""},
        )

        self.assertEqual(
            test_creator.get_type_template("circ_depend_1", []),
            {"DependOn2": {"DependOn1": {}, "Normal2": ""}, "Normal": ""},
        )

    def test_type_templating_should_fail(self):
        test_creator = TestFileCreator.new_from_cli(
            TestJsonGenerate.get_dir("json_type_cases_bad")
        )

        # type does not exist in custom types and is not a base type
        with self.assertRaises(InsightException):
            test_creator.get_type_template("non_existent_type", [])
        # list of a nonexistent type
        with self.assertRaises(InsightException):
            test_creator.get_type_template("[]non_existent_type", [])

        # As far as I can tell nothing else should really fail
