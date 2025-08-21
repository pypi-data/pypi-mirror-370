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

"""Read and modify state related to the CLI"""

import os
from os import path

from osducli.config import CLI_CONFIG_DIR, CLI_ENV_VAR_PREFIX, CLI_NAME, CLIConfig

# CLIConfig has all the functionality needed to keep track of state, so we are using that
# here to prevent code duplication. We are using CLIConfig to create a file called 'state' to
# track states associated with osducli, such as the last time osducli version was checked.

# Default names
CLI_STATE_DIR = os.path.expanduser(os.path.join("~", f".{CLI_NAME}"))
STATE_FILE_NAME = "state"

# Format: Year, month, day, hour, minute, second, microsecond
DATETIME_FORMAT = "Year %Y Month %m Day %d %H:%M:%S:%f"


def get_state_path():
    """
    Returns the path of where the state file of osducli is stored.
    :return: str
    """

    return CLIConfig(CLI_STATE_DIR, CLI_ENV_VAR_PREFIX, STATE_FILE_NAME).config_path


def get_state_value(name, fallback=None):
    """Gets a state entry by name.

    In the case where the state entry name is not found, will use fallback value."""

    cli_config = CLIConfig(CLI_STATE_DIR, CLI_ENV_VAR_PREFIX, STATE_FILE_NAME)

    return cli_config.get("core", name, fallback)


def set_state_value(name, value):
    """
    Set a state entry with a specified a value.

    Args:
        name (str): Name of the state.
        value (str): Value of the state.
    """
    cli_config = CLIConfig(CLI_STATE_DIR, CLI_ENV_VAR_PREFIX, STATE_FILE_NAME)
    cli_config.set_value("core", name, value)


def get_default_config_path(locate: bool = False) -> str:
    """Get the path of the default config file.

    Args:
        locate (bool): Whether to try and locate the default config file. Defaults to False

    Returns:
        str: Path to config, or None if not in state
    """
    config_path = get_state_value("default_config")
    if not config_path and locate:
        config_path = CLIConfig(CLI_CONFIG_DIR, CLI_ENV_VAR_PREFIX).config_path  # noqa: E501 pylint:disable=redefined-variable-type
    return config_path


def get_default_config(locate: bool = False) -> CLIConfig:
    """Get the path of the default config file.

    Args:
        locate (bool): Whether to try and locate the default config file. Defaults to False

    Returns:
        CLIConfig: CLIConfig, or None if nothing found / set
    """
    default_config = get_default_config_path(locate)
    default_config_path, default_config_file = path.split(default_config)
    return CLIConfig(default_config_path, CLI_ENV_VAR_PREFIX, default_config_file)


def set_default_config_path(default_config: str = None):
    """Set the default config file.

    Args:
        default_config (str, optional): path of default config file. Defaults to None.
    """
    set_state_value("default_config", default_config)
