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

"""File metadata command"""

import click

from osducli.click_cli import CustomClickCommand, State, command_with_output
from osducli.cliclient import CliOsduClient, handle_cli_exceptions
from osducli.config import CONFIG_FILE_URL


# click entry point
@click.command(cls=CustomClickCommand)
@click.option("-id", "--id", "_id", help="id to get metadata for", required=True)
@handle_cli_exceptions
@command_with_output()
def _click_command(state: State, _id: str):
    """Get file metadata"""
    return file_metadata(state, _id)


def file_metadata(state: State, _id: str):
    client = CliOsduClient(state.config)
    json = client.cli_get_returning_json(CONFIG_FILE_URL, f"files/{_id}/metadata")
    return json
