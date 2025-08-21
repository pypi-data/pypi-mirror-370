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

"""Version command"""

import platform
import sys

import click
from packaging.version import Version
from requests.exceptions import RequestException

from osducli.click_cli import CustomClickCommand, State, command_with_output
from osducli.cliclient import CliOsduClient, handle_cli_exceptions
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
    CONFIG_WORKFLOW_URL,
)
from osducli.log import get_logger
from osducli.util.pypi import get_pypi_version
from osducli.version import get_version

logger = get_logger(__name__)


# click entry point
@click.command(cls=CustomClickCommand)
@handle_cli_exceptions
@command_with_output("results[]")
def _click_command(state: State):
    """Version information"""
    return version(state)


def get_runtime_version() -> str:
    """Get the runtime information.

    Returns:
        str: Runtime information
    """

    version_info = f"Python ({platform.system()}) {sys.version}"
    version_info += "\n\n"
    version_info += f"Python location '{sys.executable}'"
    return version_info


def get_api_info(connection: CliOsduClient, config_url_key: str, url_extra_path: str):
    """Check the status of the given service"""
    try:
        response = connection.cli_get_returning_json(config_url_key, url_extra_path)
        return response
    except RequestException:
        return None


def version(state: State):
    """Print version information to standard system out."""
    if state.is_user_friendly_mode():
        current_version = get_version()
        latest_version = get_pypi_version("osducli")
        version_info = f"Installed OSDU Cli Version {current_version}\n"
        if latest_version is not None:
            version_info += f"Latest OSDU Cli Version {latest_version}\n"
            if Version(current_version) < Version(latest_version):
                version_info += f"\b\n\033[33mWARNING: You are using osdu cli version {current_version}; however version {latest_version} is available.\033[39m"  # noqa: E501
                version_info += "\b\n\033[33mYou should consider upgrading via the 'pip install -U osducli' command\033[39m"  # noqa: E501
        else:
            version_info += "Latest OSDU Cli Version - unable to check!\n"

        version_info += "\n"
        version_info += get_runtime_version()
        print(version_info)

    services = [
        ("CRS catalog service", CONFIG_CRS_CATALOG_URL, "info"),
        ("CRS converter service", CONFIG_CRS_CONVERTER_URL, "info"),
        ("Entitlements service", CONFIG_ENTITLEMENTS_URL, "info"),
        ("File service", CONFIG_FILE_URL, "info"),
        ("Legal service", CONFIG_LEGAL_URL, "info"),
        ("Schema service", CONFIG_SCHEMA_URL, "info"),
        ("Search service", CONFIG_SEARCH_URL, "info"),
        ("Storage service", CONFIG_STORAGE_URL, "info"),
        ("Unit service", CONFIG_UNIT_URL, "info"),
        ("Workflow service", CONFIG_WORKFLOW_URL, "info"),
    ]
    results = []
    connection = CliOsduClient(state.config)
    for service in services:
        result = get_api_info(connection, service[1], service[2])
        results.append(result)
        if state.is_user_friendly_mode():
            print()
            print(service[0])
            print("  Version:", result["version"])
            print("  Build Time:", result["buildTime"])
            print("  Branch:", result["branch"])
            print("  Commit Id:", result["commitId"])

    return None if state.is_user_friendly_mode() else {"results": results}
