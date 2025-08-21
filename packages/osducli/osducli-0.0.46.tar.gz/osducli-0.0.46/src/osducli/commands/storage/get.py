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

"""Storage service get command"""

import click

from osducli.click_cli import CustomClickCommand, State, command_with_output
from osducli.cliclient import CliOsduClient, handle_cli_exceptions
from osducli.config import CONFIG_STORAGE_URL


# click entry point
@click.command(cls=CustomClickCommand)
@click.option("-k", "--kind", help="Get records by kind")
@click.option("-id", "--id", "_id", help="An id to search for")
@handle_cli_exceptions
@command_with_output("results || {Id:id,Version:version,Kind:kind,CreateUser:createUser,CreateTime:createTime}")
def _click_command(state: State, kind: str, _id: str):
    """Get records"""
    return get(state, kind, _id)


def get(
    state: State, kind: str = None, id: str = None
):  # pylint: disable=invalid-name,redefined-builtin
    """Get records

    Args:
        state (State): Global state
        kind (str): Kind of records
        id (str): Id of records
    """
    client = CliOsduClient(state.config)
    record_client = client.get_storage_record_client()
    response = None

    # NOTE: there is a difference between records and query endpoints
    # url = "records/id"
    # url = "query/records?limit=10000&kind=osdu:wks:work-product-component--WellLog:1.0.0"

    if kind is None and id is None:
        raise ValueError("You must specify either a kind or id")

    if kind is not None:
        response = client.cli_get(CONFIG_STORAGE_URL, f"query/records?kind={kind}")

    if id is not None:
        response = record_client.query_record(id)

    client.check_status_code(response)
    return response.json()
