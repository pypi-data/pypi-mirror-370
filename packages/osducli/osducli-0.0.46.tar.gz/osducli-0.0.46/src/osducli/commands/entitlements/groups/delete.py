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

"""Entitlements groups delete command"""

import click

from osducli.click_cli import CustomClickCommand, State, global_params
from osducli.cliclient import CliOsduClient, handle_cli_exceptions
from osducli.config import CONFIG_ENTITLEMENTS_URL


# click entry point
@click.command(cls=CustomClickCommand)
@click.option("-g", "--group", help="Email address of the group", required=True)
@handle_cli_exceptions
@global_params
def _click_command(state: State, group: str):
    """Delete a group."""
    delete_group(state, group)


def delete_group(state: State, group: str):
    """Delete a group

    Args:
        state (State): Global state
        group (str): Unique email identifier of the group
    """
    client = CliOsduClient(state.config)
    client.cli_delete(
        config_url_key=CONFIG_ENTITLEMENTS_URL,
        url_extra_path=f"groups/{group}",
        ok_status_codes=[200, 204]
    )

    if state.is_user_friendly_mode():
        print("1 group deleted")
