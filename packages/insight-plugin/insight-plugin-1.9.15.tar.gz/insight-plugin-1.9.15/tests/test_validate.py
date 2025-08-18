from unittest import TestCase
import sys
import os

sys.path.append(os.path.abspath("../"))

from insight_plugin.features.validate.controller import ValidateController
from tests import TEST_RESOURCES


class TestValidate(TestCase):
    def test_validate_plugin_fail(self):
        validate_feature = ValidateController.new_from_cli(
            spec_path=f"{TEST_RESOURCES}/test_base64/base64",
        )
        response_status = validate_feature.validate()
        self.assertEqual(True, response_status)
