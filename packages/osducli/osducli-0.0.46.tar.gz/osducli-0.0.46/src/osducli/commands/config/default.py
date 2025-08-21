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

"""config default command"""
import os.path
from pathlib import Path

import click

from osducli.click_cli import CustomClickCommand, State, global_params
from osducli.cliclient import handle_cli_exceptions
from osducli.state import get_default_config_path, set_default_config_path
from osducli.util.prompt import prompt


# click entry point
@click.command(cls=CustomClickCommand)
@handle_cli_exceptions
@global_params
def _click_command(state: State):
    """Set the default config file"""
    config_default(state)


def config_default(state: State):
    """Set the default config file

    Args:
        state (State): Global state
    """
    config_file = get_default_config_path()
    default_config_file = get_default_config_path(locate=True)

    if config_file:
        print(f"Currently using '{config_file}'")
    elif default_config_file:
        print(f"Currently using default config '{default_config_file}'")

    if state.config_path is None:
        config_file = prompt("What config file should be the default: ")
    else:
        config_file = state.config_path

    if config_file:
        if Path(config_file).is_file():
            print(f"Setting default config to: '{config_file}'")
            set_default_config_path(config_file)
        else:
            config_file = state.config.config_dir + os.path.sep + config_file
            if Path(config_file).is_file():
                print(f"Setting default config to: '{config_file}'")
                set_default_config_path(config_file)
            else:
                print("The specified file was not found. Run osdu config update to add configuration values.")
    else:
        print("No changes made!")
