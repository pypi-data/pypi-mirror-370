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

"""Entry or launch point for CLI."""

import importlib
import os.path
import pkgutil

import click

from osducli.click_cli import CustomClickGroup, CustomMainClickGroup, State


def get_commands_from_pkg(pkg) -> dict:
    """Dynamically and recursively get all click commands within the specified package

    Args:
        pkg ([type]): [description]

    Returns:
        dict: [description]
    """
    # groups with only 1 command that should be kept as groups for future expandability
    keep_groups = [
        "osducli.commands.legal",
        "osducli.commands.list",
        "osducli.commands.unit",
    ]
    pkg_obj = importlib.import_module(pkg)

    pkg_path = os.path.dirname(pkg_obj.__file__)
    commands = {}
    for module in pkgutil.iter_modules([pkg_path]):
        module_obj = importlib.import_module(f"{pkg}.{module.name}")

        if not module.ispkg:
            if hasattr(module_obj, "_click_command"):
                commands[module.name] = module_obj._click_command
                # print(f"Add command {pkg}.{module.name}")

        else:
            group_commands = get_commands_from_pkg(f"{pkg}.{module.name}")
            if len(group_commands) == 1 and f"{pkg}.{module.name}" not in keep_groups:
                # print(f"Add command {pkg}.{module.name} - {module.name.replace('_', '-')}")
                click_command = list(group_commands.values())[0]
                click_command.context_settings["help_option_names"] = ["-h", "--help"]
                commands[module.name.replace("_", "-")] = click_command
            elif len(group_commands) >= 1:
                # print(f"Add group {module.name.replace('_', '-')}\n{group_commands}")
                commands[module.name.replace("_", "-")] = CustomClickGroup(
                    context_settings={"help_option_names": ["-h", "--help"]},
                    help=module_obj.__doc__,
                    commands=group_commands,
                )
            # else:
            #     print(f"Skip group {module.name.replace('_', '-')}")

    return commands


# Main entry point for OSDU CLI.
# noqa: W606,W605
@click.group(
    cls=CustomMainClickGroup,
    commands=get_commands_from_pkg("osducli.commands"),
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.pass_context
def cli(ctx):
    """
    \b
      ___   ____   ____   _   _     ____  _      ___
     / _ \\ / ___| |  _ \\ | | | |   / ___|| |    |_ _|
    | | | |\\___ \\ | | | || | | |  | |    | |     | |
    | |_| | ___) || |_| || |_| |  | |___ | |___  | |
     \\___/ |____/ |____/  \\___/    \\____||_____||___|
    Welcome to the OSDU CLI!

    \033[33mNote: This is currently a work in progress and may contain bugs or breaking changes.
    Please share ideas / issues on the git page:
    \b

    https://community.opengroup.org/osdu/platform/data-flow/data-loading/osdu-cli/-/issues\033[39m

    Use `osdu version` to display the current version.

    Usage:
    osdu [command]
    """
    ctx.obj = State()


def main():
    """Main entry point for OSDU CLI."""
    cli(None)


if __name__ == "__main__":
    main()
