#  Quapp Platform Project
#  invocation_handler.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from quapp_common.data.request.invocation_request import InvocationRequest
from quapp_common.handler.handler import Handler

from ..component.backend.qiskit_invocation import QiskitInvocation


class InvocationHandler(Handler):
    def __init__(self, request_data: dict, circuit_preparation_fn,
                 post_processing_fn):
        super().__init__(request_data, post_processing_fn)
        self.circuit_preparation_fn = circuit_preparation_fn

    def handle(self):
        self.logger.debug('Handle Invocation: start')
        try:

            invocation_request = InvocationRequest(self.request_data)
            self.logger.debug(f'Invocation request created successfully: '
                              f'{invocation_request.__dict__.keys()}')

            backend = QiskitInvocation(invocation_request)
            self.logger.info('Submitting job via QiskitInvocation')

            backend.submit_job(
                    circuit_preparation_fn=self.circuit_preparation_fn,
                    post_processing_fn=self.post_processing_fn)

            self.logger.debug('Job submission triggered successfully')
        except Exception as exception:
            self.logger.exception(f'Invocation handling failed: {exception}')
            raise
