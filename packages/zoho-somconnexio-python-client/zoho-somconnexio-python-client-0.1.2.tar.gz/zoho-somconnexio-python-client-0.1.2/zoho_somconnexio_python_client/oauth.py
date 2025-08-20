import os
import tempfile
import json
from time import time
import requests as req

from typing import Optional

from zoho_somconnexio_python_client.exceptions import ErrorCreatingSession


class ZohoCRMOauth:
    OAUTH_URL = "https://accounts.zoho.eu/oauth/v2/token"

    def __init__(self, scope: str) -> None:
        self.client_id = self._client_id()
        self.client_secret = self._client_secret()
        self.organization_id = self._organization_id()
        self.scope = scope
        self.token_store = os.path.join(
            self._crm_store(), "{}.json".format(scope.replace(".", "_").lower())
        )

    @staticmethod
    def _client_id():
        return os.environ.get("ZOHO_CRM_CLIENT_ID", "")

    @staticmethod
    def _client_secret():
        return os.environ.get("ZOHO_CRM_CLIENT_SECRET", "")

    @staticmethod
    def _organization_id():
        return os.environ.get("ZOHO_CRM_ORGANIZATION_ID", "")

    @staticmethod
    def _crm_store():
        path = os.environ.get("ZOHO_CRM_STORE", tempfile.gettempdir())

        if not os.path.isdir(path):
            os.mkdir(path)

        return path

    def _get_token_from_store(self) -> Optional[dict]:
        """
        Gets access token from the local store if it exists and is not outdated
        """

        if not os.path.isfile(self.token_store):
            return None

        with open(self.token_store, "r", encoding="utf-8") as fp:
            try:
                token = json.load(fp)

                if token["expires_at"] < time():
                    return None

                if token["scope"] != self.scope:
                    return None

                return token
            except json.decoder.JSONDecodeError:
                return None

    def _oauth_request_token(self) -> dict:
        """
        Use the client credentials to get access token from Zoho OAuth server
        """
        res = req.post(
            self.OAUTH_URL,
            params={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "soid": "ZohoCRM." + self.organization_id,
                "grant_type": "client_credentials",
                "scope": self.scope,
            },
        )

        if res.status_code >= 400:
            raise ErrorCreatingSession(res.status_code, res.text)

        data = res.json()

        if data.get("error"):
            raise ErrorCreatingSession(400, data["error"])

        return data

    def get_token(self) -> dict:
        """
        Gets the Zoho API access token using the store to make it persistent
        """

        token = self._get_token_from_store()

        if not token:
            token = self._oauth_request_token()
            token["expires_at"] = int(time()) + int(token["expires_in"])

            with open(self.token_store, "w", encoding="utf-8") as fp:
                json.dump(token, fp)

        return token
