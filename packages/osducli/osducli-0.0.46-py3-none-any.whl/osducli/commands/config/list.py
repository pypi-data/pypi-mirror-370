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

"""Config list command"""

import os

import click

from osducli.click_cli import CustomClickCommand, global_params
from osducli.cliclient import handle_cli_exceptions
from osducli.config import CLIConfig


@click.command(cls=CustomClickCommand)
@global_params
@handle_cli_exceptions
def _click_command(state):
    # def _click_command(ctx, debug, config, hostname):
    """List available configurations"""
    config_list(state)


def list_configurations(cli_config: CLIConfig):
    """List the configurations

    Args:
        cli_config (CLIConfig): CLIConfig
    """
    if os.path.exists(cli_config.config_dir):
        try:
            files = os.listdir(cli_config.config_dir)
            if files:
                print(f"Configuration files available in {cli_config.config_dir}:")
                list_config_files(cli_config.config_file_name, files)
            else:
                warn_config_missing(cli_config.config_dir)
        except OSError:
            warn_config_missing(cli_config.config_dir)


def list_config_files(current_filename: str, files: list[str]):
    """List configuration files"""
    for file in files:
        if file not in ("state", "msal_token_cache.bin"):
            if file == current_filename:
                print(file + "  <== (Currently using)")
            else:
                print(file)


def warn_config_missing(config_dir: str):
    """Warn missing configuration"""
    print(f"No config file found at {config_dir}.")
    print("Try running 'osdu config update' or 'osdu config set'")


def config_list(state):
    """List configurations

    Args:
        state (State): Global state
    """
    list_configurations(state.config)
