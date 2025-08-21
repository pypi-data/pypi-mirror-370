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

"""Dataload status command"""

import click

from osducli.click_cli import CustomClickCommand, State, command_with_output
from osducli.cliclient import handle_cli_exceptions
from osducli.commands.workflow.status import status
from osducli.log import get_logger

# pylint: disable=duplicate-code

START_TIME = "startTimeStamp"
END_TIME = "endTimeStamp"
STATUS = "status"
RUN_ID = "runId"
TIME_TAKEN = "timeTaken"
FINISHED = "finished"
FAILED = "failed"

logger = get_logger(__name__)


# click entry point
@click.command(cls=CustomClickCommand)
@click.option("-r", "--runid", help="Runid to query status of.")
@click.option(
    "-rl",
    "--runid-log",
    help="Path to a file containing run ids to get status of (see dataload ingest -h).",
    type=click.Path(exists=True, file_okay=True, readable=True, resolve_path=True),
)
@click.option(
    "-w", "--wait", help="Whether to wait for runs to complete.", is_flag=True, show_default=True
)
@handle_cli_exceptions
@command_with_output(None)
def _click_command(state: State, runid: str = None, runid_log: str = None, wait: bool = False):
    """Get status of workflow runs."""
    return status(state, runid, runid_log, wait)
