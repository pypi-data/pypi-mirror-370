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

"""Legal service add command"""

import json

import click

from osducli.click_cli import CustomClickCommand, State, command_with_output
from osducli.cliclient import CliOsduClient, handle_cli_exceptions
from osducli.config import CONFIG_LEGAL_URL
from osducli.log import get_logger

logger = get_logger(__name__)


# click entry point
@click.command(cls=CustomClickCommand)
@click.option(
    "-p",
    "--path",
    help="Path to a json file with the legal tag to add.",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True),
    required=True,
)
@handle_cli_exceptions
@command_with_output(None)
def _click_command(state: State, path: str):
    """Add a legal tag"""
    return add_legal_tag(state, path)


def add_legal_tag(state: State, path: str) -> dict:
    """Add a legal tag

    Args:
        state (State): Global state
        path (str): Path to json file with the legal tag to add.
    Returns:
        dict: Response from service
    """
    connection = CliOsduClient(state.config)

    if path.endswith(".json"):
        with open(path, encoding="utf-8") as file:
            payload = json.load(file)
            response_json = None
            response_json = connection.cli_post_returning_json(
                CONFIG_LEGAL_URL, "legaltags", payload, [200, 201]
            )
            return response_json
    else:
        print(f"{path} must be a json file and have a .json extension")

    return None
