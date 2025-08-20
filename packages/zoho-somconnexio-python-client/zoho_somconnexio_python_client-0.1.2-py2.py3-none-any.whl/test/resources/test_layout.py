import os
import json
import unittest
import time
from mock import patch, mock_open, call

from test.utilities import FakeResponse
from zoho_somconnexio_python_client.resources.layout import ZohoCRMLayout

CRM_STORE = "path_store"


@patch.dict(
    os.environ,
    {
        "ZOHO_CRM_STORE": CRM_STORE,
    },
)
@patch(
    "zoho_somconnexio_python_client.resources.layout.ZohoCRMClient.__init__",
    return_value=None,
)
class ZohoCRMLayoutTestCase(unittest.TestCase):
    def setUp(self):
        self.module = "module"
        self.stored_layout_test = {
            "module": {
                "__time": time.time(),
            }
        }
        self.path_stored = CRM_STORE + "/layouts.json"

    """
        test _get_layout_from_store
    """

    @patch("os.path.isfile", return_value=False)
    def test_get_layout_from_store_not_file(self, _, __):
        self.assertEqual(ZohoCRMLayout(self.module)._get_layout_from_store(), None)

    @patch("os.path.isfile", return_value=True)
    @patch("builtins.open", new_callable=mock_open)
    def test_get_layout_from_store_ok(self, mock_file, _, __):
        mock_file.return_value.__enter__.return_value.read.return_value = json.dumps(
            self.stored_layout_test
        )

        self.assertEqual(
            ZohoCRMLayout(self.module)._get_layout_from_store(),
            self.stored_layout_test["module"],
        )

        mock_file.assert_called_with(self.path_stored, "r", encoding="utf-8")

    @patch("os.path.isfile", return_value=True)
    @patch("builtins.open", new_callable=mock_open)
    def test_get_layout_from_store_expired(self, mock_file, _, __):
        expired_layout = {**self.stored_layout_test}
        expired_layout["module"]["__time"] = time.time() - 3610
        mock_file.return_value.__enter__.return_value.read.return_value = json.dumps(
            expired_layout
        )
        self.assertEqual(ZohoCRMLayout(self.module)._get_layout_from_store(), None)

    @patch("os.path.isfile", return_value=True)
    @patch("builtins.open", new_callable=mock_open)
    def test_get_layout_from_store_bad_module(self, mock_file, _, __):
        mock_file.return_value.__enter__.return_value.read.return_value = json.dumps(
            {"other_module": {}}
        )
        self.assertEqual(ZohoCRMLayout(self.module)._get_layout_from_store(), None)

    """
        test _layout_request_token
    """

    @patch(
        "zoho_somconnexio_python_client.resources.layout.ZohoCRMLayout.get",
        return_value=FakeResponse(
            content='{"layouts": [{"sections": [{"fields": ["field"]}]}]}'
        ).json(),
    )
    def test_layout_request_token(self, mock_get, _):
        result = ZohoCRMLayout(self.module)._layout_request_token()

        self.assertEqual(
            result["sections"],
            [{"fields": ["field"]}],
        )

        self.assertIsInstance(result["__time"], int)

        mock_get.assert_called_once_with("/settings/layouts", {"module": self.module})

    """
        test get_layout
    """

    @patch(
        "zoho_somconnexio_python_client.resources.layout.ZohoCRMLayout._get_layout_from_store",
        return_value={"sections": [{"fields": ["field"]}]},
    )
    def test_get_layout_without_request(self, _, mock_parent):
        self.assertEqual(["field"], ZohoCRMLayout(self.module).fields)
        mock_parent.assert_called_once_with("ZohoCRM.settings.layouts.READ")

    @patch(
        "zoho_somconnexio_python_client.resources.layout.ZohoCRMLayout._get_layout_from_store",
        return_value=None,
    )
    @patch(
        "zoho_somconnexio_python_client.resources.layout.ZohoCRMLayout._layout_request_token",
        return_value={"sections": [{"fields": ["field"]}]},
    )
    @patch("os.path.isfile", return_value=True)
    @patch("builtins.open", new_callable=mock_open)
    def test_get_layout_requested(self, mock_file, _, __, ___, ____):
        mock_file.return_value.__enter__.return_value.read.return_value = json.dumps(
            {self.module: "module"}
        )
        self.assertEqual(["field"], ZohoCRMLayout(self.module).fields)
        mock_file.assert_has_calls(
            [
                call(self.path_stored, "r", encoding="utf-8"),
                call(self.path_stored, "w", encoding="utf-8"),
            ],
            any_order=True,
        )

    @patch(
        "zoho_somconnexio_python_client.resources.layout.ZohoCRMLayout._get_layout_from_store",
        return_value=None,
    )
    @patch(
        "zoho_somconnexio_python_client.resources.layout.ZohoCRMLayout._layout_request_token",
        return_value={"sections": [{"fields": ["field"]}]},
    )
    @patch("os.path.isfile", return_value=False)
    @patch("builtins.open", new_callable=mock_open)
    def test_get_layout_requested_variant(self, mock_file, _, __, ___, ____):
        mock_file.return_value.__enter__.return_value.read.return_value = json.dumps(
            {self.module: "module"}
        )
        self.assertEqual(["field"], ZohoCRMLayout(self.module).fields)
        mock_file.assert_called_with(self.path_stored, "w", encoding="utf-8")
