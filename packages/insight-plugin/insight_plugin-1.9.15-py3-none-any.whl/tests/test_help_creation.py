import hashlib
import unittest
import sys
import os

sys.path.append(os.path.abspath("../"))

from insight_plugin.features.common.plugin_spec_util import (
    PluginSpecConstants,
    PluginSpecUtil,
    PluginSpecUtilModes,
)
from insight_plugin.features.create.plugin_to_helpmd import ConvertPluginToHelp
from tests import TEST_RESOURCES


class TestHelpCreation(unittest.TestCase):
    def test_jira_help_v2(self):
        filepath = f"{TEST_RESOURCES}/help_creation_tests/test_jira_v2"
        self.help_wrapper(filepath)

    def test_jira_help_v3(self):
        filepath = f"{TEST_RESOURCES}/help_creation_tests/test_jira_v3"
        self.help_wrapper(filepath)

    def test_insight_vm_help(self):
        filepath = f"{TEST_RESOURCES}/help_creation_tests/insight_vm_v2"
        self.help_wrapper(filepath)

    def test_custom_recursive_spec(self):
        filepath = f"{TEST_RESOURCES}/help_creation_tests/custom_recursive_spec"
        self.help_wrapper(filepath)

    def test_lists_key_features_changelog(self):
        # test to verify that the add list feature still works on a spec
        # namely the two new features, key features and changelog
        filepath = f"{TEST_RESOURCES}/help_creation_tests/key_features_changelog"
        self.help_wrapper(filepath)

    def test_complete_help_gen_v2(self):
        # Test to attempt to verify if the help.md generation has changed in a way that will break validators
        # will compare a currently generated hash to a previously generated files hash and if they are different, fail
        filepath = f"{TEST_RESOURCES}/help_creation_tests/custom_everything_spec_v2"
        # self.help_wrapper(filepath)
        self.help_wrapper_hash_check(filepath)
        """
        coverage in this test:
        v2 connection version
        adding connection, components, types
        adding all basic sections with blank types as needed
        """

    def test_complete_help_gen_v3(self):
        # Test to attempt to verify if the help.md generation has changed in a way that will break validators
        # will compare a currently generated hash to a previously generated files hash and if they are different, fail
        filepath = f"{TEST_RESOURCES}/help_creation_tests/custom_everything_spec_v3"
        self.help_wrapper_hash_check(filepath)
        """
        coverage in this test:
        connection troubleshooting
        component troubleshooting
        component "help"
        connection fields nested inside "input"
        all non-custom type fields have examples
        version history
        changelog
        references
        """

    def help_wrapper(self, filepath):
        spec = PluginSpecUtil(PluginSpecUtilModes.SPECFILE)
        spec.load(**{PluginSpecConstants.FILEPATH: filepath})
        plugin_help = ConvertPluginToHelp.new_for_markdown(
            spec.spec_dictionary, filepath
        )
        plugin_help.convert_function()
        path_check = os.path.join(filepath, "help.md")
        self.assertTrue(os.path.exists(path_check))
        os.remove(path_check)

    def help_wrapper_hash_check(self, filepath):
        spec = PluginSpecUtil(PluginSpecUtilModes.SPECFILE)
        spec.load(**{PluginSpecConstants.FILEPATH: filepath})
        plugin_help = ConvertPluginToHelp.new_for_markdown(
            spec.spec_dictionary, filepath
        )
        plugin_help.convert_function()

        path_check = os.path.join(filepath, "help.md")
        regression_test_help = os.path.join(filepath, "help.check.md")
        self.assertTrue(os.path.exists(path_check))
        self.assertTrue(os.path.exists(regression_test_help))

        test_hash = self.get_bytes_helper(path_check)
        our_hash = self.get_bytes_helper(regression_test_help)
        self.assertEqual(our_hash, test_hash)
        os.remove(path_check)

    @staticmethod
    def get_bytes_helper(filename):
        # get the md5 of a file
        with open(filename, "rb") as f:
            file_bytes = f.read()
            file_hash = hashlib.md5(file_bytes).hexdigest()
            return file_hash
