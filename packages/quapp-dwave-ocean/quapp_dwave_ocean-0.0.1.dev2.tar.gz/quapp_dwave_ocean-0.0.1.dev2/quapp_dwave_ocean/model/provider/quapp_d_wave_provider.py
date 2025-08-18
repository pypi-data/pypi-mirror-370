#  Quapp Platform Project
#  quapp_d_wave_provider.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from dwave.samplers import SimulatedAnnealingSampler

from quapp_common.config.logging_config import job_logger
from quapp_common.enum.provider_tag import ProviderTag
from quapp_common.model.provider.provider import Provider

logger = job_logger(__name__)


class QuappDWaveProvider(Provider):

    def __init__(self):
        logger.debug('[Quapp D-Wave] Initiate QuappDWaveProvider')
        super().__init__(ProviderTag.QUAO_QUANTUM_SIMULATOR)

    def get_backend(self, device_specification):
        logger.debug('[Quapp D-Wave] Get backend')

        return SimulatedAnnealingSampler()

    def collect_provider(self):
        return None
