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

from msal import ConfidentialClientApplication
from osdu_api.providers.types import BaseCredentials

from osducli.log import get_logger

logger = get_logger(__name__)


class MsalNonInteractiveCredential(BaseCredentials):
    """Get token based client for connecting with OSDU."""

    _access_token = None

    def __init__(self,
                 client_id: str,
                 client_secret: str,
                 authority: str,
                 scopes: str):
        """Setup the new client

        Args:
            client_id (str): client id for connecting
            authority (str): authority url
            scopes (str): scopes to request
        """
        super().__init__()
        self._client_id = client_id
        self._client_secret = client_secret
        self._authority = authority
        self._scopes = scopes
        self._app = ConfidentialClientApplication(
            self._client_id, self._client_secret, self._authority
        )

    @property
    def access_token(self) -> str:
        return self._access_token

    def refresh_token(self) -> str:
        """
        return access_token.
        """
        response = self._app.acquire_token_for_client(scopes=[self._scopes])
        if 'access_token' in response:
            self._access_token = response['access_token']
        else:
            raise Exception("Failed to aquire token")

        return self._access_token
