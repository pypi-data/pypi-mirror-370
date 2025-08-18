from insight_plugin.features.common.common_feature import CommonFeature
from insight_plugin.constants import SubcommandDescriptions
from insight_plugin.features.common.docker_util import DockerUtil


class RunShellController(CommonFeature):
    """
    Controls the subcommand for Run Shell
    Allows the user to run the plugin via the docker shell
    """

    HELP_MSG = SubcommandDescriptions.SHELL_DESCRIPTION

    def __init__(
        self,
        verbose: bool,
        target_dir: str,
        rebuild: bool = False,
        volumes: [str] = None,
    ):
        super().__init__(verbose, target_dir)
        self.rebuild = rebuild
        self.volumes = volumes
        self._verbose = verbose

    @classmethod
    def new_from_cli(cls, **kwargs):
        super().new_from_cli(
            **{"verbose": kwargs.get("verbose"), "target_dir": kwargs.get("target_dir")}
        )
        return cls(**kwargs)

    def run(self):
        docker_util = DockerUtil(
            verbose=self._verbose,
            target_dir=self.target_dir,
            rebuild=self.rebuild,
            volumes=self.volumes,
            shell=True,  # nosec
        )

        docker_util.run_docker_command()
