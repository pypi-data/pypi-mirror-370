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

"""Unit service list command"""

import click

from osducli.click_cli import CustomClickCommand, State, command_with_output
from osducli.cliclient import CliOsduClient, handle_cli_exceptions
from osducli.config import CONFIG_UNIT_URL


# click entry point
@click.command(cls=CustomClickCommand)
@handle_cli_exceptions
@command_with_output("units[].[displaySymbol,name,source]")
def _click_command(state: State):
    """List unit configuration"""
    return unit_list(state)


def unit_list(state: State):
    """List unit configuration

    Args:
        state (State): Global state
    """
    connection = CliOsduClient(state.config)
    json = connection.cli_get_returning_json(CONFIG_UNIT_URL, "unit?limit=10000")
    return json
