#  Quapp Platform Project
#  qapp_braket_provider.py
#  Copyright © CITYNOW Co. Ltd.All rights reserved.

from braket.devices import LocalSimulator

from quapp_common.config.logging_config import logger
from quapp_common.enum.provider_tag import ProviderTag
from quapp_common.model.provider.provider import Provider

logger = logger.bind(context='QuappBraketProvider')


class QuappBraketProvider(Provider):

    def __init__(self, ):
        super().__init__(ProviderTag.QUAO_QUANTUM_SIMULATOR)

    def get_backend(self, device_specification):
        logger.debug('get_backend()')

        provider = self.collect_provider()

        device_names = provider.registered_backends()

        if device_names.__contains__(device_specification):
            return LocalSimulator(device_specification)

        raise ValueError('Unsupported device')

    def collect_provider(self):
        logger.debug('collect_provider()')

        return LocalSimulator()
