import os
import shutil

from typing import List

from insight_plugin.features.common.exceptions import InsightException
from insight_plugin.features.connector_to_plugin.help.constants import (
    FileExtensionsConstants as Constants,
)
from insight_plugin import ROOT_DIR


def copy_archived_packages(source_dir: str, target_dir: str, package: str) -> None:
    """
    Copies archived packages from source to target directory
    :param source_dir: The absolute path to the source directory
    :param target_dir: The absolute path to the target directory
    :param package: The package name
    :return:
    """
    _, file_extension = os.path.splitext(package)

    if file_extension in [Constants.GZ, Constants.ZIP]:
        try:
            source_package = os.path.join(source_dir, package)
            shutil.copyfile(source_package, os.path.join(target_dir, package))
        except FileNotFoundError:
            raise InsightException(
                message=f"{package} not found",
                troubleshooting=f"Ensure {package} is in the {source_dir} path.",
            )


def copy_app_folder_to_utils(source_dir: str, target_dir: str) -> None:
    """
    Copy all of the contents from the _app folder of the connector to the plugins util folder

    :param str source_dir: The path to connector folder
    :param str target_dir: THhe path to the plugins util folder
    """

    for folder in os.listdir(source_dir):
        if folder.endswith("_app"):
            for filename in os.listdir(os.path.join(source_dir, folder)):
                if os.path.isfile(os.path.join(os.path.join(source_dir, folder), filename)):
                    shutil.copyfile(
                        os.path.join(os.path.join(source_dir, folder), filename), os.path.join(target_dir, filename)
                    )
                elif os.path.isdir(os.path.join(os.path.join(source_dir, folder), filename)):
                    shutil.copytree(
                        os.path.join(os.path.join(source_dir, folder), filename), os.path.join(target_dir, filename)
                    )
            break

    # if there is no app folder, this is a Surcom Connector and
    # we need to copy the functions folder
    functions_folder = os.path.join(source_dir, "functions")

    if os.path.exists(functions_folder):

        shutil.copytree(functions_folder, os.path.join(target_dir, "functions"), dirs_exist_ok=True)


def copy_types_folder(source_dir: str, target_dir: str) -> None:
    """
    Copy all of the contents from the types folder of the connector to the plugins folder

    :param str source_dir: The path to connector folder
    :param str target_dir: The path to the plugins folder
    """

    types_folder = os.path.join(source_dir, "types")

    if os.path.exists(types_folder):
        for filename in os.listdir(types_folder):
            if os.path.isfile(os.path.join(types_folder, filename)):
                shutil.copyfile(
                    os.path.join(types_folder, filename), os.path.join(target_dir, filename)
                )


def copy_images(target_dir: str, file_location: str = "connector") -> None:
    """
    Copy placeholder images into the plugin

    :param str target_dir: The path to copy the images to
    :param str file_location: The location of the images in the templates directory
    """
    for image in ("extension.png", "icon.png"):
        shutil.copyfile(
            os.path.join(f"{ROOT_DIR}/templates/{file_location}/images", image),
            os.path.join(target_dir, image),
        )


def copy_spec_file(target_dir_name) -> None:
    """
    A method to copy the generated spec file into the plugin

    :param _type_ target_dir_name: The path of the plugin to copy the plugin.spec.yaml file to
    """
    shutil.copyfile(
        os.path.join(os.getcwd(), "plugin.spec.yaml"),
        os.path.join(target_dir_name, "plugin.spec.yaml"),
    )
