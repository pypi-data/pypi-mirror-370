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

"""Search service query command"""

import click
from osdu_api.model.search.query_request import QueryRequest

from osducli.click_cli import CustomClickCommand, State, command_with_output
from osducli.cliclient import CliOsduClient, handle_cli_exceptions


# click entry point
@click.command(cls=CustomClickCommand)
@click.argument("kind")
@click.option(
    "-l",
    "--limit",
    "limit",
    default=10,
    show_default=True,
    help="maximum number of records to return.",
)
@handle_cli_exceptions
@command_with_output("results[*]")
def _click_command(
    state: State, kind: str, limit: int
):  # noqa:W1
    """Search for items of the specified kind"""
    return query(state, kind, limit)


def query(state: State, kind: str, limit: int):
    """Search for the specified kind

    Args:
        state (State): Global state
        kind (str): Kind to search for
        limit (int): Maximum number of records to return
    """
    client = CliOsduClient(state.config)
    search_client = client.get_search_client()
    query_request = QueryRequest(kind=kind, query='', limit=limit)
    response = search_client.query_records(query_request=query_request)
    client.check_status_code(response)
    return response.json()
