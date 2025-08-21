"""
    QApp Platform Project ibm_cloud_device.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
#  Quapp Platform Project
#  oqc_cloud_device.py
#  Copyright © CITYNOW Co. Ltd.All rights reserved.

from time import time

from qcaas_client.client import CompilerConfig, QPUTask
from qiskit.qasm2 import dumps
from quapp_common.data.device.circuit_running_option import CircuitRunningOption
from quapp_common.enum.status.job_status import JobStatus
from quapp_common.model.provider.provider import Provider

from quapp_braket.constant.job_result_const import MEAS
from quapp_braket.constant.job_status_const import COMPLETED, FAILED
from quapp_braket.model.device.qapp_braket_device import QuappBraketDevice
from quapp_braket.util.circuit_convert_utils import braket_to_qiskit


class OqcCloudDevice(QuappBraketDevice):

    def __init__(self, provider: Provider, device_specification: str):
        super().__init__(provider, device_specification)
        self.device_specification = device_specification

    def _create_job(self, circuit, options: CircuitRunningOption):
        self.logger.debug(
                'Creating job on device with circuit: {circuit}, options: {options}')

        start_time = time()

        self.logger.debug('Converting braket circuit to qiskit circuit')
        qiskit_circuit = braket_to_qiskit(circuit)
        self.logger.info(
                'Converting braket circuit to qiskit circuit completed')

        self.logger.debug('Submitting job to OQC Cloud')
        qiskit_circuit.measure_all()
        qasm_str = dumps(qiskit_circuit)
        circuit_submit_options = CompilerConfig(repeats=options.shots)
        task = QPUTask(program=qasm_str, config=circuit_submit_options)
        self.logger.debug('Submitting job to OQC Cloud completed')

        self.logger.debug('Executing job on OQC Cloud')
        job = self.device.execute_tasks(task, qpu_id=self.device_specification)

        self.execution_time = time() - start_time

        self.logger.debug('Executing job on OQC Cloud completed')
        return job

    def _produce_histogram_data(self, job_result) -> dict | None:
        self.logger.info(
                f'Producing histogram data for job_result: {job_result}')

        result = next(iter(job_result.values()))
        self.logger.debug(f'Produced histogram data: {result}')
        return result

    def _get_provider_job_id(self, job) -> str:
        self.logger.debug(f'Getting provider job id for job: {job}')
        job_id = job[0].id
        self.logger.info(f'Provider job id: {job_id}')
        return job_id

    def _get_job_status(self, job) -> str:
        self.logger.info(f'Getting job status for job: {job}')

        oqc_status = self.device.get_task_status(task_id=job[0].id,
                                                 qpu_id=self.device_specification)
        self.logger.debug(f'Raw job state: {oqc_status}')

        if FAILED.__eq__(oqc_status):
            self.logger.info('Job state is FAILED, marking as ERROR')
            return JobStatus.ERROR.value
        elif COMPLETED.__eq__(oqc_status):
            self.logger.info('Job state is COMPLETED, marking as DONE')
            return JobStatus.DONE.value

        self.logger.info(f'Returned job state: {oqc_status}')
        return oqc_status

    def _get_job_result(self, job):
        self.logger.debug(f'Getting job result for job: {job}')
        result = job[0].result
        self.logger.info(f'Job result received: {result}')
        return result

    def _get_shots(self, job_result) -> int | None:
        """
        Retrieve the total number of measurement shots from the job result.

        This method checks if the job result contains measurement data
        and calculates the total number of shots based on the measurement
        results. If the measurement data is not available, the method
        returns None.

        Args:
            job_result: An object representing the result of a job, which
                        may contain measurement results under the 'result'
                        attribute.

        Returns:
            int | None: The total number of shots if measurement data is
                         available; otherwise, None.
        """
        self.logger.debug(f'Getting shots from job_result: {job_result}')
        result_meas = getattr(job_result, MEAS, {})
        shots = sum(result_meas.values()) if result_meas else None
        self.logger.debug(f'Calculated shots: {shots}')
        return shots
