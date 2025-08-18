#  Quapp Platform Project
#  invocation_handler.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from quapp_common.data.request.invocation_request import InvocationRequest
from quapp_common.handler.handler import Handler

from ..component.backend.d_wave_ocean_invocation import DWaveOceanInvocation


class InvocationHandler(Handler):
    def __init__(self, request_data: dict, circuit_preparation_fn,
                 post_processing_fn):
        super().__init__(request_data, post_processing_fn)
        self.circuit_preparation_fn = circuit_preparation_fn

    def handle(self):
        """
        Handles the invocation and submission of a quantum job request to the
        DWaveOceanInvocation backend. This method creates an invocation request
        with the provided data, logs relevant debug information, and submits
        the job to the backend using the specified preparation and post-processing
        functions.
        """
        self.logger.debug('Creating InvocationRequest')
        try:
            invocation_request = InvocationRequest(self.request_data)
            self.logger.debug(
                f'Invocation request keys: {list(invocation_request.__dict__.keys())}')

            backend = DWaveOceanInvocation(invocation_request)
            self.logger.debug('DWaveOceanInvocation backend instantiated')

            self.logger.debug('Submitting job to backend')
            backend.submit_job(
                    circuit_preparation_fn=self.circuit_preparation_fn,
                    post_processing_fn=self.post_processing_fn)
            self.logger.info('Job submitted to backend')
        except Exception as exception:
            self.logger.exception(
                    f'Error submitting job to backend: {exception}')
            raise ValueError(f'Error submitting job to backend: {exception}')
