"""
    QApp platform Project invocation_handler.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from quapp_common.data.request.invocation_request import InvocationRequest
from quapp_common.handler.handler import Handler

from ..component.backend.pyquil_invocation import PyquilInvocation


class InvocationHandler(Handler):

    def __init__(self, request_data: dict,
                 circuit_preparation_fn,
                 post_processing_fn):
        super().__init__(request_data, post_processing_fn)
        self.circuit_preparation_fn = circuit_preparation_fn

    def handle(self):
        self.logger.info("[InvocationHandler] handle()")

        invocation_request = InvocationRequest(self.request_data)

        backend = PyquilInvocation(invocation_request)

        backend.submit_job(circuit_preparation_fn=self.circuit_preparation_fn,
                           post_processing_fn=self.post_processing_fn)
