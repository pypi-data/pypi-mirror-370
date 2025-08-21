#  Quapp Platform Project
#  qiskit_device.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from abc import ABC

from qiskit import QiskitError
from quapp_common.model.device.custom_device import CustomDevice


class QiskitDevice(CustomDevice, ABC):

    def _produce_histogram_data(self, job_result) -> dict | None:
        self.logger.debug('Producing histogram data')

        try:
            histogram_data = job_result.get_counts()
            self.logger.debug(f'Histogram data produced successfully: '
                              f'{histogram_data}')
            return histogram_data
        except QiskitError as qiskit_error:
            self.logger.debug(
                    f"Can't produce histogram data due to QiskitError: "
                    f"{str(qiskit_error)}. Returning None")
            return None
        except Exception as exception:
            self.logger.exception(
                    f'Unexpected error while producing histogram data: {exception}')
            return None

    def _get_provider_job_id(self, job) -> str:
        self.logger.debug('Get provider job id')
        try:
            job_id = job.job_id()
            self.logger.debug(f'Provider job id: {job_id}')
            return job_id
        except Exception as exception:
            self.logger.exception(f'Failed to get provider job id: {exception}')
            raise

    def _get_job_status(self, job) -> str:
        self.logger.debug('Get job status')

        try:
            status = str(job.status()).split(".")[-1]
            self.logger.debug(f'Job status resolved to: {status}')
            return status
        except Exception as exception:
            self.logger.exception(f'Failed to get job status: {exception}')
            raise

    def _calculate_execution_time(self, job_result):
        self.logger.debug('Calculate execution time')

        try:
            if "metadata" not in job_result:
                self.logger.debug("No 'metadata' key found in job_result")
                return None

            metadata = job_result["metadata"]
            if not metadata:
                self.logger.debug('Empty or None metadata in job_result')
                return None

            if "time_taken_execute" not in metadata:
                self.logger.debug(
                        "'time_taken_execute' not present in metadata")
                return None

            self.execution_time = metadata["time_taken_execute"]
            self.logger.debug(
                    f'Execution time calculation was: {self.execution_time} seconds')
            return None
        except Exception as exception:
            self.logger.exception(
                    f'Failed to calculate execution time: {exception}')
            return None

    def _get_job_result(self, job):
        self.logger.debug('Getting job result')
        try:
            result = job.result()
            self.logger.debug('Result fetched successfully')
            return result
        except Exception as exception:
            self.logger.exception(f'Failed to fetch job result: {exception}')
            raise

    def _get_shots(self, job_result) -> int | None:
        """
        Get the number of shots used in the job.

        :param job_result:
        :return: The number of shots used in the job if available, otherwise None.
        """
        try:
            if not job_result.results:
                self.logger.debug('No results found in job_result')
                return None

            first_result = job_result.results[0]
            if first_result is None:
                self.logger.debug('First result is None')
                return None

            shots = first_result.shots
            self.logger.debug(f'Number of shots: {shots}')
            return shots
        except Exception as exception:
            self.logger.exception(
                    f'Failed to get shots from job_result: {exception}')
            return None
