#  Quapp Platform Project
#  aws_braket_provider.py
#  Copyright © CITYNOW Co. Ltd.All rights reserved.

from braket.aws import AwsDevice, AwsSession
from quapp_common.config.logging_config import logger
from quapp_common.enum.provider_tag import ProviderTag
from quapp_common.model.provider.provider import Provider

from ...util.braket_utils import create_boto3_session

logger = logger.bind(context='AwsBraketProvider')


class AwsBraketProvider(Provider):

    def __init__(self, aws_access_key, aws_secret_access_key, region_name):
        super().__init__(ProviderTag.AWS_BRAKET)
        self.aws_access_key = aws_access_key
        self.aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name

    def get_backend(self, device_specification: str):
        logger.debug('get_backend()')

        session = self.collect_provider()

        return AwsDevice(
            arn=device_specification,
            aws_session=session)

    def collect_provider(self):
        logger.debug('collect_provider()')

        session = create_boto3_session(access_key=self.aws_access_key,
                                       secret_key=self.aws_secret_access_key,
                                       region_name=self.region_name)
        return AwsSession(boto_session=session)
