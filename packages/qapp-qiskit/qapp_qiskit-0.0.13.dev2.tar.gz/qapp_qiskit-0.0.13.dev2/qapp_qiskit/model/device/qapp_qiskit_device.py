"""
    QApp Platform Project qapp_qiskit_device.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
#  Quapp Platform Project
#  qapp_qiskit_device.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from qiskit import transpile
from quapp_common.data.device.circuit_running_option import CircuitRunningOption
from quapp_common.model.provider.provider import Provider

from .qiskit_device import QiskitDevice


class QappQiskitDevice(QiskitDevice):
    def __init__(self, provider: Provider, device_specification: str):
        super().__init__(provider, device_specification)

    def _create_job(self, circuit, options: CircuitRunningOption):
        self.logger.debug(f'Creating job with {options.shots} shots')
        self.device.set_options(device=options.processing_unit.value,
                                shots=options.shots, executor=options.executor,
                                max_job_size=options.max_job_size)
        self.logger.debug(
                f'Set options: device={options.processing_unit.value}, '
                f'shots={options.shots}, executor={options.executor}, '
                f'max_job_size={options.max_job_size}')

        transpiled_circuit = transpile(circuits=circuit, backend=self.device)
        self.logger.debug('Transpiled circuit created successfully')

        return self.device.run(transpiled_circuit)

    def _is_simulator(self) -> bool:
        self.logger.debug('Checking if simulator')
        self.logger.debug(f'Simulator: {True}')
        return True
