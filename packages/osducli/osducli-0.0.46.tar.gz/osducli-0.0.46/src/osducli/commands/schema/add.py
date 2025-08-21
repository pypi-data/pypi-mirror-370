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
import os
from pathlib import Path

import click

from osducli.click_cli import CustomClickCommand, State, command_with_output
from osducli.cliclient import CliOsduClient, handle_cli_exceptions
from osducli.config import CONFIG_SCHEMA_URL
from osducli.log import get_logger
from osducli.util.exceptions import CliError
from osducli.util.file import get_files_from_path

logger = get_logger(__name__)


# click entry point
@click.command(cls=CustomClickCommand)
@click.option(
    "-p",
    "--path",
    help="Path to a schema or schemas to add.",
    required=True,
)
@click.option(
    "-k",
    "--kind",
    help="Kind of the schema. Inferred from schemaInfo property if not specified.",
)
@click.option(
    "--status",
    help="Status of the schema.",
    default="DEVELOPMENT",
    show_default=True,
)
@click.option(
    "--overwrite-existing",
    help="Overwrite any existing schema with the same version.",
    is_flag=True,
    show_default=True,
)
@click.option(
    "--self-contained",
    help="Make the schema self contained by including all references.",
    is_flag=True,
    show_default=True,
)
@handle_cli_exceptions
@command_with_output(None)
def _click_command(
    state: State, path: str, kind: str, status: str, overwrite_existing: bool, self_contained: bool
):
    """Add a schema"""
    return add_schema(state, path, kind, status, overwrite_existing, self_contained)


def add_schema(
    state: State, path: str, kind: str, status: str, overwrite_existing: bool, self_contained: bool
) -> dict:
    """Add schemas to OSDU

    Args:
        state (State): Global state
        path (str): Path to a schema or schemas to add.
        kind (str): Kind of the schema.
        status (str): Status of the schema.
        overwrite_existing (bool): Overwrite any existing schema
        self_contained (bool): Make the schema self contained by including all references.

    Returns:
        dict: Response from service
    """
    connection = CliOsduClient(state.config)
    url = "schema"

    files = get_files_from_path(path)
    logger.debug("Files list: %s", files)

    responses = []
    for filepath in files:
        if filepath.endswith(".json"):
            with open(filepath, encoding="utf-8") as file:
                schema_object = json.load(file)

                logger.info("Processing file %s.", filepath)

                if kind is None:
                    if "x-osdu-schema-source" in schema_object:
                        kind = schema_object["x-osdu-schema-source"]
                        logger.debug("Kind determined as %s", kind)

                #     kind = _kind_from_schema_info(schema_object)
                if kind is None:
                    raise CliError(
                        f"Kind not specified for {filepath} and could not determine schema"
                        " kind from schemaInfo property."
                    )

                if self_contained:
                    _make_self_contained(schema_object, Path(filepath).parent)
                schema_info = _get_schema_info(kind, status)
                payload = {"schemaInfo": schema_info, "schema": schema_object}

                response_json = None
                if overwrite_existing:
                    response_json = connection.cli_put_returning_json(
                        CONFIG_SCHEMA_URL, url, payload, [200, 201]
                    )
                else:
                    response_json = connection.cli_post_returning_json(
                        CONFIG_SCHEMA_URL, url, payload, [200, 201]
                    )
                responses.append(response_json)

    return responses


def _make_self_contained(schema_object, folder):
    all_references = set()
    # references_to_check = set()

    # _get_refs_in_schema_recursive(schema_object, None, all_references, None)

    # check_new_refs(schema_object, folder, all_references)

    # while len(references_to_check) > 0:
    #     ref = references_to_check.pop()
    #     if ref not in all_references:
    #         referenced_file_path = folder.joinpath(ref)
    #         with open(referenced_file_path) as referenced_file:
    #             referenced_schema_object = json.load(referenced_file)
    #             schema_object["definitions"][path_to_reference(ref)] = referenced_schema_object
    #         check_new_refs(schema_object, folder, all_references)

    #         pass

    if "definitions" not in schema_object:
        schema_object["definitions"] = {}
    for ref in all_references:
        referenced_file_path = folder.joinpath(ref)
        with open(referenced_file_path, encoding="utf-8") as referenced_file:
            referenced_schema_object = json.load(referenced_file)

            schema_object["definitions"][_path_to_reference(ref)] = referenced_schema_object
    print(json.dumps(schema_object))
    return all_references


def _check_new_refs(schema_object, filepath, all_references):
    for ref in all_references:
        referenced_file_path = Path(filepath).parent.joinpath(ref)
        new_references = set()
        _get_refs_in_schema_recursive(schema_object, None, new_references, None)
        new_references = new_references - all_references
        with open(referenced_file_path, encoding="utf-8") as referenced_file:
            referenced_schema_object = json.load(referenced_file)
            schema_object["definitions"][_path_to_reference(ref)] = referenced_schema_object


def _get_refs_in_schema_recursive(obj, key, refs, parent):
    if isinstance(obj, dict):
        for _k, _v in obj.items():
            _get_refs_in_schema_recursive(_v, _k, refs, obj)
    elif isinstance(obj, list):
        for list_item in obj:
            _get_refs_in_schema_recursive(list_item, None, refs, obj)
    elif key == "$ref":
        refs.add(obj)
        parent[key] = f"#/definitions/{_path_to_reference(obj)}"


def _path_to_reference(obj):
    ref = (
        "osdu:wks:" + os.path.splitext(os.path.basename(obj))[0]
    )  # obj.replace("../abstract/", "").replace(".json", "")
    return ref


def _get_schema_info(kind: str, status: str):
    kind_parts = kind.split(":")
    if len(kind_parts) != 4:
        raise CliError(
            f"Kind '{kind}' is not in the correct format 'authority:source:entity:v:v:v'"
        )
    version = kind_parts[3].split(".")
    if len(version) != 3:
        raise CliError(
            f"Kind '{kind}' is not in the correct format 'authority:source:entity:v:v:v'"
        )

    schema_info = {
        "schemaIdentity": {
            "authority": kind_parts[0],
            "source": kind_parts[1],
            "entityType": kind_parts[2],
            "schemaVersionMajor": version[0],
            "schemaVersionMinor": version[1],
            "schemaVersionPatch": version[2],
        },
        "createdBy": "osducli",
        "status": status,
    }
    return schema_info


def _kind_from_schema_info(schema: dict) -> str:
    try:  # pylint: disable=too-many-try-statements
        _si = schema.get("schemaInfo", {}).get("schemaIdentity", {})
        authority = _si.get("authority", "")
        source = _si.get("source", "")
        entity = _si.get("entityType", "")
        major = str(_si.get("schemaVersionMajor", 0))
        minor = str(_si.get("schemaVersionMinor", 0))
        patch = str(_si.get("schemaVersionPatch", 0))
        return f"{authority}:{source}:{entity}:{major}.{minor}.{patch}"
    except Exception:  # pylint: disable=broad-except
        return None
