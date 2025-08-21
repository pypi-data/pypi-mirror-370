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

"""Read and modify configuration settings related to the CLI"""

import logging
from enum import IntEnum

CLI_LOGGER_NAME = "cli"
# Add more logger names to this list so that ERROR, WARNING, INFO logs from these loggers can also be displayed
# without --debug flag.
cli_logger_names = [CLI_LOGGER_NAME]

LOG_FILE_ENCODING = "utf-8"


class CliLogLevel(IntEnum):
    """[summary]

    Args:
        IntEnum ([type]): [description]
    """

    CRITICAL = 0
    ERROR = 1
    WARNING = 2
    INFO = 3
    DEBUG = 4


def get_logger(module_name=None):
    """Get the logger for a module. If no module name is given, the current CLI logger is returned.

    Example:
        get_logger(__name__)

    :param module_name: The module to get the logger for
    :type module_name: str
    :return: The logger
    :rtype: logger
    """
    if module_name:
        logger_name = f"{CLI_LOGGER_NAME}.{module_name}"
    else:
        logger_name = CLI_LOGGER_NAME
    return logging.getLogger(logger_name)
