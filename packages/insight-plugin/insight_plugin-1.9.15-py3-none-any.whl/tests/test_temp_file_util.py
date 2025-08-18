import unittest
import sys
import os

sys.path.append(os.path.abspath("../"))
from insight_plugin.features.common.temp_file_util import SafeTempDirectory


class TestSafeTempDirectory(unittest.TestCase):
    def test_create_files(self):
        pass

    def test_execute_safe_dir(self):
        SafeTempDirectory.execute_safe_dir(
            func=TestSafeTempDirectory.test_create_files, target_dir="", overwrite=False
        )
