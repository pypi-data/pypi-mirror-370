import tempfile
import unittest
import shutil
import sys
import os
from filecmp import cmp

from parameterized import parameterized
from typing import List
from insight_plugin.features.common.plugin_spec_util import PluginSpecConstants

sys.path.append(os.path.abspath("../"))
from insight_plugin.features.common.exceptions import InsightException
from insight_plugin.features.refresh.controller import RefreshController
from insight_plugin.features.create.controller import CreateController
from tests import TEST_RESOURCES

spec = os.path.join(TEST_RESOURCES, "test_base64/plugin.spec.yaml")
base64_plugin = os.path.join(TEST_RESOURCES, "test_base64/base64")
ignore = ""


class TestRefresh(unittest.TestCase):
    def test_refresh(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            shutil.copy(spec, temp_dir)

            refresh_controller = RefreshController.new_from_cli(
                verbose=False,
                target_dir=temp_dir,
                spec_path=base64_plugin,
                ignore=ignore,
            )

            refresh_controller.refresh()

    def test_spec_to_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            shutil.copy(spec, temp_dir)

            refresh_controller = RefreshController.new_from_cli(
                verbose=False, target_dir=temp_dir, spec_path=spec, ignore=ignore
            )
            refresh_controller.spec_to_file(spec, temp_dir)

    def test_non_directory(self):
        with self.assertRaises(InsightException) as context:
            RefreshController.new_from_cli(
                verbose=False,
                target_dir="thisdirectorydoesntexist",
                spec_path=spec,
                ignore=ignore,
            )
        self.assertEqual(
            context.exception.troubleshooting,
            "Verify that the target path is correct, accessible, and a directory",
        )

    def test_refresh_carbon_black(self):
        mismatches = TestRefreshUtil.test_refresh(
            "test_carbon_black", "carbon_black_defense", ignore
        )
        if mismatches:
            for mismatch in mismatches:
                print(mismatch)
            self.fail()

    def test_refresh_jira(self):
        mismatches = TestRefreshUtil.test_refresh("test_jira", "jira", ignore)
        if mismatches:
            for mismatch in mismatches:
                print(mismatch)
            self.fail()

    def test_refresh_ignore_multiple_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            shutil.copy(spec, temp_dir)

            refresh_controller = RefreshController.new_from_cli(
                verbose=False,
                target_dir=temp_dir,
                spec_path=base64_plugin,
                ignore=["help.md", "dockerfile", "unit_test"],
            )

            refresh_controller.refresh()

    @parameterized.expand(
        [
            ["help.md"],
            ["dockerfile"],
            ["unit_test"],
        ],
    )
    def test_refresh_ignore_file(self, ignore_file):
        with tempfile.TemporaryDirectory() as temp_dir:
            shutil.copy(spec, temp_dir)

            refresh_controller = RefreshController.new_from_cli(
                verbose=False,
                target_dir=temp_dir,
                spec_path=base64_plugin,
                ignore=[ignore_file],
            )

            refresh_controller.refresh()


class TestRefreshUtil:
    @staticmethod
    def test_refresh(
        plugin_dir: str, plugin_name: str, _ignore: ignore = "", target_dir: str = None
    ) -> List[str]:
        # Examples of correctly created plugins exist under the tests/resources path
        test_dir = os.path.join(TEST_RESOURCES, plugin_dir)
        expect_dir = os.path.join(test_dir, plugin_name)
        # This is the plugin.spec.yaml that is adjacent to the generated plugin directory, not inside the plugin dir
        spec_file_path = os.path.join(test_dir, PluginSpecConstants.FILENAME)
        # We create a temporary directory for the resulting content created by the test subject
        with tempfile.TemporaryDirectory() as temp_dir:
            create_feature = CreateController.new_from_cli(
                spec_path=spec_file_path,
                verbose=True,
                target_dir=target_dir if target_dir is not None else temp_dir,
            )
            # This method is the test subject!
            create_feature.create()
            # breakpoint()
            refresh_feature = RefreshController.new_from_cli(
                spec_path=spec_file_path,
                verbose=True,
                target_dir=os.path.join(temp_dir, plugin_name),
                ignore=_ignore,
            )
            refresh_feature.refresh()

            result_dir = os.path.join(
                target_dir if target_dir is not None else temp_dir, plugin_name
            )
            return TestRefreshUtil.compare_dir_contents(expect_dir, result_dir, True)

    @staticmethod
    def compare_dir_contents(
        expect_dir: str, result_dir: str, verbose: bool = False
    ) -> List[str]:
        """
        Make a list of differences that the resulting directory content
        has from the expected content directory content.
        :param expect_dir: Path to a directory with the correct contents we expect from the test subject
        :param result_dir: Path to a directory with the actual contents created by the test subject
        :param verbose: Flag to print file differences or not, default is non-verbose
        :return: A list of strings describing mismatches result_dir has compared to expected_dir, pass if empty
        """
        mismatches = []
        # Traverses all plugin directory contents
        # TestCreateUtil.recursive_check(expect_dir, result_dir, mismatches) # Try this if walk() traversal fails
        for path, dirs, files in os.walk(expect_dir):
            expect_path = os.path.join(expect_dir, path)
            # result_path should have the same path under result_dir as the expect_path has under expect_dir
            result_path = os.path.join(
                result_dir, os.path.relpath(expect_path, expect_dir)
            )
            # Assert that the expected directory exists in the result
            if not os.path.exists(result_path):
                result_path = result_path.replace("komand_", "icon_")
                if not os.path.exists(result_path):
                    mismatches.append(f"{result_path} directory not found.")
                    continue
            # Iterate over the files in this directory to verify existence & content match
            for _file in files:
                expect_file = os.path.join(expect_path, _file)
                result_file = os.path.join(result_path, _file)
                # Assert that the expected file exists in the result
                if not os.path.exists(result_file):
                    result_file = result_file.replace("komand_", "icon_")
                    if not os.path.exists(result_file):
                        mismatches.append(f"{result_file} file not found.")
                        continue
                # Files both exist, now we compare the contents
                if not cmp(expect_file, result_file):
                    if not _file.__eq__(".CHECKSUM"):
                        mismatches.append(
                            f"{result_file} does not match expected content."
                        )
                        continue
                if verbose:
                    print(f"{result_file} matches expected content!")
        # If all files exist and match, mismatches should be empty
        return mismatches

    @staticmethod
    def recursive_check(expect, result, mismatches: [str]):
        """An alternate traversal implementation for TestCreateUtil.compare_dir_contents() using recursion"""
        if os.path.isdir(expect):
            if not os.path.exists(result):
                mismatches.append(f"directory {expect} not produced in result")
                return mismatches
            else:
                for items in os.listdir(expect):
                    result_item = os.path.join(result, items)
                    expect_item = os.path.join(expect, items)
                    mismatches = TestRefreshUtil.recursive_check(
                        expect_item, result_item, mismatches
                    )
                return mismatches
        else:
            if not os.path.exists(result):
                mismatches.append(f"{result} file not found.")
                return mismatches
            if not cmp(expect, result):
                mismatches.append(f"{result} does not match expected content.")
                return mismatches
        return mismatches
