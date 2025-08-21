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

from osducli.click_cli import CustomClickCommand, State, command_with_output
from osducli.cliclient import CliOsduClient, handle_cli_exceptions
from osducli.config import CONFIG_WORKFLOW_URL


# click entry point
@click.command(cls=CustomClickCommand)
@click.option("-n", "--name", help="Workflow (DAG) name", required=True)
@click.option("-d", "--description", help="Description", required=True)
@handle_cli_exceptions
@command_with_output(None)
def _click_command(state: State, name: str, description: str) -> dict:
    """Register an Airflow workflow with OSDU"""
    return register_workflow(state, name, description)


def register_workflow(state: State, name: str, description: str) -> dict:
    """Register an Airflow workflow with OSDU

    Args:
        state (State): Global state
        name (str): DAG Name
        description (str): Description

    Returns:
        dict: Response from service
    """
    connection = CliOsduClient(state.config)

    request = {
        "description": description,
        "registrationInstructions": {},
        "workflowName": name,
    }
    response_json = connection.cli_post_returning_json(CONFIG_WORKFLOW_URL, "workflow", request)
    return response_json
