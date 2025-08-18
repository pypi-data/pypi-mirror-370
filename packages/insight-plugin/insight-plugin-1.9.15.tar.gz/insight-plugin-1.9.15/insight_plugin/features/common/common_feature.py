import os

from insight_plugin.features.common.exceptions import InsightException
from insight_plugin.features.common.logging_util import BaseLoggingFeature


def set_target_dir(target_dir) -> str:
    """
    Check that the target directory is an existing path.
    If a target directory was not provided, assume the target dir is the current working directory.
    :param target_dir: The provided path to check
    :return: The target directory as a string
    """
    if target_dir is not None:
        if not os.path.isdir(target_dir):
            raise InsightException(
                message=f"The target directory {target_dir} does not exist",
                troubleshooting="Verify that the target path is correct, accessible, and a directory",
            )
        return target_dir
    else:
        return os.getcwd()


class CommonFeature(BaseLoggingFeature):
    def __init__(
        self,
        verbose: bool = False,
        target_dir: str = None,  # pylint: disable=unused-argument
    ):
        super().__init__(verbose=verbose)

    @classmethod
    def new_from_cli(cls, **kwargs):
        cls.target_dir = set_target_dir(kwargs.get("target_dir"))

    @property
    def verbose(self):
        return self._verbose

    @property
    def help(self):
        return self._help

    @property
    def target_dir(self):
        return self._target_dir
