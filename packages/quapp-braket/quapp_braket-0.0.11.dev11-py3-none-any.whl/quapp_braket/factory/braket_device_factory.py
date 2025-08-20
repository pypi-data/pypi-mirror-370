#  Quapp Platform Project
#  braket_device_factory.py
#  Copyright © CITYNOW Co. Ltd.All rights reserved.

from quapp_common.config.logging_config import logger
from quapp_common.enum.provider_tag import ProviderTag
from quapp_common.enum.sdk import Sdk
from quapp_common.model.provider.provider import Provider

from quapp_braket.constant.authentication_const import BUCKET_NAME, PREFIX
from quapp_braket.model.device.aws_braket_device import AwsBraketDevice
from quapp_braket.model.device.oqc_cloud_device import OqcCloudDevice
from quapp_braket.model.device.qapp_braket_device import QuappBraketDevice

logger = logger.bind(context='BraketDeviceFactory')


def create_device(provider: Provider, device_specification: str, authentication: dict, sdk: Sdk):
    logger.info("Creating device")

    # Validate inputs
    if not isinstance(provider, Provider):
        logger.error("Invalid provider: %s", type(provider).__name__)
        raise ValueError(f"provider must be a Provider instance, got {type(provider).__name__}")
    if not isinstance(device_specification, str):
        logger.error("Invalid device_specification: %s", type(device_specification).__name__)
        raise ValueError(
            f"device_specification must be a string, got {type(device_specification).__name__}")
    if not isinstance(sdk, Sdk):
        logger.error("Invalid sdk: %s", type(sdk).__name__)
        raise ValueError(f"sdk must be an Sdk instance, got {type(sdk).__name__}")

    provider_type = ProviderTag.resolve(provider.get_provider_type().value)
    logger.debug(f"Resolved provider_type: {provider_type}")

    if provider_type == ProviderTag.QUAO_QUANTUM_SIMULATOR and sdk == Sdk.BRAKET:
        logger.info("Creating QuappBraketDevice")
        device = QuappBraketDevice(provider, device_specification)
        logger.info("QuappBraketDevice created successfully")
        return device

    if provider_type == ProviderTag.AWS_BRAKET:
        if not isinstance(authentication, dict):
            logger.error(f"Invalid authentication: {type(authentication).__name__}")
            raise ValueError(
                f"authentication must be a dictionary, got {type(authentication).__name__}")

        bucket = authentication.get(BUCKET_NAME)
        prefix = authentication.get(PREFIX)
        if bucket is None or prefix is None:
            logger.error("Missing AWS authentication details - bucket: %s, prefix: %s", bucket,
                         prefix)
            raise ValueError(
                f"AWS authentication requires {BUCKET_NAME} and {PREFIX}, got bucket={bucket}, prefix={prefix}")
        logger.debug(f"AWS authentication details - bucket: {bucket}, prefix: {prefix}")
        logger.info("Creating AwsBraketDevice")
        device = AwsBraketDevice(provider, device_specification, bucket, prefix)
        logger.info("AwsBraketDevice created successfully")
        return device

    if provider_type == ProviderTag.OQC_CLOUD:
        logger.info("Creating OqcCloudDevice")
        device = OqcCloudDevice(provider, device_specification)
        logger.info("OqcCloudDevice created successfully")
        return device

    logger.error(f"Unsupported device for provider_type: {provider_type}, sdk: {sdk}")
    raise ValueError(f"Unsupported device for provider_type={provider_type}, sdk={sdk}")
