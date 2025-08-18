#  Quapp Platform Project
#  d_wave_system_provider.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from dwave.cloud import Client
from dwave.system import DWaveSampler, AutoEmbeddingComposite

from quapp_common.config.logging_config import job_logger
from quapp_common.enum.provider_tag import ProviderTag
from quapp_common.model.provider.provider import Provider

system_devices = ["Advantage_system4.1"]
hybrid_devices = ["hybrid_binary_quadratic_model_version2"]

logger = job_logger(__name__)


class DWaveSystemProvider(Provider):

    def __init__(self, api_token, endpoint):
        super().__init__(ProviderTag.D_WAVE)
        self.api_token = api_token
        self.endpoint = endpoint

    def get_backend(self, device_specification: str):
        logger.debug("[DWave system] Get backend")

        if device_specification in system_devices:
            provider = self.collect_provider()
            logger.debug("[DWave system] Get auto embedding composite")
            return AutoEmbeddingComposite(provider)

        if device_specification in hybrid_devices:
            client = Client(endpoint=self.endpoint, token=self.api_token)
            logger.debug("[DWave system] Get solver")
            return client.get_solver(device_specification)

        raise ValueError(
                "Unsupported DWave device: {0}".format(device_specification))

    def collect_provider(self):
        logger.debug("[DWave system] Connect to provider")
        try:
            return DWaveSampler(endpoint=self.endpoint, token=self.api_token)
        except Exception as exception:
            logger.exception(
                f"Failed to connect to DWave provider: {exception}")
            raise ValueError(
                f"Failed to connect to DWave provider: {exception}")
