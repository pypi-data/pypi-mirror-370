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

"""Service information"""

from osducli.click_cli import State
from osducli.cliclient import CliOsduClient
from osducli.commands.status.status import check_status
from osducli.commands.version.version import get_api_info


def info(
    state: State,
    name: str,
    config_url_key: str,
    status_path: str,
    swagger_path: str,
    documentation: str = None,
) -> dict:
    """Return information about the service

    Args:
        state (State): Global state
        name (str): Name of the service
        config_url_key (str): Config url key
        status_path (str): Path to status service
        swagger_path (str): Swagger path
        documentation (str): Link to documentaion about the underlying service

    Returns:
        dict: Response from service
    """
    connection = CliOsduClient(state.config)

    status = check_status(connection, name, config_url_key, status_path)
    if state.is_user_friendly_mode():
        print("Status:", status["status"])
        print("Reason:", status["reason"])

    version = get_api_info(connection, config_url_key, "info")

    swagger_path_expanded = (
        connection.url_from_config(config_url_key, swagger_path) if swagger_path else None
    )

    if state.is_user_friendly_mode():
        if version:
            print("Version:", version["version"])
            print("Build Time:", version["buildTime"])
            print("Branch:", version["branch"])
            print("Commit Id:", version["commitId"])
        else:
            print("No version information available")

        if swagger_path_expanded:
            print("Swagger:", swagger_path_expanded)
        else:
            print("Swagger path unknown")

        if documentation:
            print("Documentation:", documentation)

    return (
        None
        if state.is_user_friendly_mode()
        else {
            "status": status,
            "version": version,
            "swagger": swagger_path_expanded,
            "documentation": documentation,
        }
    )
