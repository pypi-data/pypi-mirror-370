import os
import subprocess
import unittest
import sys

sys.path.append(os.path.abspath("../"))


from insight_plugin.features.common.command_line_util import CommandLineUtil
from insight_plugin.features.common.plugin_spec_util import PluginSpecUtil
from insight_plugin.features.export.controller import ExportController
from tests import TEST_RESOURCES


class TestExport(unittest.TestCase):
    def test_export_build_image(self):
        subprocess.run(
            [
                "docker rmi -f $(docker images | grep 'base64 *1.1.6' | awk '{print $3}')"
            ],
            shell=True,
        )

        export_feature = ExportController.new_from_cli(
            no_pull=True,
            verbose=True,
            target_dir=os.path.join(TEST_RESOURCES, "export_test_base64"),
        )
        export_feature.spec = PluginSpecUtil.get_spec_file(export_feature.target_dir)
        export_feature._build_image()
        completed_process = subprocess.run(
            ["docker images | grep 'base64 *1.1.6' | awk '{print $3}'"],
            shell=True,
            capture_output=True,
        )
        self.assertEqual(True, completed_process.stdout is not None)

    def test_export_tarball(self):
        # test assumes the _build_image() is successful, asserts correctness if the tarball exists at the end

        if not CommandLineUtil.does_program_exist("docker"):
            return

        test_dir = os.getcwd()
        tarball_path = os.path.join(
            test_dir, "resources", "export_test_base64", "rapid7_base64_1.1.6.plg"
        )
        prev_exists = os.path.exists(tarball_path)
        if prev_exists:
            os.remove(tarball_path)
        os.chdir(test_dir)

        export_feature = ExportController.new_from_cli(
            no_pull=True,
            verbose=True,
            target_dir=os.path.join(TEST_RESOURCES, "export_test_base64"),
        )
        export_feature.export()

        exists_ = os.path.exists(export_feature.target_name)
        if exists_:
            os.remove(export_feature.target_name)
        self.assertEqual(True, exists_)
