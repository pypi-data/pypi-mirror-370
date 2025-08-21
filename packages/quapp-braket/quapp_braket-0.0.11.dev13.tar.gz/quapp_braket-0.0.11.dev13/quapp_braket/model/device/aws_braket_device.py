#  Quapp Platform Project
#  aws_braket_device.py
#  Copyright © CITYNOW Co. Ltd.All rights reserved.

from dateutil.parser import parse
from quapp_common.data.device.circuit_running_option import CircuitRunningOption
from quapp_common.model.provider.provider import Provider

from ...constant.job_result_const import CREATED_AT, ENDED_AT, TASK_METADATA
from ...model.device.qapp_braket_device import QuappBraketDevice


class AwsBraketDevice(QuappBraketDevice):

    def __init__(self, provider: Provider, device_specification: str,
                 s3_bucket_name: str, s3_prefix: str):
        super().__init__(provider, device_specification)
        self.s3_folder = (s3_bucket_name, s3_prefix)
        self.logger.debug(
                f'Initialized AwsBraketDevice: s3_folder={self.s3_folder}, provider={provider}, device_specification={device_specification}')

    def _create_job(self, circuit, options: CircuitRunningOption):
        self.logger.debug(
                f'Creating job on device {self.device} with circuit: {circuit}, options: {options}, s3_folder: {self.s3_folder}')

        job = self.device.run(task_specification=circuit,
                              s3_destination_folder=self.s3_folder,
                              shots=options.shots)

        self.logger.info(f'Job created: {job}')
        return job

    def _calculate_execution_time(self, job_result):
        self.logger.debug(
                f'Calculating execution time for job_result: {job_result}')

        if TASK_METADATA not in job_result:
            self.logger.warning(f'{TASK_METADATA} not found in job_result')
            return

        task_metadata = job_result[TASK_METADATA]

        if task_metadata is None or not bool(
                task_metadata) or CREATED_AT not in task_metadata or ENDED_AT not in task_metadata:
            self.logger.warning(
                    'Task metadata missing or incomplete; cannot calculate execution time.')
            return

        created_at = task_metadata[CREATED_AT]
        ended_at = task_metadata[ENDED_AT]

        if created_at is None or ended_at is None:
            self.logger.warning(
                    'Created/ended time is None; cannot calculate execution time.')
            return

        created_at = parse(created_at.replace('T', ' ').replace('Z', ''))
        ended_at = parse(ended_at.replace('T', ' ').replace('Z', ''))

        offset = ended_at - created_at

        self.execution_time = offset.total_seconds()

        self.logger.info(
                f'Execution time calculation was: {self.execution_time} seconds')
