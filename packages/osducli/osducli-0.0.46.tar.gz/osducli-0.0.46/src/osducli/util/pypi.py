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

import requests

from osducli.log import get_logger

logger = get_logger(__name__)


def get_pypi_version(package: str) -> str:
    """Get the latest version of a package from pypi

    Args:
        package (str): Package name

    Returns:
        str: Version number or None if unable to retrieve.
    """
    try:
        response = requests.get(f"https://pypi.org/pypi/{package}/json", timeout=20)
        if response.status_code == 200:
            data = response.json()
            return data["info"]["version"]
    except Exception as ex:  # pylint: disable=broad-except
        logger.debug(ex, exc_info=True)

    return None
