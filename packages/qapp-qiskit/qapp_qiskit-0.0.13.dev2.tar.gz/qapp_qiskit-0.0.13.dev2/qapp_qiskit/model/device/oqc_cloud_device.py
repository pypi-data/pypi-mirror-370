"""
    QApp Platform Project ibm_cloud_device.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
#  Quapp Platform Project
#  oqc_cloud_device.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from abc import ABC
from time import time

from qcaas_client.client import QPUTask, CompilerConfig
from qiskit.qasm2 import dumps
from quapp_common.config.logging_config import logger
from quapp_common.data.device.circuit_running_option import CircuitRunningOption
from quapp_common.enum.status.job_status import JobStatus
from quapp_common.model.device.custom_device import CustomDevice
from quapp_common.model.provider.provider import Provider


class OqcCloudDevice(CustomDevice, ABC):

    def __init__(self, provider: Provider, device_specification: str):
        super().__init__(provider, device_specification)

        self.device_specification = device_specification

    def _create_job(self, circuit, options: CircuitRunningOption):
        self.logger.debug(f'Creating job with {options.shots} shots')

        start_time = time()

        qasm_str = dumps(circuit)
        circuit_submit_options = CompilerConfig(repeats=options.shots)
        self.logger.debug(f'QASM string: {qasm_str}')

        task = QPUTask(program=qasm_str, config=circuit_submit_options)
        self.logger.debug(f'Task created successfully: {task}')

        job = self.device.execute_tasks(task, qpu_id=self.device_specification)
        self.logger.debug(f'Job created successfully: {job}')

        self.execution_time = time() - start_time

        return job

    def _is_simulator(self) -> bool:
        self.logger.debug('Checking if simulator')
        self.logger.debug(f'Simulator: {True}')
        return True

    def _produce_histogram_data(self, job_result) -> dict | None:
        self.logger.debug('Producing histogram data')
        histogram = next(iter(job_result.result.values()))
        self.logger.debug(f'Histogram data produced successfully: {histogram}')
        return histogram

    def _get_provider_job_id(self, job) -> str:
        self.logger.debug('Get provider job id')
        provider_job_id = job[0].id
        self.logger.debug(f'Provider job id: {provider_job_id}')
        return provider_job_id

    def _get_job_status(self, job) -> str:
        self.logger.debug('Get job status')
        oqc_status = self.device.get_task_status(task_id=job[0].id,
                                                 qpu_id=self.device_specification)
        self.logger.debug(f'Job status resolved to: {oqc_status}')

        if "FAILED".__eq__(oqc_status):
            self.logger.info("Job failed")
            return JobStatus.ERROR.value
        elif "COMPLETED".__eq__(oqc_status):
            self.logger.info("Job completed")
            return JobStatus.DONE.value

        self.logger.info("Job is still running")
        return oqc_status

    def _calculate_execution_time(self, job_result):
        self.logger.debug('Calculate execution time')
        self.logger.debug(
                f'Execution time calculation was: {self.execution_time} seconds')

    def _get_job_result(self, job):
        self.logger.debug('Getting job result')
        job_result = job[0]
        self.logger.info(f'Job result fetched successfully: {job_result}')
        return job_result

    def _get_shots(self, job_result) -> int | None:
        self.logger.debug('Getting shots')
        result_classical = job_result.result.get('classical')
        if result_classical is not None:
            logger.debug(f'Classical results found: {result_classical}')
            total_shots = sum(value for value in result_classical.values())
            self.logger.debug(f'Total shots: {total_shots}')
            return total_shots

        logger.debug('No classical results found.')
        return None
