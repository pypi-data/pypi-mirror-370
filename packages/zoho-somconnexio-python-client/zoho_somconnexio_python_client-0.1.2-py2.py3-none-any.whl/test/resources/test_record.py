import unittest
from mock import patch, Mock

from zoho_somconnexio_python_client.resources.record import ZohoCRMRecord

test_layout_fields = [
    {
        "api_name": "status",
        "data_type": "picklist",
        "pick_list_values": [
            {
                "display_value": "Open",
                "reference_value": "OPEN",
                "actual_value": "open",
            },
            {
                "display_value": "Closed",
                "reference_value": "CLOSED",
                "actual_value": "closed",
            },
        ],
    },
    {
        "api_name": "priority",
        "data_type": "text",
        "pick_list_values": [],
    },
]


@patch(
    "zoho_somconnexio_python_client.resources.record.ZohoCRMClient.__init__",
    return_value=Mock(),
)
class ZohoCRMRecordTestCase(unittest.TestCase):
    def setUp(self):
        self.module = "module"

    @patch(
        "zoho_somconnexio_python_client.resources.record.ZohoCRMRecord.delete",
        return_value="ok",
    )
    def test_drop(self, mock_delete, mock_parent):
        self.assertEqual(ZohoCRMRecord(self.module).drop("id"), "ok")
        mock_delete.assert_called_once_with("/" + self.module, params={"ids": "id"})
        mock_parent.assert_called_once()

    @patch(
        "zoho_somconnexio_python_client.resources.record.ZohoCRMRecord.get",
        return_value="ok",
    )
    def test_list(self, mock_get, mock_parent):
        self.assertEqual(ZohoCRMRecord(self.module).list(["field"]), "ok")
        mock_get.assert_called_once_with(
            "/" + self.module, {"fields": "field", "page": 1, "per_page": 20}
        )
        mock_parent.assert_called_once()

    @patch(
        "zoho_somconnexio_python_client.resources.record.ZohoCRMRecord.put",
        return_value={"data": ["ok"]},
    )
    @patch(
        "zoho_somconnexio_python_client.resources.record.ZohoCRMRecord._layout_sanitization",
        return_value={},
    )
    def test_write(self, mock_sanitization, mock_put, mock_parent):
        self.assertEqual(ZohoCRMRecord(self.module).write("id", {"data": "test"}), "ok")
        mock_put.assert_called_once_with("/" + self.module + "/id", data={"id": "id"})
        mock_sanitization.assert_called_once_with({"data": "test"})
        mock_parent.assert_called_once()

    @patch(
        "zoho_somconnexio_python_client.resources.record.ZohoCRMRecord.post",
        return_value={"data": ["ok"]},
    )
    @patch(
        "zoho_somconnexio_python_client.resources.record.ZohoCRMRecord._layout_sanitization",
        return_value={"data": "test"},
    )
    def test_create_upsert(self, mock_sanitization, mock_post, mock_parent):
        self.assertEqual(
            ZohoCRMRecord(self.module).create({"data": "test"}, upsert=True), "ok"
        )

        mock_post.assert_called_once_with(
            "/" + self.module + "/upsert", data={"data": "test"}
        )

        mock_sanitization.assert_called_once_with({"data": "test"})
        mock_parent.assert_called_once()

    @patch(
        "zoho_somconnexio_python_client.resources.record.ZohoCRMRecord._layout_sanitization",
        return_value={},
    )
    @patch(
        "zoho_somconnexio_python_client.resources.record.ZohoCRMRecord.post",
        return_value={"data": ["ok"]},
    )
    def test_create(self, _, __, ___):
        self.assertEqual(
            ZohoCRMRecord(self.module).create({"data": "test"}, False), "ok"
        )

    @patch("zoho_somconnexio_python_client.resources.record.ZohoCRMLayout")
    def test_layout_sanitization_invalid_picklist_value(self, mock_layout, _):
        mock_layout_instance = mock_layout.return_value
        mock_layout_instance.fields = test_layout_fields
        data = {"status": "In Progress"}
        expected = {}
        self.assertEqual(
            ZohoCRMRecord(self.module)._layout_sanitization(data), expected
        )
        mock_layout.assert_called_once_with(self.module)

    @patch("zoho_somconnexio_python_client.resources.record.ZohoCRMLayout")
    def test_layout_sanitization_mixed_fields(self, mock_layout, _):
        mock_layout_instance = mock_layout.return_value
        mock_layout_instance.fields = test_layout_fields
        data = {
            "status": "closed",  # valid actual_value
            "priority": "High",  # valid non-picklist
            "unknown": "xxx",  # not in layout
            "status2": "Open",  # not in layout
        }
        expected = {
            "status": "closed",
            "priority": "High",
        }
        self.assertEqual(
            ZohoCRMRecord(self.module)._layout_sanitization(data), expected
        )
        mock_layout.assert_called_once_with(self.module)
