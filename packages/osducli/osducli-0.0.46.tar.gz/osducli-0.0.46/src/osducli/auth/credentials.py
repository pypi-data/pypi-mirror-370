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
"""Credentials functions."""

import os

from osdu_api.providers.types import BaseCredentials

from osducli.auth.aws_token_credential import AwsTokenCredential
from osducli.auth.msal_interactive import MsalInteractiveCredential
from osducli.auth.msal_non_interactive import MsalNonInteractiveCredential
from osducli.auth.token_credential import TokenCredential
from osducli.config import (
    CLI_CONFIG_DIR,
    CONFIG_AUTHENTICATION_AUTHORITY,
    CONFIG_AUTHENTICATION_SCOPES,
    CONFIG_CLIENT_ID,
    CONFIG_CLIENT_SECRET,
    CONFIG_REFRESH_TOKEN,
    CONFIG_TOKEN_ENDPOINT,
)


def aws_token_credentials(config) -> BaseCredentials:
    """Credentials for AWS"""
    client_id = config.get("core", CONFIG_CLIENT_ID)
    client_secret = config.get("core", CONFIG_CLIENT_SECRET, None)
    token_endpoint = config.get("core", CONFIG_AUTHENTICATION_AUTHORITY, None)
    scopes = config.get("core", CONFIG_AUTHENTICATION_SCOPES, None)
    credentials = AwsTokenCredential(client_id, client_secret, token_endpoint, scopes)
    return credentials


def msal_non_interactive_credentials(config) -> BaseCredentials:
    """Credentials for Azure using MSAL non-interactive"""
    client_id = config.get("core", CONFIG_CLIENT_ID)
    authority = config.get("core", CONFIG_AUTHENTICATION_AUTHORITY, None)
    scopes = config.get("core", CONFIG_AUTHENTICATION_SCOPES, None)
    client_secret = config.get("core", CONFIG_CLIENT_SECRET, None)
    credentials = MsalNonInteractiveCredential(
        client_id=client_id,
        client_secret=client_secret,
        authority=authority,
        scopes=scopes,
    )
    return credentials


def msal_interactive_credentials(config) -> BaseCredentials:
    """Credentials for Azure using MSAL interactive"""
    client_id = config.get("core", CONFIG_CLIENT_ID)
    authority = config.get("core", CONFIG_AUTHENTICATION_AUTHORITY, None)
    scopes = config.get("core", CONFIG_AUTHENTICATION_SCOPES, None)
    cache_path = os.path.join(CLI_CONFIG_DIR, "msal_token_cache.bin")
    credentials = MsalInteractiveCredential(
        client_id, authority, scopes, cache_path
    )
    return credentials


def refresh_token_credentials(config) -> BaseCredentials:
    """Credentials for Azure using refresh token"""
    client_id = config.get("core", CONFIG_CLIENT_ID)
    token_endpoint = config.get("core", CONFIG_TOKEN_ENDPOINT, None)
    refresh_token = config.get("core", CONFIG_REFRESH_TOKEN, None)
    client_secret = config.get("core", CONFIG_CLIENT_SECRET, None)
    credentials = TokenCredential(
        client_id, token_endpoint, refresh_token, client_secret
    )
    return credentials
