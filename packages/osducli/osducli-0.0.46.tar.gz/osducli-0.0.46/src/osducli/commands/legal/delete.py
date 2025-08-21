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

"""Legal service delete command"""

import click

from osducli.click_cli import CustomClickCommand, State, global_params
from osducli.cliclient import CliOsduClient, handle_cli_exceptions
from osducli.config import CONFIG_LEGAL_URL


# click entry point
@click.command(cls=CustomClickCommand)
@click.option("-n", "--name", required=True, help="Name of tag to delete")
@handle_cli_exceptions
@global_params
def _click_command(state: State, name: str):
    """Delete legal tag"""
    return delete(state, name)


def delete(state: State, name: str):
    """Delete legal tag

    Args:
        state (State): Global state
        name (str): Name of legal tag to delete
    """
    connection = CliOsduClient(state.config)
    url = "legaltags/" + name
    connection.cli_delete(CONFIG_LEGAL_URL, url, [204])

    if state.is_user_friendly_mode():
        print("1 legal tag deleted")
