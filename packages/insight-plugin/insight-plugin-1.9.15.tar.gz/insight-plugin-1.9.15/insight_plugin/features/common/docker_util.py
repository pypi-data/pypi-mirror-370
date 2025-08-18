import os
import json
from insight_plugin.features.common.command_line_util import CommandLineUtil
from typing import Optional, Union, Any, List
from insight_plugin import ROOT_DIR, DOCKER_CMD
from insight_plugin.features.common.template_util import Templates
from insight_plugin.features.create.json_generation_util import JSONFormatting
from insight_plugin.features.common.exceptions import (
    InsightException,
    RunCommandExceptions,
)
from insight_plugin.features.common.logging_util import BaseLoggingFeature
from insight_plugin.features.common.plugin_spec_util import (
    PluginSpecUtil,
)
import jq


class DockerUtil(BaseLoggingFeature):
    def __init__(  # pylint: disable=too-many-positional-arguments
        self,
        verbose: bool,
        target_dir: str,
        rebuild: bool = False,
        run: bool = False,
        json_target: str = None,
        assessment: bool = False,
        is_test: bool = False,
        server: bool = False,
        volumes: [str] = None,
        ports: [str] = None,
        _jq: str = None,
        shell: bool = False,
        is_unit_test: bool = False,
    ):
        super().__init__(verbose=verbose)
        self.verbose = verbose
        self.target_dir = target_dir
        self.is_test = is_test
        self.json_target = json_target
        self.volumes = volumes
        self.assessment = assessment
        self.ports = ports
        self.jq = _jq
        self.run = run
        self.server = server
        self.rebuild = rebuild
        self.shell = shell
        self.run_outputs = []
        self.test_outputs = []
        self.is_unit_test = is_unit_test

    def run_docker_command(self) -> None:
        """
        Build out the docker command and run it depending
        on whether it is run or server.
        :return:
        """

        # Rebuild first if flagged
        if self.rebuild:
            self.rebuild_command()

        # Run
        if self.run:
            self.manage_run()

        # Server or Bash
        else:
            self.run_command()

    def manage_run(self) -> None:
        """
        Check if json path is provided. If it is, run individual component, else
        run all components.
        :return:
        """
        if self.json_target:
            if self.is_test:
                # Only first needed for connection test
                self.run_component_json(self.json_target)
            else:
                self.run_component_json(self.json_target)
        else:
            self._run_all()

        if self.assessment:
            self._create_assessment()

    def run_command(self) -> None:
        """
        Helper command to cli run the created docker command.
        :return:
        """
        command = self._build_command(False)

        return_code = os.system(command)  # nosec

        if return_code == 0:
            return
        elif return_code != 0:
            self.logger.error(f"Return code from shell was {return_code}")
            raise InsightException(
                message=RunCommandExceptions.ERROR_INVOKING_SHELL_MESSAGE,
                troubleshooting=RunCommandExceptions.ERROR_INVOKING_SHELL_TROUBLESHOOTING,
            )

    def run_component_json(
        self,
        json_path: str,
    ) -> None:
        """
        Runs a single json test file. Options encoded into self
        :param json_path: path (relative or absolute) to the json test file we will run
        :return: None
        """
        if not self.is_test:
            self.logger.info(f"Running {json_path}")
        else:
            self.logger.info(f"Running connection test with {json_path}")

        # Handle the input
        self._check_test_file(json_path)

        command_args = self._build_command(args_list_only=True)
        possible_results = CommandLineUtil.run_command_send_input(
            DOCKER_CMD, command_args, input_=json_path, return_output=self.assessment
        )

        # The rest here is just for jq and assessment.
        command_run = self._build_command(args_list_only=False)
        command = Formatter(command_run, possible_results)

        if self.is_test:
            self.test_outputs.append(command)
        else:
            self.run_outputs.append(command)

        if self.assessment:
            command.serialize_last_output()
        if self.jq:
            command.jq_output(self.jq)

    def _create_assessment(self) -> None:
        """
        Return assessment.jinja filled out with assessment details.
        :return:
        """
        templates_dir = Templates(os.path.join(ROOT_DIR, "templates"))

        assessment_dict = {
            "tests": self.test_outputs,
            "runs": self.run_outputs,
        }

        file_content = templates_dir.fill(
            os.path.join("assessment", "assessment.jinja"), assessment_dict
        )

        print(file_content)

    def rebuild_command(self) -> None:
        """
        Run 'make image' command.
        Use make image since it is much quicker to build but
        still applies code changes
        """
        try:
            os.system("make image")  # nosec
        except FileNotFoundError as error:
            self.logger.error(f"No Makefile found: {error}")

    def _get_docker_container(self) -> str:
        """
        Helper method to get docker name from spec file.
        :return:
        """
        spec_dict = PluginSpecUtil.get_spec_file(self.target_dir)
        docker_container = PluginSpecUtil.get_docker_name(spec_dict)
        return docker_container

    def _run_all(self) -> None:
        """
        Helper method to list through the tests directory and run each file.
        :return:
        """

        connection_test_run = False
        test_dir = os.path.join(self.target_dir, "tests")

        for file in os.listdir(test_dir):
            if file.endswith(".json"):
                json_path = os.path.join(test_dir, file)
                if self.is_test and not connection_test_run:
                    self.run_component_json(json_path)
                    # prevents this from being run again- only want 1 conn test
                    connection_test_run = True
                self.run_component_json(json_path)

    def _check_test_file(self, filepath) -> None:
        """
        Test if .json test file can be opened successfully.
        Return object if successful, else raise relevant error.
        :param filepath: Path to tests/{test}.json
        :return:
        """
        try:
            # open uses cwd if no absolute path is provided
            with open(filepath, "rt", encoding="utf-8") as spec_file:
                json_object = json.load(spec_file)
        except FileNotFoundError:
            raise InsightException(
                message=f"{os.path.basename(filepath)} not found in {os.path.dirname(filepath)}.",
                troubleshooting=RunCommandExceptions.TEST_FILE_NOT_FOUND_TROUBLESHOOTING,
            )
        except PermissionError as error:
            self.logger.error(
                f"Permission error for file {filepath}. Check that your user has access to this file"
            )
            raise error
        except OSError as error:
            self.logger.error(f"Operating system could not open file {filepath}")
            raise error
        except json.JSONDecodeError as error:
            self.logger.error(f"Could not decode JSON object at {filepath}")
            raise InsightException(
                message=f"Could not decode JSON object at {filepath}",
                troubleshooting=RunCommandExceptions.TEST_FILE_INVALID_JSON_TROUBLESHOOTING,
            ) from error

        # Checks if the component with json in json_obj has type trigger or task to set the --debug part of docker cmd
        if json_object.get("type") is None:
            raise InsightException(
                message=f"{filepath} json does not contain the required 'type' field",
                troubleshooting="Add the field back in with (action/trigger/task)_start, "
                'e.g. "action_start".',
            )

    def _build_command(self, args_list_only: bool) -> Union[List[Union[str, Any]], str]:
        """
        Generalised docker argument build command.
        :return: A built out docker command string
        """

        args = []

        args_mapping = {
            "run": ["run", "--rm", "-i"],
            "server": ["run", "--rm"],
            "shell": [
                "run",
                "--rm",
                "--entrypoint",
                "sh",
                "-i",
                "-t",
                self._get_docker_container(),
            ],
        }

        for key, value in args_mapping.items():
            if getattr(self, key):
                args = value

        if self.ports:
            for port in self.ports:
                args.extend(["-p", port])

        if self.volumes:
            for volume in self.volumes:
                args.extend(["-v", volume])

        if self.run:
            args.extend([self._get_docker_container(), "--debug"])
            if self.is_test:
                args.append("test")
            else:
                args.append("run")
        elif self.server:
            # in a uit test we want to run in detached mode to let tests continue and not hang in attached server mode
            if self.is_unit_test:
                args.append("-d --name unit_test_container")
            args.extend([self._get_docker_container(), "http"])

        if self.verbose:
            args.append("--debug")

        if args_list_only:
            return args

        # Run (with json path)
        if self.run and self.json_target:
            command_run = f"{DOCKER_CMD} {' '.join(args)} < {self.json_target}"

        # Server | Run (without json path)
        else:
            command_run = f"{DOCKER_CMD} {' '.join(args)}"

        self.logger.info(f"Running command: {command_run}")

        return command_run


class Formatter:
    def __init__(
        self,
        command_run: str,
        full_output: [str],
        complete_one_line_output: Optional[str] = None,
    ):
        """
        Format the output for assessment and jq output.
        :param command_run: Docker run command built out as a string.
        :param full_output: Usual output expected from running the command.
        :param complete_one_line_output: Optional input in event of a single str return.
        """
        self.cmd_run = command_run

        if complete_one_line_output is None:
            self.full_output = full_output
        else:
            self.full_output = complete_one_line_output

        self.output = ""

    def serialize_last_output(self) -> None:
        """
        Serialize the output for assessment mode
        :return:
        """
        if len(self.full_output) > 0:
            # handling the case that full output is a list
            if isinstance(self.full_output, list):
                last_line = self.full_output[-1]
            # or that it is one long string
            else:
                last_line = self.full_output
            try:
                last_line_obj = json.loads(last_line)
            except json.JSONDecodeError:
                raise InsightException(
                    message=RunCommandExceptions.LAST_OUTPUT_NOT_JSON_MESSAGE,
                    troubleshooting=RunCommandExceptions.LAST_OUTPUT_NOT_JSON_TROUBLESHOOTING,
                )
            self.output = json.dumps(last_line_obj, indent=JSONFormatting.INDENT)

    def jq_output(self, pattern) -> str:
        """
        JQ-ify the output of whatever command ran given the jq input
        :param pattern: The jq pattern the user inputted. Default is .body.output
        :return:
        """
        if len(self.full_output) > 0:
            try:
                jq_pattern = jq.compile(pattern)
            except ValueError as error:
                raise InsightException(
                    message=RunCommandExceptions.JQ_COMPILE_FAIL_MESSAGE,
                    troubleshooting=RunCommandExceptions.JQ_COMPILE_FAIL_TROUBLESHOOTING,
                ) from error
            try:
                jq_res = jq_pattern.input(text=self.full_output[-1]).all()
            except ValueError as error:
                raise InsightException(
                    message=RunCommandExceptions.JQ_PARSE_ERROR_MESSAGE,
                    troubleshooting=RunCommandExceptions.JQ_PARSE_ERROR_TROUBLESHOOTING,
                ) from error
            for obj in jq_res:
                # Don't want this to run through a logger due to the extra text being printed.
                print(json.dumps(obj, indent=JSONFormatting.INDENT))
            return jq_res
        else:
            return "No Command Output to JQ"
