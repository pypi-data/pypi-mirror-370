from insight_plugin.features.common.common_feature import CommonFeature
from insight_plugin.constants import SubcommandDescriptions
from insight_plugin.features.common.docker_util import DockerUtil


class RunController(CommonFeature):
    """
    Controls the subcommand for run
    Allows the user to run the plugin
    """

    HELP_MSG = SubcommandDescriptions.RUN_DESCRIPTION

    def __init__(  # pylint: disable=too-many-positional-arguments
        self,
        verbose: bool,
        target_dir: str,
        rebuild: bool,
        assessment: bool,
        is_test: bool,
        jq_: str,
        json_target: str,
        volumes: [str],
    ):
        super().__init__(verbose, target_dir)
        self._verbose = verbose
        self.json_target = json_target
        self.rebuild = rebuild
        self.is_test = is_test
        self.assessment = assessment
        self.volumes = volumes
        self.jq = jq_

    @classmethod
    def new_from_cli(cls, **kwargs):
        super().new_from_cli(
            **{"verbose": kwargs.get("verbose"), "target_dir": kwargs.get("target_dir")}
        )
        return cls(
            kwargs.get("verbose"),
            kwargs.get("target_dir"),
            kwargs.get("rebuild"),
            kwargs.get("assessment"),
            kwargs.get("is_test"),
            kwargs.get("jq_"),
            kwargs.get("json_target"),
            kwargs.get("volumes"),
        )

    def run(self):
        """
        Main run function for Run .json test file.
        :return:
        """
        docker_util = DockerUtil(
            verbose=self._verbose,
            target_dir=self.target_dir,
            rebuild=self.rebuild,
            assessment=self.assessment,
            is_test=self.is_test,
            json_target=self.json_target,
            volumes=self.volumes,
            _jq=self.jq,
            run=True,
        )
        docker_util.run_docker_command()
