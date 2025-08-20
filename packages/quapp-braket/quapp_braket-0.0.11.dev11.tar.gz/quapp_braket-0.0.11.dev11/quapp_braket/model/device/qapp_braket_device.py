#  Quapp Platform Project
#  qapp_braket_device.py
#  Copyright © CITYNOW Co. Ltd.All rights reserved.

import time

from quapp_common.data.device.circuit_running_option import CircuitRunningOption
from quapp_common.enum.status.job_status import JobStatus
from quapp_common.model.device.custom_device import CustomDevice
from quapp_common.model.provider.provider import Provider

from ...constant.job_result_const import SHOTS, TASK_METADATA


class QuappBraketDevice(CustomDevice):

    def __init__(self, provider: Provider, device_specification: str):
        super().__init__(provider, device_specification)

    def _create_job(self, circuit, options: CircuitRunningOption):
        self.logger.debug(
                'Creating job on device with circuit: {circuit}, options: {options}')
        start_time = time.time()

        self.logger.debug('Submitting job')
        job = self.device.run(task_specification=circuit, shots=options.shots)

        self.execution_time = time.time() - start_time

        self.logger.debug('Submitting job completed')
        return job

    def _produce_histogram_data(self, job_result) -> dict:
        self.logger.info(
                f'Producing histogram data for job_result: {job_result}')
        result = dict(job_result.measurement_counts)
        self.logger.debug(f'Produced histogram data: {result}')
        return result

    def _get_provider_job_id(self, job) -> str:
        self.logger.debug(f'Getting provider job id for job: {job}')
        job_id = job.id
        self.logger.info(f'Provider job id: {job_id}')
        return job_id

    def _get_job_status(self, job) -> str:
        self.logger.info(f'Getting job status for job: {job}')

        job_state = job.state()
        self.logger.debug(f'Raw job state: {job_state}')

        if JobStatus.COMPLETED.value.__eq__(job_state):
            self.logger.info('Job state is COMPLETED, marking as DONE')
            job_state = JobStatus.DONE.value

        self.logger.info(f'Returned job state: {job_state}')
        return job_state

    def _is_simulator(self) -> bool:
        self.logger.info("Device is simulator.")
        return True

    def _calculate_execution_time(self, job_result):
        self.logger.debug(
                f'Calculating execution time for job_result: {job_result}')

        self.logger.info(
                f"Execution time calculation was: {self.execution_time} seconds")

    def _get_job_result(self, job):
        self.logger.debug(f'Getting job result for job: {job}')

        while job.state() not in ['COMPLETED', 'FAILED', 'CANCELLED']:
            self.logger.debug(f'Job status (waiting): {job.state()}')
            time.sleep(2)

        self.logger.debug(f'Job status (final): {job.state()}')

        result = job.result()
        self.logger.info(f'Job result received: {result}')
        return result

    def _get_shots(self, job_result) -> int | None:
        """
        Retrieve the number of shots from the job result.

        This method checks if the job result contains task metadata and
        retrieves the number of shots if available. If task metadata
        does not exist or does not contain the shot attribute,
        the method returns None.

        Args:
            job_result: An object representing the result of a job, which
                        may contain task metadata.

        Returns:
            int | None: The number of shots if available; otherwise, None.
        """
        self.logger.debug(f'Getting shots from job_result: {job_result}')

        if hasattr(job_result, TASK_METADATA) and hasattr(
                job_result.task_metadata, SHOTS):
            shots = job_result.task_metadata.shots
            self.logger.debug(f"Shots retrieved: {shots}")
            return shots
        self.logger.warning(
                "Shots attribute not found in job_result's task_metadata.")
        return None
