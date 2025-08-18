import subprocess  # nosec
import shutil
from insight_plugin.features.common.exceptions import InsightException
from typing import Callable


class CommandLineUtil:
    @staticmethod
    def does_program_exist(program_name: str) -> bool:
        """
        :param program_name: name of the program to lookup
        :return: true if the program exists, otherwise false
        """
        ret_code = bool(shutil.which(program_name))
        return ret_code

    @staticmethod
    def run_command(
        command: str, args: [str], throw_on_error=True, use_shell=False
    ) -> str:
        """
        :param command: command to run
        :param args: string list or arguments to call command with
        :param throw_on_error: if exit code is != 0, throw an exception
        :param use_shell: use a fully separate pseudo shell to execute
        :return: "" if no return code is 0, or all of stderr if there is an issue
        """

        if not CommandLineUtil.does_program_exist(command):
            raise SystemError(
                f"Could not find {command} executable. Make sure {command} is installed (and running)"
            )
        actual_command = [command] + args
        child_process = subprocess.run(  # pylint: disable=subprocess-run-check
            actual_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=use_shell,  # nosec
        )
        if child_process.returncode == 0:
            return str(child_process.stdout)
        else:
            if throw_on_error:
                raise InsightException(
                    message=f"Command {actual_command} failed.",
                    troubleshooting="Check the output for details.",
                )
            return str(child_process.stdout)

    @staticmethod
    def run_command_send_input(
        command: str,
        args: [str],
        input_: str = None,
        return_output: bool = False,
        output_function: Callable[[str], None] = print,
    ):
        if not CommandLineUtil.does_program_exist(command):
            raise SystemError(
                f"Could not find {command} executable. Make sure {command} is installed (and running)"
            )
        actual_command = [command] + args
        output = []
        try:
            with open(input_, encoding="utf-8") as f:
                with subprocess.Popen(  # nosec
                    actual_command, stdout=subprocess.PIPE, stdin=f
                ) as p:  # nosec
                    while True:
                        line = p.stdout.readline().decode("utf-8")
                        if len(line) == 0:
                            break
                        if not return_output:
                            output_function(line)
                        output.append(line)
                    p.stdout.close()
                    p.wait()
            return output
        except FileNotFoundError:
            raise InsightException(
                message=f"Could not find input file {input_} to be used for: {actual_command}.",
                troubleshooting=f"Create the file {input_} to continue.",
            )
