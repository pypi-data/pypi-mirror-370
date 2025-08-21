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
import os

import msal
from osdu_api.providers.types import BaseCredentials

from osducli.log import get_logger

logger = get_logger(__name__)


class MsalInteractiveCredential(BaseCredentials):
    """Refresh token based client for connecting with OSDU."""

    __access_token = None

    def __init__(self, client_id: str, authority: str, scopes: str, token_cache: str = None):
        """Setup the new client

        Args:
            client_id (str): client id for connecting
            authority (str): authority url
            scopes (str): scopes to request
            token_cache (str): path to persist tokens to
        """
        super().__init__()
        self._client_id = client_id
        self._authority = authority
        self._scopes = scopes
        self._token_cache = token_cache

    @property
    def access_token(self) -> str:
        return self.__access_token

    def _refresh_access_token(self) -> dict:
        """Refresh token using msal.

        Returns:
            dict: Dictionary representing the returned token
        """

        # Create a preferably long-lived app instance which maintains a persistant token cache.
        cache = msal.SerializableTokenCache()
        if os.path.exists(self._token_cache):
            with open(self._token_cache, encoding="utf8") as cachefile:
                cache.deserialize(cachefile.read())

        app = msal.PublicClientApplication(
            self._client_id, authority=self._authority, token_cache=cache
        )

        result = None

        # Firstly, check the cache to see if this end user has signed in before
        # accounts = app.get_accounts(username=config.get("username"))
        accounts = app.get_accounts()
        if accounts:
            logger.debug("Account(s) exists in cache, probably with token too. Let's try.")
            # for a in accounts:
            #     print(a["username"])
            chosen = accounts[
                0
            ]  # Assuming the end user chose this one to proceed - should change if multiple
            # Now let's try to find a token in cache for this account
            result = app.acquire_token_silent([self._scopes], account=chosen)

        if not result:
            logger.debug("No suitable token exists in cache. Let's get a new one from AAD.")
            print("A local browser window will be open for you to sign in. CTRL+C to cancel.")
            result = app.acquire_token_interactive(
                [self._scopes],
                timeout=10,
                # login_hint=config.get("username"),  # Optional.
                # If you know the username ahead of time, this parameter can pre-fill
                # the username (or email address) field of the sign-in page for the user,
                # Often, apps use this parameter during reauthentication,
                # after already extracting the username from an earlier sign-in
                # by using the preferred_username claim from returned id_token_claims.
                # Or simply "select_account" as below - Optional. It forces to show account selector page
                prompt=msal.Prompt.SELECT_ACCOUNT,
            )

            if cache.has_state_changed:
                with open(self._token_cache, "w", encoding="utf8") as cachefile:
                    cachefile.write(cache.serialize())

        return result

    def refresh_token(self) -> str:
        result = self._refresh_access_token()

        if "access_token" in result:
            self.__access_token = result["access_token"]
        else:
            logger.error(result.get("error"))
            logger.error(result.get("error_description"))
            logger.error(result.get("correlation_id"))

        return self.__access_token
