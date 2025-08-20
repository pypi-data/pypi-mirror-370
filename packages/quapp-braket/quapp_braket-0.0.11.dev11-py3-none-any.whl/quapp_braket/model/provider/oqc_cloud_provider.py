#  Quapp Platform Project
#  oqc_cloud_provider.py
#  Copyright © CITYNOW Co. Ltd.All rights reserved.

from qcaas_client.client import OQCClient
from quapp_common.config.logging_config import logger
from quapp_common.enum.provider_tag import ProviderTag
from quapp_common.model.provider.provider import Provider

logger = logger.bind(context='OqcCloudProvider')


class OqcCloudProvider(Provider):

    def __init__(self, oqc_cloud_url: str, access_token: str):
        super().__init__(ProviderTag.OQC_CLOUD)
        self.oqc_cloud_url = oqc_cloud_url
        self.access_token = access_token

    def get_backend(self, device_specification):
        logger.debug("get_backend()")

        return self.collect_provider()

    def collect_provider(self):
        logger.debug("collect_provider()")

        return OQCClient(url=self.oqc_cloud_url, authentication_token=self.access_token)
