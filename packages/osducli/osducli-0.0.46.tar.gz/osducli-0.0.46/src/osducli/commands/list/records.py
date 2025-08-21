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

"""Custom cluster upgrade specific commands"""
import click
from osdu_api.model.search.query_request import QueryRequest

from osducli.click_cli import CustomClickCommand, State, command_with_output
from osducli.cliclient import CliOsduClient, handle_cli_exceptions


@click.command(cls=CustomClickCommand)
@handle_cli_exceptions
@command_with_output("sort_by(aggregations,&key)[*].{Key:key,Count:count}")
def _click_command(state: State):
    """List count of populated records"""

    return records(state)


def records(state: State):
    """[summary]

    Args:
        state (State): Global state
    """
    client = CliOsduClient(state.config)
    search_client = client.get_search_client()
    query_request = QueryRequest(kind='*:*:*:*', query='*', limit=1, aggregate_by='kind')
    response = search_client.query_records(query_request=query_request)
    client.check_status_code(response)
    return response.json()
