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

from urllib.parse import quote_plus

import click

from osducli.click_cli import CustomClickCommand, State, command_with_output
from osducli.cliclient import CliOsduClient, handle_cli_exceptions
from osducli.config import CONFIG_SCHEMA_URL


# click entry point
@click.command(cls=CustomClickCommand)
@click.option("-a", "--authority", help="Authority to filter by")
@click.option("-e", "--entity", help="Entity to filter by")
@click.option("-s", "--source", help="Source to filter by")
@handle_cli_exceptions
@command_with_output(
    "sort_by(schemaInfos[].schemaIdentity[].{id:id,Authority:authority,Source:source,Entity:entityType,MajorVersion:schemaVersionMajor,MinorVersion:schemaVersionMinor,PatchVersion:schemaVersionPatch},&id)"  # noqa: E501
)
def _click_command(state: State, authority: str = None, entity: str = None, source: str = None):
    """List schemas"""
    return schema_list(state, authority, entity, source)


def schema_list(state: State, authority: str, entity: str, source: str):
    """List schemas

    Args:
        state (State): Global state
        authority (str): Global state
        entity (str): Global state
        source (str): Global state
    """
    connection = CliOsduClient(state.config)
    url = "schema?limit=10000"
    if authority:
        url += "&authority=" + quote_plus(authority)
    if entity:
        url += "&entity=" + quote_plus(entity)
    if source:
        url += "&source=" + quote_plus(source)
    json = connection.cli_get_returning_json(CONFIG_SCHEMA_URL, url)
    return json
