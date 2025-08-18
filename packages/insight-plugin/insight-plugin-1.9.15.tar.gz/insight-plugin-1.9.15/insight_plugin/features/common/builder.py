from insight_plugin.features.common.command_line_util import CommandLineUtil
from insight_plugin.features.common.logging_util import BaseLoggingFeature
from insight_plugin.features.common.exceptions import InsightException
from insight_plugin.features.common.plugin_spec_util import PluginSpecUtil
from enum import Enum

# TODO - Move to export Util, its not a common util


class BuilderOperation(Enum):
    TARBALL = "tarball"
    IMAGE = "image"


class Builder(BaseLoggingFeature):
    def __init__(  # pylint: disable=too-many-positional-arguments
        self,
        operation: BuilderOperation,
        includes: [str],
        verbose: bool,
        no_pull: bool,
        full_command: str = None,
        target_dir: str = None,
    ):
        super().__init__(verbose=verbose)
        self._operation = operation
        self._includes = includes
        self._no_pull = no_pull
        self._full_command = full_command
        self._image_name = None
        self._target_dir = target_dir

    @classmethod
    def new_from_cli(  # pylint: disable=too-many-positional-arguments
        cls,
        operation: BuilderOperation,
        includes: [str],
        verbose: bool,
        no_pull: bool,
        full_command: str = None,
        target_dir: str = None,
    ):
        builder = cls(
            operation=operation,
            includes=includes,
            verbose=verbose,
            no_pull=no_pull,
            full_command=full_command,
            target_dir=target_dir,
        )

        return builder

    @property
    def full_command(self):
        return self._full_command

    @property
    def image_name(self):
        return self._image_name

    def build(self, spec):
        cmd = "docker"

        # TODO from icon-plugin: cleanup dir?

        # Run Docker build
        plugin_name = PluginSpecUtil.get_docker_name(spec)
        self._image_name = plugin_name
        if self._no_pull:
            self.logger.info(
                "Using --no-pull option; will not pull latest base image during build"
            )
            args = ["build", "-t", plugin_name, self._target_dir]
        else:
            args = ["build", "--pull", "-t", plugin_name, self._target_dir]

        self.logger.info(f"Running build command : {cmd} {args}")

        err = CommandLineUtil.run_command(cmd, args)
        if err:
            self.logger.error(err)
            raise InsightException(
                message="Docker build command failed",
                troubleshooting="Check docker install and error logs",
            )

        # Run Docker tag
        plugin_tag = f"{spec['vendor']}/{spec['name']}:latest"

        self.logger.info("Tagging docker image")

        args = ["tag", plugin_name, plugin_tag]
        err = CommandLineUtil.run_command(cmd, args)
        if err:
            self.logger.error(err)
            raise InsightException(
                message="Failed to tag docker image",
                troubleshooting="Check the logs and consider contacting support",
            )
