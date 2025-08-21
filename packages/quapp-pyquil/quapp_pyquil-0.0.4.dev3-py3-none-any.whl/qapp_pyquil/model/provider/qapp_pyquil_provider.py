"""
    QApp Platform Project
    qapp_pennylane_provider.py
    Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from quapp_common.config.logging_config import logger
from quapp_common.enum.provider_tag import ProviderTag
from quapp_common.model.provider.provider import Provider

from pyquil import get_qc


class QAppPyquilProvider(Provider):
    def __init__(self, ):
        logger.debug('[QAppPyquilProvider] get_backend()')
        super().__init__(ProviderTag.QUAO_QUANTUM_SIMULATOR)

    def get_backend(self, device_specification):
        logger.debug('[QAppPyquilProvider] get_backend()')

        try:
            print(device_specification)
            return get_qc(device_specification,as_qvm=True)
        except Exception as e:
            print(e)
            raise ValueError('[QAppPyquilProvider] Unsupported device')

    def collect_provider(self):
        logger.debug('[QAppPyquilProvider] collect_provider()')
        return None