"""
    QApp Platform Project
    pennylane_device_factory.py
    Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from quapp_common.config.logging_config import logger
from quapp_common.enum.provider_tag import ProviderTag
from quapp_common.enum.sdk import Sdk
from quapp_common.factory.device_factory import DeviceFactory
from quapp_common.model.provider.provider import Provider
from ..model.device.qapp_pyquil_device import QAppPyquilDevice
from ..model.device.rigetti_pyquil_device import RigettiPyquilDevice

class PyquilDeviceFactory(DeviceFactory):

    @staticmethod
    def create_device(provider: Provider, device_specification: str, authentication: dict, sdk: Sdk,
                      **kwargs):
        logger.info("[PyquilDeviceFactory] create_device()")

        provider_type = ProviderTag.resolve(provider.get_provider_type().value)

        logger.info("[PyquilDeviceFactory] provider type:" + str(provider_type))

        match provider_type:
            case ProviderTag.QUAO_QUANTUM_SIMULATOR:
                if Sdk.PYQUIL == sdk:
                    logger.debug('[PyquilDeviceFactory] Creating QAppPyquilDevice')
                    return QAppPyquilDevice(provider, device_specification)
            case ProviderTag.RIGETTI:
                if Sdk.PYQUIL == sdk:
                    logger.debug('[PyquilDeviceFactory] Creating RigettiPyquilDevice')
                    return RigettiPyquilDevice(provider, device_specification)
            case _:
                raise ValueError(f"Unsupported provider type: {provider_type}")