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

"""Entitlements my groups command"""

import click

from osducli.click_cli import CustomClickCommand, State, command_with_output
from osducli.cliclient import CliOsduClient, handle_cli_exceptions


# click entry point
@click.command(cls=CustomClickCommand)
@handle_cli_exceptions
@command_with_output("groups[*]")
def _click_command(state: State):
    """List groups you have access to."""
    return list_my_groups(state)


def list_my_groups(state: State) -> dict:
    """Get the calling users groups

    Args:
        state (State): Global state

    Returns:
        dict: Response from service
    """
    client = CliOsduClient(state.config)
    entitlements_client = client.get_entitlements_client()
    response = entitlements_client.get_groups_for_user()
    return response.json()
