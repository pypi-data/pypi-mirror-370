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

"""Workflow list command"""

import click

from osducli.click_cli import CustomClickCommand, State, global_params
from osducli.cliclient import CliOsduClient, handle_cli_exceptions
from osducli.config import CONFIG_WORKFLOW_URL


# click entry point
@click.command(cls=CustomClickCommand)
@click.option("-n", "--name", help="Workflow (DAG) name", required=True)
@handle_cli_exceptions
@global_params
def _click_command(state: State, name: str) -> dict:
    """Un-register an Airflow workflow from OSDU"""
    return unregister_workflow(state, name)


def unregister_workflow(state: State, name: str) -> dict:
    """Un-register an Airflow workflow from OSDU

    Args:
        state (State): Global state
        name (str): DAG Name
    """
    connection = CliOsduClient(state.config)
    connection.cli_delete(CONFIG_WORKFLOW_URL, "workflow/" + name, [204])
