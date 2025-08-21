"""
    QApp Platform Project ibm_quantum_device.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
#  Quapp Platform Project
#  ibm_quantum_device.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from qiskit import transpile
from qiskit_ibm_runtime import SamplerV2 as Sampler
from quapp_common.data.device.circuit_running_option import CircuitRunningOption

from .ibm_cloud_device import IbmCloudDevice


class IbmQuantumDevice(IbmCloudDevice):

    def _create_job(self, circuit, options: CircuitRunningOption):
        self.logger.debug(f"Creating job with {options.shots} shots")

        transpiled_circuit = transpile(circuits=circuit, backend=self.device)
        self.logger.debug('Transpiled circuit created successfully')

        sampler = Sampler(self.device)
        self.logger.debug('Sampler created successfully')

        job = sampler.run([transpiled_circuit], shots=options.shots)
        self.logger.info('Job submitted successfully')
        return job
