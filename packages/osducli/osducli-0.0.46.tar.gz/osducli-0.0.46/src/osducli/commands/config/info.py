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

"""Config info command"""

import os

import click

from osducli.click_cli import CustomClickCommand, global_params
from osducli.cliclient import handle_cli_exceptions
from osducli.commands.config.consts import (
    MSG_HEADING_CURRENT_CONFIG_INFO,
    MSG_HEADING_ENV_VARS,
)
from osducli.config import CLI_ENV_VAR_PREFIX, CLIConfig


@click.command(cls=CustomClickCommand)
@global_params
@handle_cli_exceptions
def _click_command(state):
    # def _click_command(ctx, debug, config, hostname):
    """Configuration info"""
    config_info(state)


def print_cur_configuration(cli_config: CLIConfig):
    """Print the current configuration

    Args:
        cli_config (CLIConfig): CLIConfig
    """

    print("TODO: accesses config_parser file directly - might show actual used values instead")
    print(MSG_HEADING_CURRENT_CONFIG_INFO)
    if cli_config.config_parser:
        for section in cli_config.config_parser.sections():
            print()
            print(f"[{section}]")
            for name, value in cli_config.config_parser.items(section):
                print(f"{name} = {value}")
        env_vars = [ev for ev in os.environ if ev.startswith(CLI_ENV_VAR_PREFIX)]
        if env_vars:
            print(MSG_HEADING_ENV_VARS)
            print("\n".join([f"{ev} = {os.environ[ev]}" for ev in env_vars]))
    else:
        print(f"No config file found at {cli_config.config_path}. run osdcli ")
        print("Try running 'osdcli config update' or 'osdcli config set'")


def config_info(state):
    """Show configuration

    Args:
        state (State): Global state
    """
    print_cur_configuration(state.config)
