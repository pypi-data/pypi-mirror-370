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

"""Test cases for CliOsduClient"""

import json
from unittest.mock import MagicMock, Mock

import pytest
from osdu_api.clients.base_client import BaseClient
from osdu_api.model.http_method import HttpMethod

from osducli.cliclient import CliOsduClient
from osducli.config import CONFIG_AUTHENTICATION_MODE
from tests.helpers import MockConfig, mock_config_values

SAMPLE_JSON = {
    "name": "value",
}


def mock_config_values_invalid_auth(section, name, fallback=None):  # pylint: disable=W0613
    """Validate and mock config returns"""
    if name == CONFIG_AUTHENTICATION_MODE:
        return "invalid"

    return mock_config_values(section, name, fallback)


MOCK_CONFIG_INVALID_AUTH = MagicMock()
MOCK_CONFIG_INVALID_AUTH.get.side_effect = mock_config_values_invalid_auth

@pytest.fixture
def cli_client(mocker):
    mocker.patch.object(BaseClient, "__init__", return_value=MagicMock())
    yield CliOsduClient(MockConfig)

def test_init(cli_client):
    """Test the init method"""
    assert cli_client.server_url == mock_config_values("core", "server")
    #assert cli_client.data_partition_id == mock_config_values("core", "data_partition_id")

def test_init_invalid_auth():
    """Test the init method"""
    with pytest.raises(SystemExit):
        CliOsduClient(MOCK_CONFIG_INVALID_AUTH)

# region test cli_get
@pytest.mark.parametrize("config, path",
    [("config", "/path"),
    ("config", "/path1"),
    ("config2", "path2")]
)
def test_cli_get(mocker, cli_client, config, path):
    """Test valid get with string returns expected values"""
    response_mock = Mock()
    response_mock.status_code = 200
    mock_get = mocker.patch.object(cli_client, "make_request", return_value=response_mock)

    response = cli_client.cli_get(config, path)

    mock_get.assert_called_once()
    mock_get.assert_called_with(method=HttpMethod.GET, url="https://dummy.com/core_" + config + path)
    assert response_mock == response

def test_cli_get_defaults(mocker, cli_client):
    """Test valid get with string returns expected values"""
    response_mock = Mock()
    response_mock.status_code = 200
    mock_get = mocker.patch.object(cli_client, "make_request", return_value=response_mock)

    response = cli_client.cli_get("config", "/path")

    mock_get.assert_called_once()
    mock_get.assert_called_with(method=HttpMethod.GET, url="https://dummy.com/core_config/path")
    assert response_mock == response

@pytest.mark.parametrize("ok_status_codes, actual_status_code",
    [(None, 200),  # No status codes passed then all should be ok
    #(None, 404),  # No status codes passed then all should be ok
    ([200], 200),
    ([200, 202], 202),
    ([202], 202)]
)
def test_cli_get_status_codes(mocker, cli_client, ok_status_codes, actual_status_code):
    """Test valid get returns expected values"""
    response_mock = Mock()
    response_mock.status_code = actual_status_code
    mock_get = mocker.patch.object(cli_client, "make_request", return_value=response_mock)

    response = cli_client.cli_get("config", "/path", ok_status_codes)

    mock_get.assert_called_once()
    assert response_mock == response

# endregion test cli_get

# region test cli_post_returning_json
@pytest.mark.parametrize("config, path, string_data, status_codes",
    [("config", "/path", "string1", None),
    ("config", "/path1", "string1", None),
    ("config", "/path2", "string1", None),
    ("config", "/path2", "string2", None),
    ("config2", "path2", "string2", None),
    ("config2", "path2", "string2", [200])]
)
def test_cli_post_returning_json(mocker, cli_client, config, path, string_data, status_codes):
    """Test valid post with string returns expected values"""
    response_mock = Mock()
    response_mock.status_code = 200
    response_mock.json.return_value = {"key": "value"}
    mock_post = mocker.patch.object(cli_client, "make_request", return_value=response_mock)

    response = cli_client.cli_post_returning_json(config, path, string_data, status_codes)

    mock_post.assert_called_once()
    mock_post.assert_called_with(method=HttpMethod.POST, url="https://dummy.com/core_" + config + path , data=string_data)
    assert response_mock.json() == response

def test_cli_post_returning_json_defaults(mocker, cli_client):
    """Test valid post with string returns expected values"""
    response_mock = Mock()
    response_mock.status_code = 200
    response_mock.json.return_value = {"key": "value"}
    mock_post = mocker.patch.object(cli_client, "make_request", return_value=response_mock)

    response = cli_client.cli_post_returning_json("config", "/path", "data")

    mock_post.assert_called_once()
    mock_post.assert_called_with(method=HttpMethod.POST, url="https://dummy.com/core_config/path", data="data")
    assert response_mock.json() == response

# endregion test cli_post_returning_json

# region test cli_put
@pytest.mark.parametrize("config, path, data",
    [("config", "/path", "string1"),
    ("config", "/path1", "string1"),
    ("config", "/path2", "string1"),
    ("config", "/path2", "string2"),
    ("config2", "path2", "string2"),
    ("config2", "path2", "string2"),
    ("config2", "path2", SAMPLE_JSON)]
)
def test_cli_put(mocker, cli_client, config, path, data):
    """Test valid put with string returns expected values"""
    response_mock = Mock()
    response_mock.status_code = 200
    mock_put = mocker.patch.object(cli_client, "make_request", return_value=response_mock)

    response = cli_client.cli_put(config, path, data)

    mock_put.assert_called_once()
    if isinstance(data, dict):
        data = json.dumps(data)
    mock_put.assert_called_with(method=HttpMethod.PUT, url="https://dummy.com/core_" + config + path, data=data)
    assert response_mock == response

def test_cli_put_defaults(mocker, cli_client):
    """Test valid put with string returns expected values"""
    response_mock = Mock()
    response_mock.status_code = 200
    mock_put = mocker.patch.object(cli_client, "make_request", return_value=response_mock)

    response = cli_client.cli_put("config", "/path", "data")

    mock_put.assert_called_once()
    mock_put.assert_called_with(method=HttpMethod.PUT, url="https://dummy.com/core_config/path", data="data")
    assert response_mock == response

@pytest.mark.parametrize("ok_status_codes, actual_status_code",
    [(None, 200),  # No status codes passed then all should be ok
    #(None, 404),  # No status codes passed then all should be ok
    ([200], 200),
    ([200, 202], 202),
    ([202], 202)]
)
def test_cli_put_status_codes(mocker, cli_client, ok_status_codes, actual_status_code):
    """Test valid put returns expected values"""
    response_mock = Mock()
    response_mock.status_code = actual_status_code
    mock_put = mocker.patch.object(cli_client, "make_request", return_value=response_mock)

    response = cli_client.cli_put("config", "/path", SAMPLE_JSON, ok_status_codes)

    mock_put.assert_called_once()
    assert response_mock == response

# endregion test cli_put

# region test cli_delete

@pytest.mark.parametrize("config, path",
    [("config", "/path"),
    ("config", "/path1")]
)
def test_cli_delete(mocker, cli_client, config, path):
    """Test valid delete returns expected values"""
    response_mock = Mock()
    response_mock.status_code = 200
    mock_delete = mocker.patch.object(cli_client, "make_request", return_value=response_mock)
    mock_token_refresher = mocker.Mock()
    mock_token_refresher.refresh_token.return_value = "some-token"
    cli_client.token_refresher = mock_token_refresher

    response = cli_client.cli_delete(config, path)

    mock_delete.assert_called_once()
    mock_delete.assert_called_with(method=HttpMethod.DELETE, url="https://dummy.com/core_" + config + path, bearer_token="some-token")
    assert response_mock == response

@pytest.mark.parametrize("ok_status_codes, actual_status_code",
    [(None, 200),  # No status codes passed then all should be ok
    #(None, 404),  # No status codes passed then all should be ok
    ([200], 200),
    ([200, 202], 202),
    ([202], 202)]
)
def test_cli_delete_status_codes(mocker, cli_client, ok_status_codes, actual_status_code):
    """Test valid put returns expected values"""
    response_mock = Mock()
    response_mock.status_code = actual_status_code
    mock_delete = mocker.patch.object(cli_client, "make_request", return_value=response_mock)
    mock_token_refresher = mocker.Mock()
    mock_token_refresher.refresh_token.return_value = "some-token"
    cli_client.token_refresher = mock_token_refresher

    response = cli_client.cli_delete("config", "/path", ok_status_codes)

    mock_delete.assert_called_once()
    mock_delete.assert_called_with(method=HttpMethod.DELETE, url="https://dummy.com/core_config/path", bearer_token="some-token")
    assert response_mock == response

# endregion test cli_delete

# region test cli_put_returning_json
@pytest.mark.parametrize("config, path, string_data, status_codes",
    [("config", "/path", "string1", None),
    ("config", "/path1", "string1", None),
    ("config", "/path2", "string1", None),
    ("config", "/path2", "string2", None),
    ("config2", "path2", "string2", None),
    ("config2", "path2", "string2", [200])]
)
def test_cli_put_returning_json(mocker, cli_client, config, path, string_data, status_codes):
    """Test valid put with string returns expected values"""
    response_mock = Mock()
    response_mock.status_code = 200
    response_mock.json.return_value = {"key": "value"}
    mock_put = mocker.patch.object(cli_client, "make_request", return_value=response_mock)

    response = cli_client.cli_put_returning_json(config, path, string_data, status_codes)

    mock_put.assert_called_once()
    mock_put.assert_called_with(method=HttpMethod.PUT, url="https://dummy.com/core_" + config + path, data=string_data)
    assert response_mock.json() == response

def test_cli_put_returning_json_defaults(mocker, cli_client):
    """Test valid put with string returns expected values"""
    response_mock = Mock()
    response_mock.status_code = 200
    response_mock.json.return_value = {"key": "value"}
    mock_put = mocker.patch.object(cli_client, "make_request", return_value=response_mock)

    response = cli_client.cli_put_returning_json("config", "/path", "data")

    mock_put.assert_called_once()
    mock_put.assert_called_with(method=HttpMethod.PUT, url="https://dummy.com/core_config/path", data="data")
    assert response_mock.json() == response

# endregion test cli_put_returning_json
