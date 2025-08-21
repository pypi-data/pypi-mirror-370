#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import base64
import json

import requests
from osdu_api.providers.types import BaseCredentials
from requests import HTTPError

from osducli.log import get_logger

logger = get_logger(__name__)


class AwsTokenCredential(BaseCredentials):
    """AWS token based client for connecting with OSDU."""

    __access_token = None

    def __init__(
            self,
            client_id: str,
            client_secret: str,
            token_url: str,
            oauth_custom_scope: str,
    ):
        super().__init__()
        self._client_id = client_id
        self._client_secret = client_secret
        self._token_url = token_url
        self._oauth_custom_scope = oauth_custom_scope

    @property
    def access_token(self) -> str:
        return self.__access_token

    def refresh_token(self) -> str:
        self.__access_token = self._get_service_principal_token()
        return self.__access_token

    def _get_service_principal_token(self) -> str:
        auth = f'{self._client_id}:{self._client_secret}'
        encoded_auth = base64.b64encode(str.encode(auth))

        headers = {
            'Authorization': 'Basic ' + encoded_auth.decode(),
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        data = {
            "grant_type": "client_credentials",
            "scope": self._oauth_custom_scope
        }
        try:
            response = requests.post(url=self._token_url, headers=headers, data=data, timeout=10)
            return json.loads(response.content.decode())['access_token']
        except HTTPError as ex:
            code = ex.response.status_code
            message = ex.response.content.decode()
            logger.error("Refresh token request failed. %s %s", code, message)
            raise
