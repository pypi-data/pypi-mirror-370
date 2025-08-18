#  Quapp Platform Project
#  d_wave_device.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from abc import ABC

from quapp_common.enum.status.job_status import JobStatus
from quapp_common.model.device.custom_device import CustomDevice


class DWaveDevice(CustomDevice, ABC):

    def _is_simulator(self) -> bool:
        self.logger.debug("[DWave Device] Get device type")

        return True

    def _produce_histogram_data(self, job_result) -> dict | None:
        self.logger.debug("[DWave Device] Produce histogram")

        return None

    def _get_job_status(self, job) -> str:
        self.logger.debug("[DWave Device] Get job status")

        return JobStatus.DONE.value

    def _get_shots(self, job_result) -> int | None:
        self.logger.debug('[DWave Device] Get shots')
        self.logger.debug(f'[DWave Device] Job result: {job_result}')
        return None
