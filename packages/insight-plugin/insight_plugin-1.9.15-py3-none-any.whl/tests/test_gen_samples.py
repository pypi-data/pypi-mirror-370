import shutil
import tempfile
import unittest
import sys
import os
import filecmp
import subprocess

sys.path.append(os.path.abspath("../"))

from insight_plugin.features.common.exceptions import InsightException
from insight_plugin.features.samples.controller import GenSampleController
from tests import TEST_RESOURCES

plugin_dir_base_64 = os.path.join(TEST_RESOURCES, "test_base64/base64")
test_files = os.path.join(TEST_RESOURCES, "test_base64/tests")
spec = os.path.join(plugin_dir_base_64, "plugin.spec.yaml")


class TestSamples(unittest.TestCase):
    def test_samples_all(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            shutil.copy(spec, temp_dir)

            sample_controller = GenSampleController.new_from_cli(
                verbose=True,
                target_dir=temp_dir,
            )

            sample_controller.samples()
            result_dir = os.path.join(temp_dir, "tests")
            if not filecmp.cmpfiles(
                test_files, result_dir, ["encode.json", "decode.json"]
            ):
                self.fail()

    def test_samples_action_single(self):
        test_files_decode = os.path.join(test_files, "decode.json")

        with tempfile.TemporaryDirectory() as temp_dir:
            shutil.copy(spec, temp_dir)

            sample_controller = GenSampleController.new_from_cli(
                verbose=True, target_dir=temp_dir, target_component="decode"
            )

            sample_controller.samples()
            result_dir = os.path.join(temp_dir, "tests/decode.json")
            if not filecmp.cmp(result_dir, test_files_decode):
                self.fail()

    def test_samples_trigger_single(self):
        test_files_new_trigger = os.path.join(test_files, "new_trigger.json")

        with tempfile.TemporaryDirectory() as temp_dir:
            shutil.copy(spec, temp_dir)

            sample_controller = GenSampleController.new_from_cli(
                verbose=True, target_dir=temp_dir, target_component="new_trigger"
            )

            sample_controller.samples()
            result_dir = os.path.join(temp_dir, "tests/new_trigger.json")
            if not filecmp.cmp(result_dir, test_files_new_trigger):
                self.fail()

    def test_samples_task_single(self):
        test_files_new_task = os.path.join(test_files, "new_task.json")

        with tempfile.TemporaryDirectory() as temp_dir:
            shutil.copy(spec, temp_dir)

            sample_controller = GenSampleController.new_from_cli(
                verbose=True, target_dir=temp_dir, target_component="new_task"
            )

            sample_controller.samples()
            result_dir = os.path.join(temp_dir, "tests/new_task.json")
            if not filecmp.cmp(result_dir, test_files_new_task):
                self.fail()

    def test_samples_component_not_found(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            shutil.copy(spec, temp_dir)

            sample_controller = GenSampleController.new_from_cli(
                verbose=False, target_dir=temp_dir, target_component="new_action"
            )
            with self.assertRaises(InsightException) as context:
                sample_controller.samples()

            self.assertEqual(
                context.exception.troubleshooting,
                "Verify that the target component is correctly spelled "
                "and defined in the spec",
            )

    def test_non_directory(self):
        with tempfile.TemporaryDirectory():
            with self.assertRaises(InsightException) as context:
                GenSampleController.new_from_cli(
                    verbose=False,
                    target_dir="thisdirectorydoesnotexist",
                    target_component="new_action",
                )

            self.assertEqual(
                context.exception.troubleshooting,
                "Verify that the target path is correct, accessible, and a directory",
            )

    def test_direct_command(self):
        """Test running the command from CLI parses correctly and the expected output."""
        with tempfile.TemporaryDirectory() as temp_dir:
            shutil.copy(spec, temp_dir)

            output = subprocess.check_output(
                f"insight-plugin samples -d {temp_dir} -v", shell=True
            ).decode("utf-8")

            # INFO log should be included with using verbose flag
            self.assertIn("INFO: SamplesUtil", output)
            self.assertIn("Samples process complete!", output)
