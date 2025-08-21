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

"""Client for Wellbore DDMS API in the template of osdu-api clients"""

import requests
from osdu_api.auth.authorization import TokenRefresher
from osdu_api.clients.base_client import BaseClient
from osdu_api.configuration.base_config_manager import BaseConfigManager
from osdu_api.model.http_method import HttpMethod

from osducli.log import get_logger

logger = get_logger(__name__)


class WellboreDdmsClient(BaseClient):
    """
    Client for interacting with Wellbore DDMS
    """
    def __init__(
            self,
            wellbore_ddms_url: str = None,
            config_manager: BaseConfigManager = None,
            provider: str = None,
            data_partition_id: str = None,
            token_refresher: TokenRefresher = None,
            user_id: str = None
    ):
        super().__init__(config_manager, provider, data_partition_id, token_refresher, logger, user_id)
        self.wellbore_ddms_url = wellbore_ddms_url or self.config_manager.get('environment', 'wellbore_ddms_url')

    def get_well_log(self, record_id: str = None) -> requests.Response:
        """Get wellLog record from wellbore ddms by id"""
        return self.make_request(method=HttpMethod.GET, url=f'{self.wellbore_ddms_url}/{record_id}')

    def create_well_log(self, record_data_list: str = None) -> requests.Response:
        """Create wellLog record with wellbore ddms"""
        return self.make_request(method=HttpMethod.POST, url=self.wellbore_ddms_url, data=record_data_list)

    def get_well_log_data(self, record_id: str) -> requests.Response:
        """Get wellLog composite parquet from wellbore ddms"""
        return self.make_request(method=HttpMethod.GET, url=f'{self.wellbore_ddms_url}/{record_id}/data')

    def create_well_log_data(self, record_id: str, data: str = '') -> requests.Response:
        """Create wellLog composite parquet with wellbore ddms"""
        additional_header = {'Content-Type': 'application/x-parquet'}
        return self.make_request(method=HttpMethod.POST, url=f'{self.wellbore_ddms_url}/{record_id}/data',
                                 add_headers=additional_header, data=data)
