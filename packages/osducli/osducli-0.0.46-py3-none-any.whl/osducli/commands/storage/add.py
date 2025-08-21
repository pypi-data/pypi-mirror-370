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

"""Version command"""

import json

import click
from osdu_api.model.storage.record import Record

from osducli.click_cli import CustomClickCommand, State, command_with_output
from osducli.cliclient import CliOsduClient, handle_cli_exceptions
from osducli.log import get_logger
from osducli.util.file import get_files_from_path_with_suffix

logger = get_logger(__name__)


# click entry point
@click.command(cls=CustomClickCommand)
@click.option(
    "-p",
    "--path",
    help="Path to a record or records to add.",
    type=click.Path(exists=True, file_okay=True, dir_okay=True, readable=True, resolve_path=True),
    required=True,
)
@click.option(
    "-b",
    "--batch",
    help="Number of records to add per API call. If not specified records are uploaded as is.",
    is_flag=False,
    flag_value=200,
    type=int,
    default=None,
    show_default=True,
)
@handle_cli_exceptions
@command_with_output(None)
def _click_command(state: State, path: str, batch: int):
    """Add or update a record"""
    return add_records(state, path, batch)


def add_records(state: State, path: str, batch: int = None):
    """Add or update a record

    Args:
        state (State): Global state
        path (str): Path to a record or records to add.
        batch (int): Batch size per API call. If None then ingest as is
    """
    client = CliOsduClient(state.config)
    record_client = client.get_storage_record_client()

    files = get_files_from_path_with_suffix(path, ".json")
    logger.debug("Files list: %s", files)

    if batch is not None:
        logger.info("Batching records with size %s", batch)
        file_batches = chunk_list(files, batch)
        for file_batch in file_batches:
            response = add_record_batch(record_client, file_batch)
            handle_response(client, response)
    else:
        response = add_record_batch(record_client, files)
        handle_response(client, response)


def add_record_batch(record_client, files):
    record_list = []
    for filepath in files:
        with open(filepath, encoding="utf-8") as file:
            storage_object = json.load(file)

            logger.info("Processing file %s.", filepath)
            record_list.append(Record.from_dict(storage_object))

    return record_client.create_update_records(record_list)


def chunk_list(lst, size):
    return [lst[i:i + size] for i in range(0, len(lst), size)]


def handle_response(client, response):
    client.check_status_code(response, [200, 201])
    response_json = response.json()
    count = response_json["recordCount"]
    added = response_json["recordIds"]
    skipped = response_json.get("skippedRecordIds", [])

    print(f"Record count: {count}")
    print(json.dumps(added, indent=2))

    if skipped:
        print("Skipped records:")
        print(json.dumps(skipped, indent=2))
