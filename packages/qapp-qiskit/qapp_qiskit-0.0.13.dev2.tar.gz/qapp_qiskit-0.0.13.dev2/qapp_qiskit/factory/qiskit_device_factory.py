#  Quapp Platform Project
#  qiskit_device_factory.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from quapp_common.config.logging_config import logger
from quapp_common.enum.provider_tag import ProviderTag
from quapp_common.enum.sdk import Sdk
from quapp_common.factory.device_factory import DeviceFactory
from quapp_common.model.provider.provider import Provider

from ..model.device.ibm_cloud_device import IbmCloudDevice
from ..model.device.ibm_quantum_device import IbmQuantumDevice
from ..model.device.oqc_cloud_device import OqcCloudDevice
from ..model.device.qapp_qiskit_device import QappQiskitDevice


class QiskitDeviceFactory(DeviceFactory):

    @staticmethod
    def create_device(provider: Provider, device_specification: str,
            authentication: dict, sdk: Sdk):
        logger.info("[QiskitDeviceFactory] create_device()")

        provider_type = ProviderTag.resolve(provider.get_provider_type().value)

        if ProviderTag.QUAO_QUANTUM_SIMULATOR.__eq__(
                provider_type) and Sdk.QISKIT.__eq__(sdk):
            return QappQiskitDevice(provider, device_specification)

        if ProviderTag.IBM_QUANTUM.__eq__(provider_type):
            return IbmQuantumDevice(provider, device_specification)

        if ProviderTag.IBM_CLOUD.__eq__(provider_type):
            return IbmCloudDevice(provider, device_specification)

        if ProviderTag.OQC_CLOUD.__eq__(provider_type):
            return OqcCloudDevice(provider, device_specification)

        raise Exception("Unsupported device!")
