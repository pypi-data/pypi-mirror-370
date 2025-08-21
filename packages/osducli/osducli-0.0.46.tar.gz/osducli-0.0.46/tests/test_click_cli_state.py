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

"""Test cases for click_cli State"""

from osducli.click_cli import State


def test_init():
    """Test the init method"""
    state = State()

    assert state.debug is False
    assert state.config_path is None
    assert state.config is None
    assert state.output is None
    assert state.jmes is None

def test_user_friendly_mode():
    """Test the init method"""
    state = State()

    user_friendly = state.is_user_friendly_mode()
    assert user_friendly is True

def test_user_friendly_mode_output_set():
    """Test the init method"""
    state = State()
    state.output = "json"

    user_friendly = state.is_user_friendly_mode()
    assert user_friendly is False
