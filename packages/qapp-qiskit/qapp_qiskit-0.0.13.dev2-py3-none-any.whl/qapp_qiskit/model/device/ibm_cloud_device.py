"""
    QApp Platform Project ibm_cloud_device.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
#  Quapp Platform Project
#  ibm_cloud_device.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from qiskit_ibm_runtime import Options, Session, Sampler
from quapp_common.data.device.circuit_running_option import CircuitRunningOption

from .qiskit_device import QiskitDevice


class IbmCloudDevice(QiskitDevice):
    def _is_simulator(self) -> bool:
        self.logger.debug('Checking if simulator')
        simulator = self.device.configuration().simulator
        self.logger.debug(f'Simulator: {simulator}')
        return simulator

    def _create_job(self, circuit, options: CircuitRunningOption):
        self.logger.debug(f'Creating job with {options.shots} shots')

        running_options = Options(optimization_level=1)
        running_options.execution.shots = options.shots
        self.logger.debug(
                f'Runtime options set: optimization_level=1, shots={running_options.execution.shots}')

        self.logger.debug('Opening IBM Runtime session')
        with Session(service=self.provider.collect_provider(),
                     backend=self.device) as session:
            self.logger.debug('Session opened successfully, creating Sampler')
            sampler = Sampler(session=session, options=running_options)
            self.logger.debug('Sampler created successfully')
            job = sampler.run(circuits=circuit)
            self.logger.debug('Job submitted successfully')
            return job
