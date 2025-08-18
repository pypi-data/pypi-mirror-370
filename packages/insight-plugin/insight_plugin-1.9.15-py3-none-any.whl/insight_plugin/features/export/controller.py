import os
import gzip
import shutil
from insight_plugin.features.common.plugin_spec_util import PluginSpecUtil
from insight_plugin.features.common.builder import Builder, BuilderOperation
from insight_plugin.features.common.common_feature import CommonFeature
from insight_plugin.features.common.command_line_util import CommandLineUtil
from insight_plugin.features.common.temp_file_util import SafeTempDirectory
from insight_plugin.features.common.exceptions import InsightException
from insight_plugin.constants import SubcommandDescriptions


class ExportController(CommonFeature):
    """
    Controls the subcommand for export
    Allows the user to export the plugin image to a tarball
    """

    HELP_MSG = SubcommandDescriptions.EXPORT_DESCRIPTION

    def __init__(
        self,
        no_pull: bool,
        verbose: bool,
        target_dir: str,
    ):
        super().__init__(verbose, target_dir)
        # TODO: Add check for help flag and output nicely formatted help string
        self.no_pull = no_pull
        self.spec = None
        self._builder = None
        self._target_name = None
        self._verbose = verbose

    @classmethod
    def new_from_cli(cls, **kwargs):
        super().new_from_cli(
            **{"verbose": kwargs.get("verbose"), "target_dir": kwargs.get("target_dir")}
        )
        return cls(
            kwargs.get("no_pull"), kwargs.get("verbose"), kwargs.get("target_dir")
        )

    def export(self) -> None:
        """

        :return: return code, 0 for success, others for fail # TODO
        """
        # TODO: Support other modes
        # TODO: Pass in the path from the CLI arguments
        self.spec = PluginSpecUtil.get_spec_file(self.target_dir)

        # first build the base image
        print("Beginning export.. ")
        self.logger.info("Starting Build Sequence / Building docker image")
        self._build_image()

        if self.check_for_existing_plg(self.target_dir):
            SafeTempDirectory.execute_safe_dir(self._safe_export, self.target_dir, True)
            print("Export process complete!")
        else:
            print("Export process failed!")

    def check_for_existing_plg(self, plugin_dir: str) -> bool:
        """
        Simple helper method to check if a .plg already exists in the current plugin dir

        :param plugin_dir: Name of the plugin dir

        :return: False if file exists, else True
        """
        # List contents in plugin directory
        dir_contents = os.listdir(plugin_dir)
        for file in dir_contents:
            if file.endswith(".plg"):
                self.logger.critical(
                    "A .plg exists in the current directory, please delete old .plg file before running export"
                )
                return False

        return True

    def _safe_export(self, tmpdirname: str) -> None:
        """

        :param tmpdirname: temporary directory name to save files in while exporting
        :return: None
        """
        # define useful constants
        package_base = (
            f"{self.spec['vendor']}_{self.spec['name']}_{self.spec['version']}.plg"
        )
        package_base = os.path.join(tmpdirname, package_base)
        self._target_name = os.path.join(
            self.target_dir, os.path.basename(package_base)
        )
        executable = "docker"

        # now export the docker image to tar (.plg)
        self.logger.info("Building plugin tarball")
        self._build_plugin_tarball(package_base, executable)

        # gzip file
        self.logger.info("Zipping file")
        gzip_name = package_base + ".gz"
        self._compress_file(package_base, gzip_name)

        # rename file to tar ext
        self.logger.debug("Renaming file for upload")
        try:
            os.rename(gzip_name, package_base)
        except OSError as error:
            self.logger.error(f"Could not rename zipped file due to OS error: {error}")
            raise InsightException(
                message="Could not rename zipped file due to an OS error.",
                troubleshooting="Verify write permissions for the target directory.",
            ) from error

    def _build_plugin_tarball(self, dest_name: str, cmd: str) -> None:
        """
        Build a plugin tarball from an existing image
        :param dest_name: filename for the resulting tarball
        :param cmd: command to run save for ('docker' for the foreseeable future)
        :return: None
        """
        args = ["save", self._builder.image_name, "-o", dest_name]
        error = CommandLineUtil.run_command(cmd, args)
        if error:
            self.logger.error(error)
            # Not the best troubleshooting info, but its some docker save error, where the build already succeeded
            raise InsightException(
                message="Docker save step failed",
                troubleshooting="Check the log for details",
            )

    def _compress_file(self, src_name: str, dest_name: str) -> None:
        """
        Compress a file with gzip
        :param src_name: filename to be compressed
        :param dest_name: name to save the compressed file as
        :return: None
        """
        with open(src_name, "rb") as f_in:
            with gzip.open(dest_name, "wb", compresslevel=6) as f_out:
                shutil.copyfileobj(f_in, f_out)

    def _build_image(self) -> None:
        # simply a short function to break export down into smaller steps
        self._builder = Builder.new_from_cli(
            BuilderOperation.TARBALL,
            [],
            verbose=self._verbose,
            no_pull=self.no_pull,
            target_dir=self.target_dir,
        )
        if self._builder.build(self.spec) is not None:
            self.logger.error("Build process failed")
            raise InsightException(
                message="Docker build step failed",
                troubleshooting="Check the dockerfile, or create the dockerfile if it does not exist",
            )

    @property
    def target_name(self):
        return self._target_name
