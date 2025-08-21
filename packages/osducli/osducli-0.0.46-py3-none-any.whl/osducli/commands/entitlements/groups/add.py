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

"""Entitlements groups add command"""

import click

from osducli.click_cli import CustomClickCommand, State, command_with_output
from osducli.cliclient import CliOsduClient, handle_cli_exceptions
from osducli.config import CONFIG_ENTITLEMENTS_URL


# click entry point
@click.command(cls=CustomClickCommand)
@click.option("-g", "--group", help="Email address of the group", required=True)
@click.option("-d", "--description", help="Description")
@handle_cli_exceptions
@command_with_output(None)
def _click_command(state: State, group: str, description: str):
    """Add a group."""
    return add_group(state, group, description)


def add_group(state: State, group: str, description: str = None) -> dict:
    """Add a group

    Args:
        state (State): Global state
        group (str): Email address of the group
        description (str): Description for the group

    Returns:
        dict: Response from service
    """
    client = CliOsduClient(state.config)
    request_data = {"name": group}
    if description is not None:
        request_data["description"] = description

    return client.cli_post_returning_json(
        config_url_key=CONFIG_ENTITLEMENTS_URL,
        url_extra_path="groups",
        data=request_data,
        ok_status_codes=[200, 201]
    )
