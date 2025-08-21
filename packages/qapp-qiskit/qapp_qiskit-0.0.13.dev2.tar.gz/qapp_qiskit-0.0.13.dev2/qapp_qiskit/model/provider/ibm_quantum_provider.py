#  Quapp Platform Project
#  ibm_quantum_provider.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from qiskit_ibm_runtime import QiskitRuntimeService
from quapp_common.config.logging_config import job_logger
from quapp_common.enum.provider_tag import ProviderTag
from quapp_common.model.provider.provider import Provider

logger = job_logger('IbmQuantumProvider')


class IbmQuantumProvider(Provider):

    def __init__(self, api_token):
        super().__init__(ProviderTag.IBM_QUANTUM)
        self.api_token = api_token

    def get_backend(self, device_specification: str):
        logger.debug('Get backend from IBM Quantum')

        provider = self.collect_provider()

        backend = provider.backend(device_specification)
        logger.debug(f'Backend: {backend}')
        return backend

    def collect_provider(self):
        logger.debug('Collecting provider for IBM Quantum')

        return QiskitRuntimeService(channel='ibm_quantum', token=self.api_token)
