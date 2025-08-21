"""
    QApp Platform Project
    qapp_pennylane_provider.py
    Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from quapp_common.config.logging_config import logger
from quapp_common.enum.provider_tag import ProviderTag
from quapp_common.model.provider.provider import Provider

from pyquil import get_qc
from qcs_sdk.client import QCSClient, OAuthSession, AuthServer, RefreshToken
from pyquil.api import QuantumComputer


class RigettiPyquilProvider(Provider):
    def __init__(self, device_name, client_id, issuer, refresh_token, access_token, api_url):
        self.device_name = device_name
        self.client_id = client_id
        self.issuer = issuer
        self.refresh_token = refresh_token
        self.access_token = access_token
        self.api_url = api_url
        
        logger.debug('[RigettiPyquilProvider] get_backend()')
        super().__init__(ProviderTag.RIGETTI)

    def get_backend(self, device_specification) -> QuantumComputer:
        logger.debug('[RigettiPyquilProvider] get_backend()')

        try:
            auth = AuthServer(client_id=self.client_id, issuer=self.issuer)
            ref = RefreshToken(refresh_token=self.refresh_token)
            session = OAuthSession(auth_server=auth,
                                   access_token=self.access_token,
                                   payload=ref)
            client = QCSClient(api_url=self.api_url, oauth_session=session)

            return get_qc(device_specification,client_configuration=client)
        except Exception as e:
            print(e)
            raise ValueError('[RigettiPyquilProvider] Unsupported device')

    def collect_provider(self):
        logger.debug('[RigettiPyquilProvider] collect_provider()')
        return None