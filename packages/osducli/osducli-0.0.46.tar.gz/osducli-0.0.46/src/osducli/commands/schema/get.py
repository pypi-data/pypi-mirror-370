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

"""Schema service list command"""

import click

from osducli.click_cli import CustomClickCommand, State, command_with_output
from osducli.cliclient import CliOsduClient, handle_cli_exceptions
from osducli.config import CONFIG_SCHEMA_URL


# click entry point
@click.command(cls=CustomClickCommand)
@click.option("-k", "--kind", required=True, help="Kind of the schema")
@handle_cli_exceptions
@command_with_output(None)
def _click_command(state: State, kind: str):
    """Get schema"""
    return schema_get(state, kind)


def schema_get(state: State, kind: str):
    """Get schema

    Args:
        state (State): Global state
        kind (str): Kind of the schema
    """
    connection = CliOsduClient(state.config)
    url = "schema/" + kind
    json = connection.cli_get_returning_json(CONFIG_SCHEMA_URL, url)
    return json
