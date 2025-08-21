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
"""Useful functions."""

import json
import sys
from configparser import NoOptionError, NoSectionError
from functools import wraps
from urllib.parse import urljoin

import requests
from osdu_api.auth.refresh_token import BaseTokenRefresher
from osdu_api.clients.base_client import BaseClient
from osdu_api.clients.entitlements.entitlements_client import EntitlementsClient
from osdu_api.clients.search.search_client import SearchClient
from osdu_api.clients.storage.record_client import RecordClient
from osdu_api.model.http_method import HttpMethod
from osdu_api.providers.constants import (
    AWS_CLOUD_PROVIDER,
    AZURE_CLOUD_PROVIDER,
    BAREMETAL_PROVIDER,
    GOOGLE_CLOUD_PROVIDER,
    IBM_CLOUD_PROVIDER,
)
from osdu_api.providers.credentials import get_credentials
from requests.models import HTTPError

from osducli.auth.credentials import (
    aws_token_credentials,
    msal_interactive_credentials,
    msal_non_interactive_credentials,
    refresh_token_credentials,
)
from osducli.config import (
    CONFIG_AUTHENTICATION_MODE,
    CONFIG_DATA_PARTITION_ID,
    CONFIG_ENTITLEMENTS_URL,
    CONFIG_SEARCH_URL,
    CONFIG_SERVER,
    CONFIG_STORAGE_URL,
    CONFIG_WELLBORE_DDMS_URL,
    CLIConfig,
)
from osducli.log import get_logger
from osducli.util.exceptions import CliError
from osducli.wbddms_client import WellboreDdmsClient

MSG_JSON_DECODE_ERROR = (
    "Unable to decode the response. Try running again with the --debug command line argument for"
    " more information"
)
MSG_HTTP_ERROR = (
    "An error occurred when accessing the api. Try running again with the --debug command line"
    " argument for more information"
)


logger = get_logger(__name__)


def handle_cli_exceptions(function):
    """Decorator to provide common cli error handling"""

    @wraps(function)
    def decorated(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except HTTPError as ex:
            logger.error(MSG_HTTP_ERROR)
            logger.error("Error (%s) - %s", ex.response.status_code, ex.response.reason)
            logger.error("Message: %s", get_error_message(ex.response))
        except CliError as ex:
            logger.error("Error %s", ex.message)
        except ValueError as ex:
            logger.error(MSG_JSON_DECODE_ERROR)
            logger.error(ex)
        except (NoOptionError, NoSectionError) as ex:
            logger.warning(
                "Configuration missing from config ('%s'). Run 'osdu config update'", ex.args[0]
            )
        sys.exit(1)

    def get_error_message(response: requests.Response) -> str:
        try:
            json_content = response.json()
            if "error" in json_content:
                error_data = json_content["error"]
                if "message" in error_data:
                    return error_data["message"]
                if ("errors" in error_data
                    and isinstance(error_data["errors"], list)
                    and error_data["errors"]):
                    first_error = error_data["errors"][0]
                    if "message" in first_error:
                        return first_error["message"]
            # Fallback if the JSON structure doesn't match the expected pattern
            return response.content
        except json.JSONDecodeError:
            return response.content

    return decorated


class CliOsduClient(BaseClient):
    """Specific class for use from the CLI that provides common error handling, use of configuration
    and messaging

    Args:
        OsduClient ([type]): [description]
    """

    def __init__(self, config: CLIConfig):
        """Setup the new client

        Args:
            config (CLIConfig): cli configuration
        """

        self.config = config

        try:
            # required
            self.server_url = config.get("core", CONFIG_SERVER)
            data_partition = config.get("core", CONFIG_DATA_PARTITION_ID)
            authentication_mode = config.get("core", CONFIG_AUTHENTICATION_MODE)

            if authentication_mode == "refresh_token":
                credentials = refresh_token_credentials(config)
            elif authentication_mode == "msal_interactive":
                credentials = msal_interactive_credentials(config)
            elif authentication_mode == "msal_non_interactive":
                credentials = msal_non_interactive_credentials(config)
            elif authentication_mode == AWS_CLOUD_PROVIDER:
                credentials = aws_token_credentials(config)
            elif authentication_mode in [
                AZURE_CLOUD_PROVIDER,
                BAREMETAL_PROVIDER,
                GOOGLE_CLOUD_PROVIDER,
                IBM_CLOUD_PROVIDER,
            ]:
                credentials = get_credentials(authentication_mode)
            else:
                logger.error(
                    "Unknown type of authentication mode %s. Run 'osdu config update'.",
                    authentication_mode,
                )
                sys.exit(2)

            token_refresher = BaseTokenRefresher(credentials)
            super().__init__(config_manager=config, data_partition_id=data_partition, token_refresher=token_refresher)
        except (NoOptionError, NoSectionError) as ex:
            logger.warning(
                "Authentication information missing from config ('%s'). Run 'osdu config update'",
                ex.args[0],
            )
            sys.exit(1)

    def url_from_config(self, config_url_key: str, url_extra_path: str) -> str:
        """Construct a url using values from configuration"""
        unit_url = self.config.get("core", config_url_key)
        url = urljoin(self.server_url, unit_url) + url_extra_path
        return url

    def check_status_code(self, response: requests.Response, ok_status_codes: list = None):
        """Check the status code of the response and raise an exception if not in the list of ok status codes"""
        if ok_status_codes is None:
            ok_status_codes = [200]
        if response.status_code not in ok_status_codes:
            raise HTTPError(response=response)

    def get_search_client(self) -> SearchClient:
        """Get a client for the search service"""
        search_url = self.url_from_config(CONFIG_SEARCH_URL, "")
        if search_url.endswith("/"):
            search_url = search_url[:-1]
        return SearchClient(
            search_url=search_url,
            config_manager=self.config,
            data_partition_id=self.data_partition_id,
            token_refresher=self.token_refresher
        )

    def get_storage_record_client(self) -> RecordClient:
        """Get a client for the storage record service"""
        storage_url = self.url_from_config(CONFIG_STORAGE_URL, "")
        if storage_url.endswith("/"):
            storage_url = storage_url[:-1]
        return RecordClient(
            storage_url=storage_url,
            config_manager=self.config,
            data_partition_id=self.data_partition_id,
            token_refresher=self.token_refresher
        )

    def get_entitlements_client(self) -> EntitlementsClient:
        """Get a client for the entitlements service"""
        entitlements_url = self.url_from_config(CONFIG_ENTITLEMENTS_URL, "")
        if entitlements_url.endswith("/"):
            entitlements_url = entitlements_url[:-1]
        return EntitlementsClient(
            entitlements_url=entitlements_url,
            config_manager=self.config,
            data_partition_id=self.data_partition_id,
            token_refresher=self.token_refresher
        )

    def get_wellbore_ddms_client(
        self,
        url_extra_path: str
    ) -> WellboreDdmsClient:
        """Get a client for the wellbore ddms service

        Args:
            url_extra_path (str): extra path to add to the base path
        """
        wellbore_ddms_url = self.url_from_config(CONFIG_WELLBORE_DDMS_URL, url_extra_path)
        return WellboreDdmsClient(
            wellbore_ddms_url=wellbore_ddms_url,
            config_manager=self.config,
            data_partition_id=self.data_partition_id,
            token_refresher=self.token_refresher
        )

    def cli_get(
        self,
        config_url_key: str,
        url_extra_path: str,
        ok_status_codes: list = None
    ) -> requests.Response:
        """Basic GET call to the given url, returning the response object.

        Args:
            config_url_key (str): key in configuration for the base path
            url_extra_path (str): extra path to add to the base path
            ok_status_codes (list, optional): Optional status codes to check for successful call.
        """
        url = self.url_from_config(config_url_key, url_extra_path)
        response = self.make_request(method=HttpMethod.GET, url=url)
        self.check_status_code(response, ok_status_codes)
        return response

    def cli_get_returning_json(
        self,
        config_url_key: str,
        url_extra_path: str,
        ok_status_codes: list = None
    ) -> dict:
        """Basic GET call to the given url, returning the json.

        Args:
            config_url_key (str): key in configuration for the base path
            url_extra_path (str): extra path to add to the base path
            ok_status_codes (list, optional): Status codes indicating successful call. Defaults to [200].
        """
        url = self.url_from_config(config_url_key, url_extra_path)
        response = self.make_request(method=HttpMethod.GET, url=url)
        self.check_status_code(response, ok_status_codes)
        return response.json()

    def cli_post_returning_json(
        self,
        config_url_key: str,
        url_extra_path: str,
        data: str | dict,
        ok_status_codes: list = None,
    ) -> dict:
        """Basic POST call to the given url, returning the json.

        Args:
            config_url_key (str): key in configuration for the base path
            url_extra_path (str): extra path to add to the base path
            data (Union[str, dict]): json data as string or dict to send as the body
            ok_status_codes (list, optional): Status codes indicating successful call. Defaults to [200].

        Returns:
            dict: returned json
        """
        url = self.url_from_config(config_url_key, url_extra_path)
        if isinstance(data, dict):
            data = json.dumps(data)
        response = self.make_request(method=HttpMethod.POST, url=url, data=data)
        self.check_status_code(response, ok_status_codes)
        return response.json()

    def cli_delete(
        self,
        config_url_key: str,
        url_extra_path: str,
        ok_status_codes: list = None,
    ) -> requests.Response:
        """Basic DELETE call to the given url.

        Args:
            config_url_key (str): key in configuration for the base path
            url_extra_path (str): extra path to add to the base path
            ok_status_codes (list, optional): Optional status codes to check for successful call.

        Returns:
            requests.Response: Response object from the HTTP call
        """
        url = self.url_from_config(config_url_key, url_extra_path)

        # TODO: Fix bug in SDK for DELETE. Workaround is to give bearer_token
        response = self.make_request(method=HttpMethod.DELETE, url=url,
                                     bearer_token=self.token_refresher.refresh_token())

        self.check_status_code(response, ok_status_codes)
        return response

    def cli_put(
        self,
        config_url_key: str,
        url_extra_path: str,
        data: str | dict,
        ok_status_codes: list = None,
    ) -> requests.Response:
        """Basic PUT call to the given url.

        Args:
            config_url_key (str): key in configuration for the base path
            url_extra_path (str): extra path to add to the base path
            data (Union[str, dict]): json data as string or dict to send as the body
            ok_status_codes (list, optional): Optional status codes to check for successful call.
        """
        url = self.url_from_config(config_url_key, url_extra_path)
        if isinstance(data, dict):
            data = json.dumps(data)
        response = self.make_request(method=HttpMethod.PUT, url=url, data=data)
        self.check_status_code(response, ok_status_codes)
        return response

    def cli_put_returning_json(
        self,
        config_url_key: str,
        url_extra_path: str,
        data: str | dict,
        ok_status_codes: list = None,
    ) -> dict:
        """Basic PUT call to the given url, returning the json.

        Args:
            config_url_key (str): key in configuration for the base path
            url_extra_path (str): extra path to add to the base path
            data (Union[str, dict]): data to send
            ok_status_codes (list, optional): accepted ok response codes. Defaults to [200].

        Returns:
            dict: returned json
        """
        url = self.url_from_config(config_url_key, url_extra_path)
        if isinstance(data, dict):
            data = json.dumps(data)
        response = self.make_request(method=HttpMethod.PUT, url=url, data=data)
        self.check_status_code(response, ok_status_codes)
        return response.json()
