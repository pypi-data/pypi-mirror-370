from unittest import TestCase
import logging

from resources.export_test_base64.komand_base64.actions import Encode


class TestEncode(TestCase):
    def test_encode(self):
        test_encoder = Encode()
        log = logging.getLogger("Test")
        test_encoder.logger = log

        input_params = {"content": "Rapid7"}

        results = test_encoder.run(input_params)
        self.assertEqual("UmFwaWQ3", results.get("data"))
