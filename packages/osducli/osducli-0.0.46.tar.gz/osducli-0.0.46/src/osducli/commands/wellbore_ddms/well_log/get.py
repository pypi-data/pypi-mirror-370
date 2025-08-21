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
"""Well Log get record command"""
import click

from osducli.click_cli import CustomClickCommand, State, command_with_output
from osducli.cliclient import CliOsduClient, handle_cli_exceptions
from osducli.commands.wellbore_ddms._const import WELLBORE_DDMS_WELL_LOG_PATH


# click entry point
@click.command(cls=CustomClickCommand, help="Get Well Log record by id")
@click.option("-id", "--id", "_id", help="WellLog id to search for", required=True)
@handle_cli_exceptions
@command_with_output()
def _click_command(state: State, _id: str):
    return get_record(state, _id)


def get_record(state: State, identifier: str):
    """Get Well Log record by id"""
    client = CliOsduClient(state.config)
    wellbore_client = client.get_wellbore_ddms_client(url_extra_path=WELLBORE_DDMS_WELL_LOG_PATH)
    response = wellbore_client.get_well_log(identifier)
    client.check_status_code(response)
    return response.json()
