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

"""Entitlements members groups command"""

import click

from osducli.click_cli import CustomClickCommand, State, command_with_output
from osducli.cliclient import CliOsduClient, handle_cli_exceptions
from osducli.config import CONFIG_ENTITLEMENTS_URL


# click entry point
@click.command(cls=CustomClickCommand)
@click.option("-m", "--member", help="Email of the member to show groups for.", required=True)
@handle_cli_exceptions
@command_with_output("groups[*]")
def _click_command(state: State, member: str):
    """List groups a member belongs to."""

    client = CliOsduClient(state.config)
    return client.cli_get_returning_json(
        config_url_key=CONFIG_ENTITLEMENTS_URL,
        url_extra_path=f"members/{member}/groups?type=none"
    )
