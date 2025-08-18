import unittest
import sys
import os

sys.path.append(os.path.abspath("../"))

from insight_plugin.features.common.exceptions import InsightException
from insight_plugin import BASE_PREFIX, FILE_ENCODING
from insight_plugin.features.common.checksum_util import ChecksumUtil
from insight_plugin.features.common.plugin_spec_util import (
    PluginSpecConstants,
    PluginSpecUtil,
)
from tests import TEST_RESOURCES

plugin_dir_base_64 = os.path.join(TEST_RESOURCES, "test_base64/base64")


class TestChecksum(unittest.TestCase):
    @staticmethod
    def get_checksum(plugin_dir: str, prefix: str):
        plugin_spec_filename = os.path.join(plugin_dir, PluginSpecConstants.FILENAME)
        plugin_spec = PluginSpecUtil.get_spec_file(plugin_spec_filename)
        return ChecksumUtil.create_checksums(
            plugin_dir, plugin_spec, base_prefix=prefix
        )

    @staticmethod
    def get_expected(plugin_dir: str):
        with open(
            os.path.join(plugin_dir, ".CHECKSUM"), "r", encoding=FILE_ENCODING
        ) as expected_file:
            return expected_file.read()

    def test_create_sum_from_file(self):
        input_file = os.path.join(plugin_dir_base_64, "extension.png")
        result = ChecksumUtil._create_sum_from_file(input_file)
        self.assertEqual(result, "e41a1513ef7eb7d68193d6f25ebadf12")

    def test_checksum_plugin(self):
        expected = TestChecksum.get_expected(plugin_dir_base_64)
        result = TestChecksum.get_checksum(plugin_dir_base_64, prefix=BASE_PREFIX)
        self.assertEqual(expected, result)

    def test_no_checksum_from_file(self):
        with self.assertRaises(InsightException) as context:
            ChecksumUtil._create_sum_from_file(
                os.path.join(plugin_dir_base_64, "file.txt")
            )
        self.assertEqual(
            context.exception.troubleshooting,
            "Verify that the target is real and is a file.",
        )
