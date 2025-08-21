#  Quapp Platform Project
#  qapp_qiskit_provider.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from qiskit_aer import Aer
from quapp_common.config.logging_config import job_logger

from quapp_common.enum.provider_tag import ProviderTag
from quapp_common.model.provider.provider import Provider

logger = job_logger('QappQiskitProvider')


class QappQiskitProvider(Provider):

    def __init__(self, ):
        super().__init__(ProviderTag.QUAO_QUANTUM_SIMULATOR)

    def get_backend(self, device_specification):
        logger.debug('Get backend from Qapp Qiskit')

        provider = self.collect_provider()

        device_names = {self.__map_aer_backend_name(backend_name) for
                        backend_name in provider.backends()}

        if device_names.__contains__(device_specification):
            backend = provider.get_backend(device_specification)
            logger.debug(f'Backend: {backend}')
            return backend

        logger.exception(f'Unsupported device: {device_specification}')
        raise Exception('Unsupported device')

    def collect_provider(self):
        logger.debug('Collecting provider for Qapp Qiskit')
        return Aer

    @staticmethod
    def __map_aer_backend_name(backend):
        return backend.configuration().backend_name
