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
"""Well Log add record command"""
import json

import click

from osducli.click_cli import CustomClickCommand, State, command_with_output
from osducli.cliclient import CliOsduClient, handle_cli_exceptions
from osducli.commands.wellbore_ddms._const import WELLBORE_DDMS_WELL_LOG_PATH


# click entry point
@click.command(cls=CustomClickCommand, help="Add Well Log record")
@click.option("-f", "--file", "_file", help="WellLog record file to add", required=True)
@handle_cli_exceptions
@command_with_output("recordIds")
def _click_command(state: State, _file: str):
    return add_record(state, _file)


def add_record(state: State, record_file: str):
    """Add Well Log record"""
    client = CliOsduClient(state.config)
    wellbore_client = client.get_wellbore_ddms_client(url_extra_path=WELLBORE_DDMS_WELL_LOG_PATH)

    with open(record_file) as file:
        record_data = json.load(file)

    record_data_list = "[" + json.dumps(record_data) + "]"
    response = wellbore_client.create_well_log(record_data_list)
    client.check_status_code(response)
    return response.json()
