import tempfile
import unittest
from filecmp import cmp
from typing import List
import sys
import os

sys.path.append(os.path.abspath("../"))
from insight_plugin.features.common.plugin_spec_util import PluginSpecConstants
from insight_plugin.features.create.controller import CreateController
from tests import TEST_RESOURCES


# Test to ensure the order in which things are written in the spec does not adversely affect the help.md
class SpecOrderTest(unittest.TestCase):
    def test_jira(self):
        mismatches = SpecOrderTestUtil.test_order("spec_order_test", "jira")
        if mismatches:
            for mismatch in mismatches:
                print(mismatch)
            self.fail()


class SpecOrderTestUtil:
    @staticmethod
    def test_order(
        plugin_dir: str, plugin_name: str, target_dir: str = None
    ) -> List[str]:
        # Examples of correctly created plugins exist under the tests/resources path
        test_dir = os.path.join(TEST_RESOURCES, plugin_dir)
        # This is the plugin.spec.yaml that is adjacent to the generated plugin directory, not inside the plugin dir
        spec_file_path = os.path.join(test_dir, PluginSpecConstants.FILENAME)
        # We create a temporary directory for the resulting content created by the test subject
        with tempfile.TemporaryDirectory() as temp_dir:
            create_feature = CreateController.new_from_cli(
                spec_path=spec_file_path, verbose=True, target_dir=temp_dir
            )

            create_feature.create()
            expect_dir = os.path.join(test_dir, plugin_name)
            result_dir = os.path.join(
                target_dir if target_dir is not None else temp_dir, plugin_name
            )

            expect_file = os.path.join(expect_dir, "help.md")
            result_file = os.path.join(result_dir, "help.md")
            mismatches = []
            if not cmp(expect_file, result_file):
                mismatches.append(f"{result_file} does not match expected content.")
            return mismatches
