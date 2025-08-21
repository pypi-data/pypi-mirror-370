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

"""Dataload ingest command"""

import json
import os
import re

import click
import requests

from osducli.click_cli import CustomClickCommand, State, command_with_output
from osducli.cliclient import CliOsduClient, handle_cli_exceptions
from osducli.commands.dataload.verify import batch_verify
from osducli.commands.workflow.status import check_status
from osducli.config import (
    CONFIG_ACL_OWNER,
    CONFIG_ACL_VIEWER,
    CONFIG_DATA_PARTITION_ID,
    CONFIG_FILE_URL,
    CONFIG_LEGAL_TAG,
    CONFIG_WORKFLOW_URL,
    CLIConfig,
)
from osducli.log import get_logger
from osducli.util.exceptions import CliError
from osducli.util.file import get_files_from_path

logger = get_logger(__name__)
VERIFY_BATCH_SIZE = 200


# click entry point
@click.command(cls=CustomClickCommand)
@click.option(
    "-p",
    "--path",
    help="Path to a sequence file, manifest file or folder with manifest files to ingest.",
    type=click.Path(exists=True, file_okay=True, dir_okay=True, readable=True, resolve_path=True),
    required=True,
)
@click.option("-f", "--files", help="Associated files to upload for Work-Products.")
@click.option(
    "-b",
    "--batch",
    help="Batch size (per file). If not specified manifests are uploaded as is.",
    is_flag=False,
    flag_value=200,
    type=int,
    default=None,
    show_default=True,
)
@click.option(
    "-rl",
    "--runid-log",
    help="Path to a file to save run ids to to later check status of (see dataload status -h).",
)
@click.option(
    "-w", "--wait", help="Whether to wait for runs to complete.", is_flag=True, show_default=True
)
@click.option(
    "-s",
    "--skip-existing",
    help="Skip reloading records that already exist.",
    is_flag=True,
    default=False,
    show_default=True,
)
@click.option("--simulate", help="Simulate ingestion only.", is_flag=True, show_default=True)
# @click.option(
#     "-a",
#     "--authority",
#     help="Schema authority to use when generating manifest files.",
#     default="osdu",
#     show_default=True,
#     required=False,
# )
# @click.option(
#     "-d",
#     "--data-partition",
#     help="A data partition name to use when generating manifest files. If not specified the default value is used.",
# )
@click.option(
    "-l",
    "--legal-tags",
    help=(  # noqa: E501
        "Rewrite existing legal tags. Specify either a comma seperated list of values or without a"
        " value to use the default value from config."
    ),
    is_flag=False,
    flag_value="",
    default=None,
    show_default=True,
)
@click.option(
    "-aclo",
    "--acl-owners",
    help=(  # noqa: E501
        "Rewrite existing acl owners. Specify either a comma seperated list of values or without a"
        " value to use the default value from config."
    ),
    is_flag=False,
    flag_value="",
    default=None,
    show_default=True,
)
@click.option(
    "-aclv",
    "--acl-viewers",
    help=(  # noqa: E501
        "Rewrite existing acl viewers. Specify either a comma seperated list of values or without a"
        " value to use the default value from config."
    ),
    is_flag=False,
    flag_value="",
    default=None,
    show_default=True,
)
@handle_cli_exceptions
@command_with_output(None)
def _click_command(
    state: State,
    path: str,
    files: str,
    batch: int,
    runid_log: str = None,
    wait: bool = False,
    skip_existing: str = False,
    simulate: bool = False,
    # authority: str = None,
    # data_partition: str = None,
    legal_tags: str = None,
    acl_owners: str = None,
    acl_viewers: str = None,
):  # pylint: disable=too-many-arguments
    """Ingest manifest files into OSDU.

    This command will take existing manfiest files and load them into OSDU via the workflow
    service and Airflow. 'legal' and 'acl' tags will be updated based upon the current
    configuration"""
    return ingest(
        state,
        path,
        files,
        batch,
        runid_log,
        wait,
        skip_existing,
        simulate,
        (
            # authority,
            # data_partition,
            None
            if legal_tags is None
            else [] if legal_tags == "" else legal_tags.split(",")
        ),
        None if acl_owners is None else [] if acl_owners == "" else acl_owners.split(","),
        None if acl_viewers is None else [] if acl_viewers == "" else acl_viewers.split(","),
    )


def ingest(  # pylint: disable=too-many-arguments
    state: State,
    path: str,
    files: str,
    batch_size: int = 1,
    runid_log: str = None,
    wait: bool = False,
    skip_existing: bool = False,
    simulate: bool = False,
    # authority: str = None,
    # data_partition: str = None,
    legal_tags: list[str] = None,
    acl_owners: list[str] = None,
    acl_viewers: list[str] = None,
) -> dict:
    """Ingest manifest files into OSDU

    Args:
        state (State): Global state
        path (str): [description]
        files (str): [description]
        batch_size (int): [description]
        runid_log (str): [description]
        wait (bool): [description]
        skip_existing (bool): [description]
        simulate (bool): [description]
        legal_tags (list[str]): [description]
        acl_owners (list[str]): [description]
        acl_viewers (list[str]): [description]

    Returns:
        dict: Response from service
    """
    manifest_files = get_files_from_path(path)
    logger.debug("Files list: %s", files)

    runids = _ingest_files(
        state.config,
        manifest_files,
        files,
        runid_log,
        batch_size,
        wait,
        skip_existing,
        simulate,
        legal_tags,
        acl_owners,
        acl_viewers,
    )
    print(runids)
    return runids


def _ingest_files(  # noqa:C901 pylint: disable=too-many-arguments
    config: CLIConfig,
    manifest_files,
    files,
    runid_log,
    batch_size,
    wait,
    skip_existing,
    simulate,
    legal_tags,
    acl_owners,
    acl_viewers,
):
    logger.debug("Files list: %s", manifest_files)
    runids = []
    runid_log_handle = None
    try:  # pylint: disable=too-many-try-statements
        if runid_log is not None and not simulate:
            # clear existing logs
            runid_log_handle = open(runid_log, "w", encoding="utf-8")  # pylint: disable=consider-using-with

        data_objects = []
        for filepath in manifest_files:
            if filepath.endswith(".json"):
                with open(filepath, encoding="utf-8") as file:
                    json_string = file.read()
                    # for reference data do replacements (acl, legal happens later)
                    json_string = json_string.replace(
                        "{{NAMESPACE}}", config.get("core", CONFIG_DATA_PARTITION_ID)
                    )
                    json_data = json.loads(json_string)

                    if not json_data:
                        logger.error("Error with file %s. File is empty.", filepath)
                    else:
                        logger.info("Processing %s.", filepath)

                        if isinstance(json_data, list):
                            _ingest_json_as_sequence_file(
                                config,
                                files,
                                runid_log,
                                batch_size,
                                skip_existing,
                                simulate,
                                runids,
                                json_data,
                                legal_tags,
                                acl_owners,
                                acl_viewers,
                            )

                        else:
                            # Note this code currently assumes only one of MasterData, ReferenceData or Data exists!
                            if "ReferenceData" in json_data and len(json_data["ReferenceData"]) > 0:  # noqa: E501 pylint: disable=else-if-used
                                _update_legal_and_acl_tags_all(
                                    config,
                                    json_data["ReferenceData"],
                                    legal_tags,
                                    acl_owners,
                                    acl_viewers,
                                )
                                if batch_size is None and not skip_existing:
                                    _create_and_submit(
                                        config, json_data, runids, runid_log_handle, simulate
                                    )
                                else:
                                    data_objects += json_data["ReferenceData"]
                                    file_batch_size = (
                                        len(data_objects)
                                        if skip_existing and not batch_size
                                        else batch_size
                                    )
                                    data_objects = _process_batch(
                                        config,
                                        file_batch_size,
                                        "ReferenceData",
                                        data_objects,
                                        runids,
                                        runid_log_handle,
                                        skip_existing,
                                        simulate,
                                    )
                            elif "MasterData" in json_data and len(json_data["MasterData"]) > 0:
                                _update_legal_and_acl_tags_all(
                                    config,
                                    json_data["MasterData"],
                                    legal_tags,
                                    acl_owners,
                                    acl_viewers,
                                )
                                if batch_size is None and not skip_existing:
                                    _create_and_submit(
                                        config, json_data, runids, runid_log_handle, simulate
                                    )
                                else:
                                    data_objects += json_data["MasterData"]
                                    file_batch_size = (
                                        len(data_objects)
                                        if skip_existing and not batch_size
                                        else batch_size
                                    )
                                    data_objects = _process_batch(
                                        config,
                                        file_batch_size,
                                        "MasterData",
                                        data_objects,
                                        runids,
                                        runid_log_handle,
                                        skip_existing,
                                        simulate,
                                    )
                            elif "Data" in json_data:
                                _update_work_products_metadata(
                                    config,
                                    json_data["Data"],
                                    files,
                                    simulate,
                                    legal_tags,
                                    acl_owners,
                                    acl_viewers,
                                )
                                _create_and_submit(
                                    config, json_data, runids, runid_log_handle, simulate
                                )
                            else:
                                logger.error(
                                    "No manifest ReferenceData, MasterData or Data section"
                                    " found in %s.",
                                    filepath,
                                )
            else:
                logger.warning("Skipping %s - no .json extension.", filepath)

    finally:
        if runid_log_handle is not None:
            runid_log_handle.close()

    if wait and not simulate:
        logger.debug("%d batches submitted. Waiting for run status", len(runids))
        check_status(config, runids, True)
    return runids


def _ingest_json_as_sequence_file(
    config,
    files,
    runid_log,
    batch_size,
    skip_existing,
    simulate,
    runids,
    sequence_file,
    legal_tags,
    acl_owners,
    acl_viewers,
):  # pylint: disable=too-many-arguments
    logger.info(
        "Processing as sequence file. Will wait for each entry to complete before submitting new."
    )

    if all(isinstance(entry, dict) and "FileName" in entry for entry in sequence_file):
        for entry in sequence_file:
            _sequence_run_ids = _ingest_files(
                config,
                get_files_from_path(entry["FileName"]),
                files,
                runid_log,
                batch_size,
                True,
                skip_existing,
                simulate,
                legal_tags,
                acl_owners,
                acl_viewers,
            )
            runids.extend(_sequence_run_ids)
    else:
        logger.error("Invalid sequence file.")


def _process_batch(
    config, batch_size, data_type, data_objects, runids, runid_log_handle, skip_existing, simulate
):
    if skip_existing:
        ids_to_verify = []
        found = []
        not_found = []
        original_length = len(data_objects)
        for data in data_objects:
            if "id" in data:
                ids_to_verify.append(data.get("id"))
        batch_verify(config, VERIFY_BATCH_SIZE, ids_to_verify, found, not_found, True)
        data_objects = [
            data for data in data_objects if "id" in data and data.get("id") in not_found
        ]
        logger.info(
            "%i of %i records already exist. Submitting %i records",
            len(found),
            original_length,
            len(data_objects),
        )

    while len(data_objects) > 0:
        total_size = len(data_objects)
        batch_size = min(batch_size, total_size)
        current_batch = data_objects[:batch_size]
        del data_objects[:batch_size]
        print(
            f"Processing batch - total {total_size}, batch size {len(current_batch)}, remaining"
            f" {len(data_objects)}"
        )

        manifest = {"kind": "osdu:wks:Manifest:1.0.0", data_type: current_batch}
        _create_and_submit(config, manifest, runids, runid_log_handle, simulate)

    return data_objects


def _create_and_submit(config, manifest, runids, runid_log_handle, simulate):
    request_data = _populate_request_body(config, manifest)
    if not simulate:
        connection = CliOsduClient(config)
        response_json = connection.cli_post_returning_json(
            CONFIG_WORKFLOW_URL, "workflow/Osdu_ingest/workflowRun", request_data
        )
        logger.debug("Response %s", response_json)

        runid = response_json.get("runId")
        logger.info("Returned runID: %s", runid)
        if runid_log_handle:
            runid_log_handle.write(f"{runid}\n")
        runids.append(runid)


def _populate_request_body(config: CLIConfig, manifest):
    request = {
        "executionContext": {
            "Payload": {
                "AppKey": "osdu-cli",
                "data-partition-id": config.get("core", CONFIG_DATA_PARTITION_ID),
            },
            "manifest": manifest,
        }
    }
    logger.debug("Request to be sent %s", json.dumps(request, indent=2))
    return request


def _upload_file(config: CLIConfig, filepath):
    connection = CliOsduClient(config)

    initiate_upload_response_json = connection.cli_get_returning_json(
        CONFIG_FILE_URL, "files/uploadURL"
    )
    location = initiate_upload_response_json.get("Location")

    if location:
        signed_url_for_upload = location.get("SignedURL")
        file_source = location.get("FileSource")

        headers = {"Content-Type": "application/octet-stream", "x-ms-blob-type": "BlockBlob"}
        with open(filepath, "rb") as file_handle:
            # pylint: disable=missing-timeout
            response = requests.put(signed_url_for_upload, data=file_handle, headers=headers)
            if response.status_code not in [200, 201]:
                raise CliError(f"({response.status_code}) {response.text[:250]}")

        # Need to figure how metadata is handled wrt. ariflow, fileid (returned v's manifest)
        # file_metadata = _populate_file_metadata_req_body(file_source)
        # _update_legal_and_acl_tags(config, file_metadata)
        # print(file_metadata)
        # update_metadata_response = connection.cli_post_returning_json(
        #     CONFIG_FILE_URL,
        #     "files/metadata",
        #     json.dumps(file_metadata),
        #     [200, 201],
        # )

        # generated_file_id = update_metadata_response.get("id")
        # logger.info(
        #     f"{filepath} is uploaded with file id {generated_file_id} with file source {file_source}"
        # )

        # # Get record version

        # file_record_version_response = connection.cli_get_returning_json(
        #     CONFIG_STORAGE_URL, "records/versions/" + generated_file_id
        # )
        # file_record_version = file_record_version_response.get("versions")[0]

        # metadata = {
        #     "file_id": generated_file_id,
        #     "file_source": file_source,
        #     "file_record_version": str(file_record_version),
        # }
        # print(metadata)

        # generated_file_id = upload_metadata_response_json.get("id")
        logger.info("%s is uploaded with file source %s", filepath, file_source)
        # return generated_file_id, file_source
        return file_source

    raise CliError(f"No upload location returned: {initiate_upload_response_json}")


def _populate_file_metadata_req_body(file_source):
    return {
        "kind": "osdu:wks:dataset--File.Generic:1.0.0",
        "acl": {
            "viewers": [],
            "owners": [],
        },
        "legal": {
            "legaltags": [],
            "otherRelevantDataCountries": ["US"],
            "status": "compliant",
        },
        "data": {"DatasetProperties": {"FileSourceInfo": {"FileSource": file_source}}},
    }


def _update_work_products_metadata(
    config: CLIConfig,
    data,
    files,
    simulate,
    legal_tags: list[str],
    acl_owners: list[str],
    acl_viewers: list[str],
):
    if "WorkProduct" in data:
        _update_legal_and_acl_tags(config, data["WorkProduct"], legal_tags, acl_owners, acl_viewers)
    if "WorkProductComponents" in data:
        _update_legal_and_acl_tags_all(
            config, data["WorkProductComponents"], legal_tags, acl_owners, acl_viewers
        )
    if "Datasets" in data:  # pylint: disable=too-many-nested-blocks
        _update_legal_and_acl_tags_all(
            config, data["Datasets"], legal_tags, acl_owners, acl_viewers
        )

        # if files is specified then upload any needed data.
        if files:
            for dataset in data.get("Datasets"):
                file_source_info = (
                    dataset.get("data", {}).get("DatasetProperties", {}).get("FileSourceInfo")
                )
                # only process if FileSource isn't already specified

                if file_source_info:
                    file_path = os.path.join(files, file_source_info["Name"])
                    if os.path.exists(file_path):
                        if not simulate:
                            file_source_info["FileSource"] = _upload_file(config, file_path)
                    else:
                        logger.info(
                            "Local file '%s' not found - skipping.",
                            file_path,
                        )

    # TO DO: Here we scan by name from filemap
    # with open(file_location_map) as file:
    #     location_map = json.load(file)

    # file_name = data["WorkProduct"]["data"]["Name"]
    # if file_name in location_map:
    #     file_source = location_map[file_name]["file_source"]
    #     file_id = location_map[file_name]["file_id"]

    #     # Update Dataset with Generated File Id and File Source.
    #     data["Datasets"][0]["id"] = file_id
    #     data["Datasets"][0]["data"]["DatasetProperties"]["FileSourceInfo"]["FileSource"] = file_source
    #     del data["Datasets"][0]["data"]["DatasetProperties"]["FileSourceInfo"]["PreloadFilePath"]

    #     # Update FileId in WorkProductComponent
    #     data["WorkProductComponents"][0]["data"]["Datasets"][0] = file_id
    # else:
    #     logger.warn(f"Filemap {file_name} does not exist")

    # logger.debug(f"data to upload workproduct \n {data}")


def _update_legal_and_acl_tags_all(
    config: CLIConfig,
    data,
    legal_tags: list[str] = None,
    acl_owners: list[str] = None,
    acl_viewers: list[str] = None,
):
    for _data in data:
        _update_legal_and_acl_tags(config, _data, legal_tags, acl_owners, acl_viewers)


def _update_legal_and_acl_tags(  # noqa: C901
    config: CLIConfig,
    data,
    legal_tags: list[str] = None,
    acl_owners: list[str] = None,
    acl_viewers: list[str] = None,
):
    # Update legal tags if needed
    if legal_tags is not None:
        if len(legal_tags) == 0:
            legal_tags = [config.get("core", CONFIG_LEGAL_TAG)]
        data["legal"]["legaltags"] = legal_tags
    else:
        for legal_tag in data["legal"]["legaltags"]:
            if re.search("^{{.*}}$", legal_tag):
                raise CliError(
                    f"Found a legal tag placeholder {legal_tag}. Use the -l option to replace"
                    " these."
                )

    # Update legal country
    data["legal"]["otherRelevantDataCountries"] = ["US"]

    # Update acl owners tags if needed
    if acl_owners is not None:
        if len(acl_owners) == 0:
            acl_owners = [config.get("core", CONFIG_ACL_OWNER)]
        data["acl"]["owners"] = acl_owners
    else:
        for acl_owner in data["acl"]["owners"]:
            if re.search("^{{.*}}$", acl_owner):
                raise CliError(
                    f"Found an acl owner placeholder {acl_owner}. Use the -aclo option to replace"
                    " these."
                )

    # Update acl viewers if needed
    if acl_viewers is not None:
        if len(acl_viewers) == 0:
            acl_viewers = [config.get("core", CONFIG_ACL_VIEWER)]
        data["acl"]["viewers"] = acl_viewers
    else:
        for acl_viewer in data["acl"]["viewers"]:
            if re.search("^{{.*}}$", acl_viewer):
                raise CliError(
                    f"Found an acl viewer placeholder {acl_viewer}. Use the -aclv option to replace"
                    " these."
                )
