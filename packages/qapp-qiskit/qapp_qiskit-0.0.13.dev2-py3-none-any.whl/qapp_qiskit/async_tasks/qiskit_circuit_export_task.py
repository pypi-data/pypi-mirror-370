#  Quapp Platform Project
#  qiskit_circuit_export_task.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from qiskit import transpile
from quapp_common.async_tasks.export_circuit_task import CircuitExportTask
from quapp_common.enum.sdk import Sdk

from ..factory.qiskit_provider_factory import QiskitProviderFactory
from ..model.provider.oqc_cloud_provider import OqcCloudProvider


class QiskitCircuitExportTask(CircuitExportTask):

    def _transpile_circuit(self):
        self.logger.debug('Transpiling circuit')
        try:
            # Optional circuit quick stats
            try:
                num_qubits = getattr(self.circuit_data_holder.circuit,
                                     "num_qubits", None)
                depth = (self.circuit_data_holder.circuit.depth() if hasattr(
                        self.circuit_data_holder.circuit, "depth") else None)
                self.logger.debug(
                        f'Circuit stats: qubits={num_qubits}, depth={depth}')
            except Exception as exception:
                # Non-fatal: circuit might not support stats
                self.logger.warning(f'Failed to get circuit stats: {exception}')
                pass

            circuit = self.circuit_data_holder.circuit
            backend_information = self.backend_data_holder.backend_information

            self.logger.info(f'Creating provider: sdk={Sdk.QISKIT}, '
                             f'provider_tag={getattr(backend_information, "provider_tag", None)}')
            provider = QiskitProviderFactory.create_provider(sdk=Sdk.QISKIT,
                                                             provider_type=backend_information.provider_tag,
                                                             authentication=backend_information.authentication, )

            if isinstance(provider, OqcCloudProvider):
                self.logger.info(
                        f"Provider '{type(provider).__name__}' does not "
                        "require transpilation. Skipping.")
                return circuit

            device_name = getattr(backend_information, "device_name", None)
            self.logger.debug(f"Fetching backend '{device_name}'")
            backend = provider.get_backend(device_name)

            backend_name = getattr(backend, "name", None)
            try:
                backend_name = backend_name() if callable(
                        backend_name) else backend_name
            except Exception as exception:
                self.logger.warning(f'Failed to get backend name: {exception}')
                pass

            self.logger.info(
                    f"Starting transpilation for backend '{backend_name or device_name}'")
            transpiled = transpile(circuits=circuit, backend=backend)
            self.logger.info('Transpilation completed successfully')
            return transpiled

        except Exception as exception:
            self.logger.exception(f'Transpilation failed: {exception}')
            raise
