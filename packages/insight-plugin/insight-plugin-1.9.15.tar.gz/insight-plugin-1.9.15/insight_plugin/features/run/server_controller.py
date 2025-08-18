from insight_plugin.features.common.common_feature import CommonFeature
from insight_plugin.constants import SubcommandDescriptions
from insight_plugin.features.common.docker_util import DockerUtil


class RunServerController(CommonFeature):
    """
    Controls the subcommand for Run Server
    Allows the user to run the plugin as a webserver
    """

    HELP_MSG = SubcommandDescriptions.SERVER_DESCRIPTION

    def __init__(  # pylint: disable=too-many-positional-arguments
        self,
        target_dir: str,
        volumes: [str],
        ports: [str],
        rebuild: bool,
        is_unit_test: bool,
    ):
        super().__init__(target_dir)
        self.rebuild = rebuild
        self.volumes = volumes
        self.ports = ports
        self.is_unit_test = is_unit_test

    @classmethod
    def new_from_cli(cls, **kwargs):
        super().new_from_cli(**{"target_dir": kwargs.get("target_dir")})
        return cls(
            kwargs.get("target_dir"),
            kwargs.get("volumes"),
            kwargs.get("ports"),
            kwargs.get("rebuild"),
            kwargs.get("is_unit_test", False),
        )

    def run(self):
        """
        Main run function for Run Server
        :return:
        """
        docker_util = DockerUtil(
            verbose=False,
            target_dir=self.target_dir,
            volumes=self.volumes,
            ports=self.ports,
            rebuild=self.rebuild,
            server=True,
            is_unit_test=self.is_unit_test,
        )
        docker_util.run_docker_command()
