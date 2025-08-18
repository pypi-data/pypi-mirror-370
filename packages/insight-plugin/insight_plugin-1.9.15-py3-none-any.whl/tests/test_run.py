import unittest
import sys
import os
from unittest.mock import patch, call

sys.path.append(os.path.abspath("../"))
from insight_plugin.features.common.exceptions import (
    InsightException,
    RunCommandExceptions,
)
from insight_plugin.features.run.bash_controller import RunShellController
from insight_plugin.features.run.run_controller import RunController
from insight_plugin.features.run.server_controller import RunServerController
from tests import TEST_RESOURCES


class TestRun(unittest.TestCase):
    def test_run_okay(self):
        target_dir = f"{TEST_RESOURCES}/test_base64"
        run_controller = RunController.new_from_cli(
            verbose=False,
            target_dir=target_dir,
            rebuild=False,
            assessment=False,
            is_test=False,
            json_target=f"{TEST_RESOURCES}/test_base64/tests/encode.json",
            volumes=False,
            _jq=False,
        )
        return run_controller.run()

    def test_run_invalid_json(self):
        target_dir = f"{TEST_RESOURCES}/run_tests/run_test_base64/base64"
        run_controller = RunController.new_from_cli(
            verbose=True,
            target_dir=target_dir,
            assessment=False,
            is_test=False,
            json_target="tests/invalid_file.json",
        )
        with self.assertRaises(InsightException) as error:
            run_controller.run()
            self.assertEqual(
                error.exception.troubleshooting,
                RunCommandExceptions.TEST_FILE_INVALID_JSON_TROUBLESHOOTING,
            )

    def test_run_missing_type(self):
        target_dir = f"{TEST_RESOURCES}/run_tests/run_test_base64/base64"
        run_controller = RunController.new_from_cli(
            verbose=True,
            target_dir=target_dir,
            assessment=False,
            is_test=False,
            json_target="tests/decode_missing_type.json",
        )
        with self.assertRaises(InsightException) as error:
            run_controller.run()
            self.assertEqual(
                error.exception.troubleshooting,
                RunCommandExceptions.JSON_TYPE_NOT_IN_JSON_TROUBLESHOOTING,
            )

    def test_missing_json(self):
        target_dir = f"{TEST_RESOURCES}/run_tests/run_test_base64/base64"
        run_controller = RunController.new_from_cli(
            verbose=False,
            target_dir=target_dir,
            assessment=False,
            is_test=False,
            json_target="tests/decode_non_existent_file.json",
        )
        with self.assertRaises(InsightException) as error:
            run_controller.run()
            self.assertEqual(
                error.troubleshooting,
                RunCommandExceptions.TEST_FILE_NOT_FOUND_TROUBLESHOOTING,
            )

    def test_run_all(self):
        target_dir = f"{TEST_RESOURCES}/run_tests/normal_base64"
        run_controller = RunController.new_from_cli(
            verbose=True,
            target_dir=target_dir,
            assessment=True,
            is_test=True,
            volumes=False,
            json_target=None,
        )
        run_controller.run()

    def test_run_server(self):
        target_dir = f"{TEST_RESOURCES}/test_base64/base64"
        server_controller = RunServerController.new_from_cli(
            verbose=False,
            target_dir=target_dir,
            volumes=None,
            ports=None,
            rebuild=False,
            is_unit_test=True,
        )
        server_controller.run()

        # Test should pass, tidy up the test container.
        os.system("docker stop unit_test_container")
        os.system("docker rm unit_test_container")

    @patch("os.system", return_value=0)
    def test_run_bash(self, mocked_command):
        target_dir = f"{TEST_RESOURCES}/test_base64/base64"
        bash_controller = RunShellController.new_from_cli(
            verbose=False, target_dir=target_dir, rebuild=False
        )

        bash_controller.run()
        # we have to mock the call to os.system otherwise docker raises an error calling `-it` from within a unit test.
        # the best way to test is to check we call the correct docker command
        command = call("docker run --rm --entrypoint sh -i -t rapid7/base64:1.1.6")
        self.assertEqual(mocked_command.call_args_list[0], command)

    @patch("os.system", return_value=0)
    def test_build_shell_cmd(self, mocked_command):
        target_dir = f"{TEST_RESOURCES}/run_tests/run_test_base64/base64"
        run_shell_controller = RunShellController.new_from_cli(
            verbose=True,
            target_dir=target_dir,
            rebuild=False,
            volumes=["/var/cache:/var/cache"],
        )

        run_shell_controller.run()
        command = call(
            "docker run --rm --entrypoint sh -i -t rapid7/base64:1.1.6 -v /var/cache:/var/cache --debug"
        )
        self.assertEqual(mocked_command.call_args_list[0], command)
