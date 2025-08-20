import unittest

from zoho_somconnexio_python_client.exceptions import ZohoCRMClientException
from zoho_somconnexio_python_client.utils.client_utils import (
    check_params,
    check_payload,
)


class ClientUtilsTestCase(unittest.TestCase):
    def test_check_params_ok(self):
        params = {"test": "test"}
        self.assertEqual(check_params(params), params)

    def test_check_params_none(self):
        self.assertEqual(check_params(None), {})

    def test_check_payload_list(self):
        self.assertEqual(check_payload(["test"]), {"data": ["test"]})

    def test_check_payload_dict(self):
        self.assertEqual(check_payload({"test": "test"}), {"data": [{"test": "test"}]})

    def test_check_payload_exception(self):
        self.assertRaisesRegex(
            ZohoCRMClientException, "Invalid payload data", check_payload, "test"
        )
