#  Quapp Platform Project
#  braket_provider_factory.py
#  Copyright © CITYNOW Co. Ltd.All rights reserved.

from quapp_common.config.logging_config import logger
from quapp_common.enum.provider_tag import ProviderTag
from quapp_common.enum.sdk import Sdk

from ..constant.authentication_const import ACCESS_KEY, ACCESS_TOKEN, REGION_NAME, SECRET_KEY, URL
from ..model.provider.aws_braket_provider import AwsBraketProvider
from ..model.provider.oqc_cloud_provider import OqcCloudProvider
from ..model.provider.qapp_braket_provider import QuappBraketProvider
from ..util.braket_utils import verify_credentials

logger = logger.bind(context='BraketProviderFactory')


def create_provider(provider_type: ProviderTag, sdk: Sdk, authentication: dict):
    logger.info("create_provider()")

    if ProviderTag.QUAO_QUANTUM_SIMULATOR.__eq__(provider_type) and Sdk.BRAKET.__eq__(sdk):
        logger.debug("Create QuappBraketProvider")

        return QuappBraketProvider()

    if ProviderTag.AWS_BRAKET.__eq__(provider_type):

        verify_credentials(authentication)
        return AwsBraketProvider(authentication.get(ACCESS_KEY), authentication.get(SECRET_KEY),
                                 authentication.get(REGION_NAME), )

    if ProviderTag.OQC_CLOUD.__eq__(provider_type):
        return OqcCloudProvider(
            authentication.get(URL),
            authentication.get(ACCESS_TOKEN)
        )

    logger.error(f"Unsupported provider: {provider_type}")
    raise ValueError("Unsupported provider!")
