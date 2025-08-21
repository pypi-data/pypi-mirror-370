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

import errno
import glob
import os


def get_files_from_path(path: str) -> list:
    """Given a path get a list of all files.

    Args:
        path (str): path

    Returns:
        list: list of file paths
    """
    allfiles = []
    if os.path.isfile(path):
        allfiles = [path]

    # Recursive traversal of files and subdirectories of the root directory and files processing
    for root, _, files in os.walk(path):
        for file in files:
            allfiles.append(os.path.join(root, file))
    return allfiles


def get_files_from_path_with_suffix(path: str, suffix: str) -> list:
    """Given a path get a list of all files with a certain suffix.

    Args:
        path (str): path
        suffix (str): file suffix to filter by

    Returns:
        list: list of file paths
    """
    if os.path.isfile(path):
        return [path] if path.endswith(suffix) else []

    pattern = os.path.join(path, '**', f'*{suffix}')
    return glob.glob(pattern, recursive=True)


def ensure_directory_exists(directory: str):
    """Create a directory if it doesn't exist"""
    if not os.path.isdir(directory):
        try:
            os.makedirs(directory)
        except OSError as _e:
            if _e.errno != errno.EEXIST:
                raise _e
