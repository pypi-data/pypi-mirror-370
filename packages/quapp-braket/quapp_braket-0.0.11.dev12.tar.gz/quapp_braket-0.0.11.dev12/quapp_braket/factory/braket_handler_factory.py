#  Quapp Platform Project
#  braket_handler_factory.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from quapp_common.config.logging_config import job_logger
from quapp_common.factory.handler_factory import HandlerFactory
from quapp_common.handler.handler import Handler

from ..handler.invocation_handler import InvocationHandler
from ..handler.job_fetching_handler import JobFetchingHandler
from ..util.provider_job_utils import is_valid_job_arn, \
    is_valid_quantum_task_arn


class BraketHandlerFactory(HandlerFactory):

    @staticmethod
    def create_handler(event, circuit_preparation_fn,
                       post_processing_fn) -> Handler:

        request_data = event.request if event and hasattr(event,
                                                          'request') else event.json()

        logger = job_logger(request_data.get('jobId'))
        logger.debug('Creating handler')

        provider_job_id = request_data.get('providerJobId')

        if provider_job_id is None:
            logger.info("No providerJobId found, returning InvocationHandler")
            return InvocationHandler(request_data=request_data,
                                     circuit_preparation_fn=circuit_preparation_fn,
                                     post_processing_fn=post_processing_fn, )

        logger.debug(f'Found providerJobId: {provider_job_id}')
        if is_valid_quantum_task_arn(provider_job_id) or is_valid_job_arn(
                provider_job_id):
            logger.info(
                    "Valid providerJobId found, returning JobFetchingHandler")
            return JobFetchingHandler(request_data=request_data,
                                      post_processing_fn=post_processing_fn)

        logger.error(f'Invalid providerJobId: {provider_job_id}')
        raise ValueError(f"Invalid providerJobId: {provider_job_id}")
