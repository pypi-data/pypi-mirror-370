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

"""file download command"""

import click
import requests

from osducli.click_cli import CustomClickCommand, State, command_with_output
from osducli.cliclient import CliOsduClient, handle_cli_exceptions
from osducli.config import CONFIG_FILE_URL


# click entry point
@click.command(cls=CustomClickCommand)
@click.option("-id", "--id", "_id", help="id to download", required=True)
@click.option(
    "-p",
    "--path",
    help="Path to download the file to.",
    type=click.Path(file_okay=True, dir_okay=False, writable=True, resolve_path=True),
    required=True,
)
@handle_cli_exceptions
@command_with_output(
    # "crses[].{Name:aliasNames[0],Authority:baseCRSAuthorityCode.auth,Code:baseCRSAuthorityCode.code,Type:crstype,Source:source}"  # noqa: E501
)
def _click_command(state: State, _id: str, path: str):
    """Download a file"""
    return file_download(state, _id, path)


def file_download(state: State, _id: str, path: str):
    """List coordinate referense systems

    Args:
        state (State): Global state
        path (str): path to download the file to
    """
    connection = CliOsduClient(state.config)
    json = connection.cli_get_returning_json(CONFIG_FILE_URL, f"files/{_id}/downloadURL")
    signed_url = json["SignedUrl"]

    # pylint: disable=missing-timeout
    with requests.get(signed_url, stream=True) as response:
        response.raise_for_status()
        with open(path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

    return json
