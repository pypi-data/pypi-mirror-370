import json
import hashlib
from os import walk
from os.path import exists, isfile, isdir, join, basename
from typing import Dict, List
from insight_plugin import BASE_PREFIX, KOMAND_PREFIX
from insight_plugin.features.common.plugin_spec_util import (
    PluginSpecTypes,
    PluginSpecConstants,
)
from insight_plugin.features.common.exceptions import InsightException


class ChecksumUtil:
    """
    Util methods to generate a .CHECKSUM file for the plugin.
    The .CHECKSUM file contains a JSON object with name -> hash mappings
    for the plugin.spec.yaml (spec), binary executable (manifest), Python setup file (setup.py),
    and also an array of each schema.py file across all plugin components.
    """

    @staticmethod
    def _create_sum_from_file(target: str) -> str:
        """
        Produce an MD5 checksum hash of the target file.
        :param target: Path to file to be hashed.
        :return: String of the MD5 hash of the target file.
        """
        if not exists(target) or not isfile(target):
            raise InsightException(
                message=f"The file {target} could not be found.",
                troubleshooting="Verify that the target is real and is a file.",
            )
        # Ignoring the insecure use of the MD5 hash function because it is not used for security
        result = hashlib.md5()  # nosec
        with open(target, "rb") as target_file:
            result.update(target_file.read())
        return str(result.hexdigest())

    @staticmethod
    def _create_sum_spec(
        plugin_dir: str, spec_file_name: str = PluginSpecConstants.FILENAME
    ):
        """
        Produce the checksum for the plugin's spec file
        :param plugin_dir: The path to the plugin's spec file, usually root of plugin_dir/
        :param spec_file_name: The name of the plugin spec file, usually plugin.spec.yaml
        :return: The MD5 checksum of the plugin spec file
        """
        spec_path = join(plugin_dir, spec_file_name)
        return ChecksumUtil._create_sum_from_file(spec_path)

    @staticmethod
    def _create_sum_manifest(manifest_dir: str, manifest_name: str):
        """
        Produce the checksum for the plugin's binary executable manifest, usually plugin_dir/bin/icon_plugin-name
        :param manifest_dir: The path to the plugin's manifest directory, usually plugin_dir/bin/
        :param manifest_name: The name of the plugin's manifest file, usually icon_plugin-name
        :return: The MD5 checksum of the manifest file
        """
        manifest_path = join(manifest_dir, manifest_name)
        return ChecksumUtil._create_sum_from_file(manifest_path)

    @staticmethod
    def _create_sum_setup(plugin_dir: str, setup_file_name: str = "setup.py"):
        """
        Produce the checksum for the plugin's Python setup file, usually plugin_dir/
        :param plugin_dir: The path to the plugin's Python setup file, usually root of plugin_dir/
        :param setup_file_name: The name of the plugin's Python setup file, usually setup.py
        :return: The MD5 checksum of the Python setup file
        """
        setup_path = join(plugin_dir, setup_file_name)
        return ChecksumUtil._create_sum_from_file(setup_path)

    @staticmethod
    def _create_sum_schemas(plugin_dir: str, spec: PluginSpecTypes.Spec) -> List[Dict]:
        """
        Produce a list of checksums for every schema file in this plugin.
        Each list entry is a 2-key JSON object containing identifier and hash.
        The object identifier is the schema file's immediate parent directory and file name.
        List must be in lexical order of the full file paths from the plugin_dir root.

        Note that identifiers may not appear to be in lexical order, for example, all actions will precede connection.
        This would still be in lexical order, even though identifiers cut off directory paths beyond the direct parent.
        :param plugin_dir: The path to the plugin's source code that contains schema.py files
        :return: A list of objects containing all schema.py files and their corresponding MD5 checksums
        """
        result = []

        using_icon = False
        komand_path = join(
            plugin_dir, KOMAND_PREFIX + "_" + spec.get(PluginSpecConstants.NAME)
        )
        icon_path = join(
            plugin_dir, BASE_PREFIX + "_" + spec.get(PluginSpecConstants.NAME)
        )

        # Check if icon naming scheme is being used
        if isdir(icon_path):
            using_icon = True

        if isdir(komand_path) or isdir(icon_path):
            # Traverse all files/directories in the plugin directory looking for schema.py files to hash
            for root, dirs, files in walk(icon_path if using_icon else komand_path):
                # By sorting dirs upon each loop, we consistently traverse the tree in lexical (alphabetical) order
                dirs.sort()
                for file_name in files:
                    if file_name == "schema.py":
                        # Identifier is "parent_directory/schema.py" where parent directory is name of the
                        # action/trigger
                        result.append(
                            {
                                "identifier": f"{join(basename(root), file_name)}",
                                "hash": ChecksumUtil._create_sum_from_file(
                                    join(root, file_name)
                                ),
                            }
                        )
        return result

    @staticmethod
    def create_checksums(
        plugin_dir: str, spec: PluginSpecTypes.Spec, base_prefix: str = BASE_PREFIX
    ) -> str:
        """
        Creates the checksums for the plugin.
        :param plugin_dir: The absolute path to the plugin directory root
        :param spec: The plugin spec dictionary, only used to get the plugin name
        :param base_prefix: Prefix for manifest file name, usually icon, older plugins may use komand
        :return: The complete checksums JSON object as a string
        """
        result = {
            "spec": ChecksumUtil._create_sum_spec(plugin_dir),
            "manifest": ChecksumUtil._create_sum_manifest(
                join(plugin_dir, PluginSpecConstants.MANIFEST),
                f'{base_prefix}_{spec.get("name")}',
            ),
            "setup": ChecksumUtil._create_sum_setup(plugin_dir),
            "schemas": ChecksumUtil._create_sum_schemas(plugin_dir, spec),
        }
        return json.dumps(result, indent="\t")
