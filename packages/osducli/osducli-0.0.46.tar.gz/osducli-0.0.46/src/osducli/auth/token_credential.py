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

from datetime import datetime
from json import loads
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from osdu_api.providers.types import BaseCredentials

from osducli.log import get_logger

logger = get_logger(__name__)


class TokenCredential(BaseCredentials):
    """Refresh token based client for connecting with OSDU."""

    __access_token_expire_date = 0
    __access_token = None

    def __init__(
        self,
        client_id: str,
        token_endpoint: str,
        refresh_token: str,
        client_secret: str,
    ):
        """Setup the new client

        Args:
            client_id (str): client id for connecting
            token_endpoint (str): token endpoint for refreshing token
            refresh_token (str): refresh token
            client_secret (str): client secret
        """
        super().__init__()
        self._client_id = client_id
        self._token_endpoint = token_endpoint
        self._refresh_token = refresh_token
        self._client_secret = client_secret

    @property
    def access_token(self) -> str:
        """
        Check expiration date and return access_token.
        """
        if datetime.now().timestamp() > self.__access_token_expire_date:
            self.refresh_token()
        return self.__access_token

    def _refresh_access_token(self) -> dict:
        """
        Send refresh token requests to OpenID token endpoint.

        Return dict with keys "access_token", "expires_in", "scope", "token_type", "id_token".
        """
        body = {
            "grant_type": "refresh_token",
            "refresh_token": self._refresh_token,
            "client_id": self._client_id,
            "client_secret": self._client_secret,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = urlencode(body).encode("utf8")
        request = Request(url=self._token_endpoint, data=data, headers=headers)
        try:
            with urlopen(request) as response:
                response_body = response.read()
                return loads(response_body)
        except HTTPError as ex:
            code = ex.code
            message = ex.read().decode("utf8")
            logger.error("Refresh token request failed. %s %s", code, message)
            raise

    def refresh_token(self) -> str:
        """Refresh from refresh token.

        Returns:
            dict: Dictionary representing the returned token
        """
        result = self._refresh_access_token()

        if "access_token" in result:
            self.__access_token = result["access_token"]
            self.__access_token_expire_date = datetime.now().timestamp() + result["expires_in"]

        else:
            print(result.get("error"))
            print(result.get("error_description"))
            print(result.get("correlation_id"))

        return self.__access_token
