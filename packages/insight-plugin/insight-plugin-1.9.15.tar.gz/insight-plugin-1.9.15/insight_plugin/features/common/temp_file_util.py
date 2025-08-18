import shutil
from insight_plugin.features.common.logging_util import BaseLoggingFeature
from insight_plugin.features.common.exceptions import InsightException
import logging
import tempfile
import os
from typing import Callable, Any
from pathlib import Path


class SafeTempDirectory(BaseLoggingFeature):
    # class to handle operations that only write to a directory if the operations all succeed
    def __init__(self, verbose):
        super().__init__(verbose=verbose)

    @staticmethod
    def execute_safe_dir(
        func: Callable[[str, Any], None],
        target_dir: str,
        overwrite: bool,
        *args,
    ):
        """
        Function for running filesystem operations safely in a temp directory.
        :param func: function to run using the temp directory
        :param target_dir: string, target directory to copy everything to upon success
        :param overwrite: overwrite existing files from matching trees in the temp dir and target dir
        :return:
        """
        logger = logging.getLogger(name=SafeTempDirectory.__name__)
        logger.debug("Making temporary directory to preserve dir in case of failure")
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                func(temp_dir, *args)
            except Exception as error:
                raise InsightException(
                    message=f"Did not write temp dir to dest due to exception in function {error}",
                    troubleshooting="Ensure the plugin.spec.yaml is written and formatted correctly.",
                ) from error
            # If we made it here, the function succeeded. Write package base name (minus temp dir) back to target dir
            logger.debug(f"Writing files from temporary directory to target dir: {target_dir}")
            SafeTempDirectory.copy_dir_over(temp_dir, target_dir, overwrite=overwrite)
            logger.debug(f"Write to target dir '{target_dir}' succeeded")

    @staticmethod
    def copy_dir_over(temp_dir, target_dir, overwrite: bool = False):
        for item in os.listdir(temp_dir):
            # setup:
            # item path is complete path from temp dir to current item
            item_path = os.path.join(temp_dir, item)
            # path that would exist at the dest:
            target_path = os.path.join(target_dir, item)
            # does this item already exist at the dest?
            does_item_exist = os.path.exists(target_path)

            # check if the current item to copy is an entire directory
            if os.path.isdir(item_path):
                if overwrite:
                    # Overwrite is true, so we can just move the entire dir over
                    shutil.copytree(item_path, target_dir, dirs_exist_ok=True)
                # if we are copying an entire dir that does not exist, might as well take the dir recursively here
                elif not does_item_exist:
                    shutil.move(item_path, target_dir)
                # else this dir already exists at target, recurse on items inside this temp dir
                else:
                    SafeTempDirectory.copy_dir_over(item_path, target_path, overwrite)
            # else this is a file. If it exists and we want to overwrite, or if it doesn't exist at all, copy it in
            elif (does_item_exist and overwrite) or not does_item_exist:
                shutil.copy(item_path, target_dir)
