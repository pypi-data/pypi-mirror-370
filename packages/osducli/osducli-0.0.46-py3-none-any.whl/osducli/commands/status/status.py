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

"""Code to handle status commands"""

import click
from requests.exceptions import RequestException

from osducli.click_cli import CustomClickCommand, State, command_with_output
from osducli.cliclient import CliOsduClient, handle_cli_exceptions
from osducli.commands.crs._const import (
    CRS_CATALOG_SERVICE_NAME,
    CRS_CATALOG_STATUS_PATH,
    CRS_CONVERTER_SERVICE_NAME,
    CRS_CONVERTER_STATUS_PATH,
)
from osducli.commands.entitlements._const import (
    ENTITLEMENTS_SERVICE_NAME,
    ENTITLEMENTS_STATUS_PATH,
)
from osducli.commands.file._const import FILE_SERVICE_NAME, FILE_STATUS_PATH
from osducli.commands.legal._const import LEGAL_SERVICE_NAME, LEGAL_STATUS_PATH
from osducli.commands.schema._const import SCHEMA_SERVICE_NAME, SCHEMA_STATUS_PATH
from osducli.commands.search._const import SEARCH_SERVICE_NAME, SEARCH_STATUS_PATH
from osducli.commands.storage._const import STORAGE_SERVICE_NAME, STORAGE_STATUS_PATH
from osducli.commands.unit._const import UNIT_SERVICE_NAME, UNIT_STATUS_PATH
from osducli.commands.wellbore_ddms._const import (
    WELLBORE_DDMS_SERVICE_NAME,
    WELLBORE_DDMS_STATUS_PATH,
)
from osducli.commands.workflow._const import WORKFLOW_SERVICE_NAME, WORKFLOW_STATUS_PATH
from osducli.config import (
    CONFIG_CRS_CATALOG_URL,
    CONFIG_CRS_CONVERTER_URL,
    CONFIG_ENTITLEMENTS_URL,
    CONFIG_FILE_URL,
    CONFIG_LEGAL_URL,
    CONFIG_SCHEMA_URL,
    CONFIG_SEARCH_URL,
    CONFIG_STORAGE_URL,
    CONFIG_UNIT_URL,
    CONFIG_WELLBORE_DDMS_URL,
    CONFIG_WORKFLOW_URL,
)
from osducli.log import get_logger

logger = get_logger(__name__)


@click.command(cls=CustomClickCommand)
@handle_cli_exceptions
@command_with_output("results[]")
def _click_command(state: State):
    # def _click_command(ctx, debug, config, hostname):
    """Shows the status of OSDU services"""
    return status(state)


def status(state: State):
    """status command entry point

    User friendly mode displays results as received for responsiveness.
    Args:
        state (State): Global state
    """
    connection = CliOsduClient(state.config)
    results = []
    services = [
        (CRS_CATALOG_SERVICE_NAME, CONFIG_CRS_CATALOG_URL, CRS_CATALOG_STATUS_PATH),
        (CRS_CONVERTER_SERVICE_NAME, CONFIG_CRS_CONVERTER_URL, CRS_CONVERTER_STATUS_PATH),
        (FILE_SERVICE_NAME, CONFIG_FILE_URL, FILE_STATUS_PATH),
        (ENTITLEMENTS_SERVICE_NAME, CONFIG_ENTITLEMENTS_URL, ENTITLEMENTS_STATUS_PATH),
        (LEGAL_SERVICE_NAME, CONFIG_LEGAL_URL, LEGAL_STATUS_PATH),
        (SCHEMA_SERVICE_NAME, CONFIG_SCHEMA_URL, SCHEMA_STATUS_PATH),
        (SEARCH_SERVICE_NAME, CONFIG_SEARCH_URL, SEARCH_STATUS_PATH),
        (STORAGE_SERVICE_NAME, CONFIG_STORAGE_URL, STORAGE_STATUS_PATH),
        (UNIT_SERVICE_NAME, CONFIG_UNIT_URL, UNIT_STATUS_PATH),
        (WELLBORE_DDMS_SERVICE_NAME, CONFIG_WELLBORE_DDMS_URL, WELLBORE_DDMS_STATUS_PATH),
        (WORKFLOW_SERVICE_NAME, CONFIG_WORKFLOW_URL, WORKFLOW_STATUS_PATH),
    ]
    for service in services:
        result = check_status(connection, service[0], service[1], service[2])
        results.append(result)
        if state.is_user_friendly_mode():
            print(f"{result['name'].ljust(20)} {result['status']}\t {result['reason']}")

    return None if state.is_user_friendly_mode() else {"results": results}


def check_status(connection: CliOsduClient, name: str, config_url_key: str, url_extra_path: str):
    """Check the status of the given service"""
    try:
        response = connection.cli_get(config_url_key, url_extra_path)
        _status = response.status_code
        _reason = response.reason
    except RequestException as _ex:
        exception_message = str(_ex) if len(str(_ex)) > 0 else "Unknown Error"
        logger.debug(exception_message)
        _status = _ex.response.status_code if _ex.response else -1
        _reason = _ex.response.reason if _ex.response else exception_message

    result = {"name": name, "status": _status, "reason": _reason}
    return result
