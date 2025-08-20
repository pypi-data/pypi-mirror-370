import os
import json
import unittest
import time
from mock import patch, mock_open

from test.utilities import FakeResponse
from zoho_somconnexio_python_client.exceptions import ErrorCreatingSession
from zoho_somconnexio_python_client.oauth import ZohoCRMOauth


CLIENT_ID = "client_id"
CLIENT_SECRET = "client_secret"
ORGANIZATION_ID = "organization_id"
CRM_STORE = "path_store"


@patch.dict(
    os.environ,
    {
        "ZOHO_CRM_CLIENT_ID": CLIENT_ID,
        "ZOHO_CRM_CLIENT_SECRET": CLIENT_SECRET,
        "ZOHO_CRM_ORGANIZATION_ID": ORGANIZATION_ID,
        "ZOHO_CRM_STORE": CRM_STORE,
    },
)
class ZohoCRMOauthTestCase(unittest.TestCase):
    def setUp(self):
        self.scope = "scope"
        self.token_test = {
            "expires_at": time.time() + 3600,
            "scope": self.scope,
        }
        self.path_stored = CRM_STORE + "/" + self.scope + ".json"

    """
        test _get_token_from_store
    """

    @patch("os.path.isfile", return_value=False)
    def test_get_token_from_store_not_file(self, mock_isfile):
        self.assertEqual(ZohoCRMOauth(self.scope)._get_token_from_store(), None)
        mock_isfile.assert_called_with(self.path_stored)

    @patch("os.path.isfile", return_value=True)
    @patch("builtins.open", new_callable=mock_open)
    def test_get_token_from_store_ok(self, mock_file, _):
        mock_file.return_value.__enter__.return_value.read.return_value = json.dumps(
            self.token_test
        )
        self.assertEqual(
            ZohoCRMOauth(self.scope)._get_token_from_store(), self.token_test
        )
        mock_file.assert_called_with(self.path_stored, "r", encoding="utf-8")

    @patch("os.path.isfile", return_value=True)
    @patch("builtins.open", new_callable=mock_open)
    def test_get_token_from_store_expired(self, mock_file, _):
        expired_token = self.token_test
        expired_token["expires_at"] = time.time() - 3600
        mock_file.return_value.__enter__.return_value.read.return_value = json.dumps(
            expired_token
        )
        self.assertEqual(ZohoCRMOauth(self.scope)._get_token_from_store(), None)

    @patch("os.path.isfile", return_value=True)
    @patch("builtins.open", new_callable=mock_open)
    def test_get_token_from_store_bad_scope(self, mock_file, _):
        expired_token = self.token_test
        expired_token["scope"] = "other"
        mock_file.return_value.__enter__.return_value.read.return_value = json.dumps(
            expired_token
        )
        self.assertEqual(ZohoCRMOauth(self.scope)._get_token_from_store(), None)

    """
        test _oauth_request_token
    """

    @patch(
        "zoho_somconnexio_python_client.oauth.req.post",
        return_value=FakeResponse(),
    )
    def test_oauth_request_token_ok(self, mock_post):
        self.assertEqual(
            ZohoCRMOauth(self.scope)._oauth_request_token(), {"test": "ok"}
        )
        mock_post.assert_called_with(
            "https://accounts.zoho.eu/oauth/v2/token",
            params={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "soid": "ZohoCRM." + ORGANIZATION_ID,
                "grant_type": "client_credentials",
                "scope": self.scope,
            },
        )

    @patch(
        "zoho_somconnexio_python_client.oauth.req.post",
        return_value=FakeResponse(404),
    )
    def test_oauth_request_token_400(self, mock_post):
        msg = "Error creating the session with the next error message: {}".format(
            mock_post.return_value.text
        )
        self.assertRaisesRegex(
            ErrorCreatingSession,
            msg,
            ZohoCRMOauth(self.scope)._oauth_request_token,
        )

    @patch(
        "zoho_somconnexio_python_client.oauth.req.post",
        return_value=FakeResponse(content='{"error": "ko"}'),
    )
    def test_oauth_request_token_error(self, mock_post):
        msg = "Error creating the session with the next error message: {}".format(
            mock_post.return_value.json()["error"]
        )
        self.assertRaisesRegex(
            ErrorCreatingSession,
            msg,
            ZohoCRMOauth(self.scope)._oauth_request_token,
        )

    """
        test get_token
    """

    @patch(
        "zoho_somconnexio_python_client.client.ZohoCRMOauth._get_token_from_store",
        return_value="token",
    )
    def test_get_token_stored(self, _):
        self.assertEqual(ZohoCRMOauth(self.scope).get_token(), "token")

    @patch(
        "zoho_somconnexio_python_client.client.ZohoCRMOauth._get_token_from_store",
        return_value=None,
    )
    @patch(
        "zoho_somconnexio_python_client.client.ZohoCRMOauth._oauth_request_token",
        return_value={"expires_at": "", "expires_in": "0"},
    )
    @patch("builtins.open", new_callable=mock_open)
    def test_get_token_request(
        self, mock_file, mock_auth_request, mock_token_from_store
    ):
        result = ZohoCRMOauth(self.scope).get_token()
        self.assertEqual(result["expires_in"], "0")
        self.assertIsInstance(result["expires_at"], int)
        mock_file.assert_called_once_with(self.path_stored, "w", encoding="utf-8")
        mock_auth_request.assert_called_once()
        mock_token_from_store.assert_called_once()
