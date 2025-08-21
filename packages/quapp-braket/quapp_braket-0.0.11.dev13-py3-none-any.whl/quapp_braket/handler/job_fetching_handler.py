#  Quapp Platform Project
#  job_fetching_handler.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.
from abc import ABC

from quapp_common.config.logging_config import logger
from quapp_common.data.request.job_fetching_request import JobFetchingRequest
from quapp_common.handler.handler import Handler

from ..component.backend.braket_job_fetching import BraketJobFetching

logger = logger.bind(context='JobFetchingHandler')


class JobFetchingHandler(Handler, ABC):
    def __init__(self, request_data: dict, post_processing_fn):
        super().__init__(request_data, post_processing_fn)

    def handle(self) -> None:
        self.logger.debug(
                f"Creating JobFetchingRequest with data: {self.request_data}")
        invocation_request = JobFetchingRequest(self.request_data)

        self.logger.debug("Initializing BraketJobFetching backend")
        job_fetching = BraketJobFetching(invocation_request)

        self.logger.debug("Starting job fetch operation")
        fetching_result = job_fetching.fetch(
                post_processing_fn=self.post_processing_fn)

        self.logger.info(
                f"Fetch operation completed with result: {fetching_result}")
        return fetching_result
