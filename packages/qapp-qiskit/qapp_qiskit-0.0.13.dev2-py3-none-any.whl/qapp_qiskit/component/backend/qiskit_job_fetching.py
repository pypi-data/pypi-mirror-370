#  Quapp Platform Project
#  qiskit_job_fetching.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from quapp_common.component.backend.job_fetching import JobFetching
from quapp_common.data.request.job_fetching_request import JobFetchingRequest
from quapp_common.enum.provider_tag import ProviderTag
from quapp_common.enum.sdk import Sdk

from ...factory.qiskit_provider_factory import QiskitProviderFactory


class QiskitJobFetching(JobFetching):

    def __init__(self, request_data: JobFetchingRequest):
        super().__init__(request_data)

    def _collect_provider(self, ):
        try:
            self.logger.debug(
                    f'Collecting provider with provider_type={ProviderTag.IBM_QUANTUM}, '
                    f'sdk={Sdk.QISKIT}')
            provider = QiskitProviderFactory.create_provider(
                    provider_type=ProviderTag.IBM_QUANTUM, sdk=Sdk.QISKIT,
                    authentication=self.provider_authentication, ).collect_provider()
            self.logger.info('Provider collected successfully')
            return provider
        except Exception as exception:
            self.logger.exception(f'Failed to collect provider: {exception}')
            raise

    def _retrieve_job(self, provider):
        try:
            self.logger.debug(
                    f'Retrieving job with job_id={self.provider_job_id}')
            job = provider.job(job_id=self.provider_job_id)
            self.logger.info('Job retrieved successfully')
            return job
        except Exception as exception:
            self.logger.exception(f'Failed to retrieve job '
                                  f'{self.provider_job_id}: {exception}')
            raise

    def _get_job_status(self, job):
        self.logger.debug('Getting job status')
        try:
            status = job.status()
            self.logger.debug(f'Job status: {status}')
            return status
        except Exception as exception:
            self.logger.exception(f'Failed to get job status for job_id='
                                  f'{self.provider_job_id}: '
                                  f'{exception}')
            raise

    def _get_job_result(self, job):
        self.logger.info("_get_job_result()")
        try:
            self.logger.debug("Returning raw job object for job_id=%s",
                              self.provider_job_id)
            return job
        except Exception as exception:
            self.logger.exception("Failed to get job result for job_id=%s: %s",
                                  self.provider_job_id, e)
            raise
