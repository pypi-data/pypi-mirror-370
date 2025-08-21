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

"""Entitlements add member command"""

import click

from osducli.click_cli import CustomClickCommand, State, command_with_output
from osducli.cliclient import CliOsduClient, handle_cli_exceptions
from osducli.config import CONFIG_ENTITLEMENTS_URL


# click entry point
@click.command(cls=CustomClickCommand)
@click.option("-m", "--member", help="Email of the member to be added.", required=True)
@click.option("-g", "--group", help="Email address of the group", required=True)
@click.option(
    "-r",
    "--role",
    type=click.Choice(["MEMBER", "OWNER"], case_sensitive=False),
    help="Members role",
    default="MEMBER",
    show_default=True,
)
@handle_cli_exceptions
@command_with_output(None)
def _click_command(state: State, member: str, group: str, role: str):
    """Add members to a group."""
    return add_member(state, member, group, role)


def add_member(state: State, member: str, group: str, role: str) -> dict:
    """Add members to a group.

    Args:
        state (State): Global state
        member (str): Email address of the member
        group (str): Email address of the group
        role (str): Members role

    Returns:
        dict: Response from service
    """
    client = CliOsduClient(state.config)
    request_data = {
        "email": member,
        "role": role,
    }
    return client.cli_post_returning_json(
        config_url_key=CONFIG_ENTITLEMENTS_URL,
        url_extra_path=f"groups/{group}/members",
        data=request_data
    )
