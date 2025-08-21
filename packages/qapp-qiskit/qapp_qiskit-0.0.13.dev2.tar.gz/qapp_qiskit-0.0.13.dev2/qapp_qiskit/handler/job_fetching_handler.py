#  Quapp Platform Project
#  job_fetching_handler.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from quapp_common.data.request.job_fetching_request import JobFetchingRequest
from quapp_common.handler.handler import Handler

from ..component.backend.qiskit_job_fetching import QiskitJobFetching


class JobFetchingHandler(Handler):
    def __init__(self, request_data: dict, post_processing_fn):
        super().__init__(request_data, post_processing_fn)

    def handle(self):
        self.logger.debug('Handle JobFetching: start')

        request = JobFetchingRequest(self.request_data)
        self.logger.debug(
                f'JobFetching request created successfully: {request.__dict__.keys()}')

        job_fetching = QiskitJobFetching(request)
        self.logger.info('Job fetching initiated')

        self.logger.debug('Job fetching started')
        fetching_result = job_fetching.fetch(
                post_processing_fn=self.post_processing_fn)
        self.logger.debug('Job fetching finished')

        return fetching_result
