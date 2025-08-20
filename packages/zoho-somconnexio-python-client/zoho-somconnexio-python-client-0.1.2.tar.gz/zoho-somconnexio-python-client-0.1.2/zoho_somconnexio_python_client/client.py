# built-in
from typing import Optional

# vendor
import requests as req

from zoho_somconnexio_python_client.exceptions import (
    CRMNotCreated,
    CRMNotDeleted,
    CRMNotFoundError,
    CRMNotUpdated,
)
from zoho_somconnexio_python_client.oauth import ZohoCRMOauth
from zoho_somconnexio_python_client.utils.client_utils import (
    check_payload,
)


class ZohoCRMClient(ZohoCRMOauth):
    """Base Zoho CRM API client"""

    API_URL = "https://www.zohoapis.eu/crm/v7"

    def __init__(self, scope: str = "ZohoCRM.modules.ALL") -> None:
        """Initializes the oauth"""
        super(ZohoCRMClient, self).__init__(scope)

    def get(self, endpoint: str, params: Optional[dict] = None) -> dict:
        res = self._send_request(verb="GET", url=self.API_URL + endpoint, params=params)

        if res.status_code >= 400:
            raise CRMNotFoundError(res.status_code, res.text, params)

        return res.json()

    def post(self, endpoint: str, data: dict, params: Optional[dict] = None) -> dict:
        res = self._send_request(
            verb="POST",
            url=self.API_URL + endpoint,
            params=params,
            payload=data,
            extra_headers={"Content-Type": "application/json"},
        )
        if res.status_code >= 400:
            raise CRMNotCreated(res.status_code, res.text)

        return res.json()

    def put(self, endpoint: str, data: dict, params: Optional[dict] = None) -> dict:
        res = self._send_request(
            verb="PUT",
            url=self.API_URL + endpoint,
            params=params,
            payload=data,
            extra_headers={"Content-Type": "application/json"},
        )

        if res.status_code >= 400:
            raise CRMNotUpdated(res.status_code, res.text)

        return res.json()

    def delete(self, endpoint: str, params: Optional[dict] = None):
        res = self._send_request(
            verb="DELETE", url=self.API_URL + endpoint, params=params
        )

        if res.status_code >= 400:
            raise CRMNotDeleted(res.status_code, res.text)

        return res.json()

    def _send_request(
        self,
        verb,
        url,
        payload=None,
        params={},
        extra_headers={},
    ):
        token = self.get_token()
        headers = {
            "Authorization": "Zoho-oauthtoken {0}".format(token["access_token"]),
            "Accept": "application/json",
        }

        if extra_headers:
            headers.update(extra_headers)
        if payload:
            payload = check_payload(payload)

        return req.request(
            verb.upper(), url, headers=headers, json=payload, params=params
        )
