import unittest
from mock import patch

from test.utilities import FakeResponse
from zoho_somconnexio_python_client.client import ZohoCRMClient
from zoho_somconnexio_python_client.exceptions import (
    CRMNotCreated,
    CRMNotDeleted,
    CRMNotFoundError,
    CRMNotUpdated,
)


@patch("zoho_somconnexio_python_client.client.ZohoCRMOauth.__init__", return_value=None)
@patch(
    "zoho_somconnexio_python_client.client.ZohoCRMOauth.get_token",
    return_value={"access_token": "token"},
)
class ClientTestCase(unittest.TestCase):
    def setUp(self):
        self.params = {"param": "test"}
        self.data = "data"
        self.endpoint = "/endpoint"

    """
        test get
    """

    @patch(
        "zoho_somconnexio_python_client.client.req.request",
        return_value=FakeResponse(),
    )
    def test_get_ok(self, mock_request, mock_token, mock_parent):
        self.assertEqual(
            ZohoCRMClient().get(self.endpoint, self.params),
            FakeResponse().json(),
        )
        mock_request.assert_called_once_with(
            "GET",
            "https://www.zohoapis.eu/crm/v7" + self.endpoint,
            headers={
                "Authorization": "Zoho-oauthtoken token",
                "Accept": "application/json",
            },
            json=None,
            params=self.params,
        )
        mock_parent.assert_called_once_with("ZohoCRM.modules.ALL")
        mock_token.assert_called_once()

    @patch(
        "zoho_somconnexio_python_client.client.req.get",
        return_value=FakeResponse(404),
    )
    def test_get_ko(self, _, __, ___):
        msg = "Error searching with the next error message:"
        self.assertRaisesRegex(
            CRMNotFoundError,
            msg,
            ZohoCRMClient().get,
            self.endpoint,
            self.params,
        )

    """
        test post
    """

    @patch(
        "zoho_somconnexio_python_client.client.check_payload",
        return_value="payload",
    )
    @patch(
        "zoho_somconnexio_python_client.client.req.request",
        return_value=FakeResponse(),
    )
    def test_post_ok(self, mock_request, mock_payload, mock_token, mock_parent):
        self.assertEqual(
            ZohoCRMClient().post(self.endpoint, self.data, self.params),
            FakeResponse().json(),
        )
        mock_request.assert_called_once_with(
            "POST",
            "https://www.zohoapis.eu/crm/v7" + self.endpoint,
            headers={
                "Authorization": "Zoho-oauthtoken token",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            json="payload",
            params=self.params,
        )
        mock_payload.assert_called_once_with(self.data)
        mock_parent.assert_called_once_with("ZohoCRM.modules.ALL")
        mock_token.assert_called_once()

    @patch("zoho_somconnexio_python_client.client.check_payload")
    @patch(
        "zoho_somconnexio_python_client.client.req.request",
        return_value=FakeResponse(500),
    )
    def test_post_ko(self, _, __, ___, ____):
        msg = "Error creating with the next error message:"
        self.assertRaisesRegex(
            CRMNotCreated,
            msg,
            ZohoCRMClient().post,
            self.endpoint,
            self.data,
            self.params,
        )

    """
        test put
    """

    @patch(
        "zoho_somconnexio_python_client.client.check_payload",
        return_value="payload",
    )
    @patch(
        "zoho_somconnexio_python_client.client.req.request",
        return_value=FakeResponse(),
    )
    def test_put_ok(self, mock_request, mock_payload, mock_token, mock_parent):
        self.assertEqual(
            ZohoCRMClient().put(self.endpoint, self.data, self.params),
            FakeResponse().json(),
        )
        mock_request.assert_called_once_with(
            "PUT",
            "https://www.zohoapis.eu/crm/v7" + self.endpoint,
            headers={
                "Authorization": "Zoho-oauthtoken token",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            json="payload",
            params=self.params,
        )
        mock_payload.assert_called_once_with(self.data)
        mock_parent.assert_called_once_with("ZohoCRM.modules.ALL")
        mock_token.assert_called_once()

    @patch("zoho_somconnexio_python_client.client.check_payload")
    @patch(
        "zoho_somconnexio_python_client.client.req.request",
        return_value=FakeResponse(500),
    )
    def test_put_ko(self, _, __, ___, ____):
        msg = "Error updating with the next error message:"
        self.assertRaisesRegex(
            CRMNotUpdated,
            msg,
            ZohoCRMClient().put,
            self.endpoint,
            self.data,
            self.params,
        )

    """
        test delete
    """

    @patch(
        "zoho_somconnexio_python_client.client.req.request",
        return_value=FakeResponse(),
    )
    def test_delete_ok(self, mock_delete, mock_token, mock_parent):
        self.assertEqual(
            ZohoCRMClient().delete(self.endpoint, self.params),
            FakeResponse().json(),
        )
        mock_delete.assert_called_once_with(
            "DELETE",
            "https://www.zohoapis.eu/crm/v7" + self.endpoint,
            headers={
                "Authorization": "Zoho-oauthtoken token",
                "Accept": "application/json",
            },
            json=None,
            params=self.params,
        )
        mock_parent.assert_called_once_with("ZohoCRM.modules.ALL")
        mock_token.assert_called_once()

    @patch(
        "zoho_somconnexio_python_client.client.req.request",
        return_value=FakeResponse(500),
    )
    def test_delete_ko(self, _, __, ___):
        msg = "Error deleting with the next error message:"
        self.assertRaisesRegex(
            CRMNotDeleted,
            msg,
            ZohoCRMClient().delete,
            self.endpoint,
            self.params,
        )
