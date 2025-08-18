#  Quapp Platform Project
#  d_wave_device_factory.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from quapp_common.config.logging_config import job_logger
from quapp_common.enum.provider_tag import ProviderTag
from quapp_common.enum.sdk import Sdk
from quapp_common.factory.device_factory import DeviceFactory
from quapp_common.model.provider.provider import Provider

from ..model.device.d_wave_hybrid_device import DWaveHybridDevice
from ..model.device.d_wave_system_device import DWaveSystemDevice
from ..model.device.quapp_d_wave_device import QuappDWaveOceanDevice
from ..model.provider.d_wave_system_provider import (system_devices,
                                                     hybrid_devices)

logger = job_logger(__name__)


class DWaveDeviceFactory(DeviceFactory):
    @staticmethod
    def create_device(provider: Provider, device_specification: str,
            authentication: dict, sdk: Sdk, ):
        """
        Creates a D-Wave device based on the provided specification and SDK.

        This method selects and returns an appropriate D-Wave device instance
        based on the provider type and device specification. It supports both
        quantum simulators and actual D-Wave devices, either system or hybrid
        devices.

        Args:
            provider (Provider): The provider instance to create the device from.
            device_specification (str): The specification of the device to be created.
            authentication (dict): Authentication details required for the provider.
            sdk (Sdk): The software development kit being used.

        Returns:
            A device instance corresponding to the specified provider and device type.

        Raises:
            Exception: If the device specification or provider type is unsupported.
        """
        provider_type = ProviderTag.resolve(provider.get_provider_type().value)
        logger.debug(
                f"[DWaveDeviceFactory] create_device called with provider_type={provider_type}, "
                f"device_specification={device_specification}, sdk={sdk}")

        if ProviderTag.QUAO_QUANTUM_SIMULATOR.__eq__(provider_type):
            logger.debug(
                    f"[DWaveDeviceFactory] Detected QUAO_QUANTUM_SIMULATOR with sdk={sdk}")
            if Sdk.D_WAVE_OCEAN.__eq__(sdk):
                logger.info(
                        f"[DWaveDeviceFactory] Creating QuappDWaveOceanDevice for spec={device_specification}")
                return QuappDWaveOceanDevice(provider, device_specification)

        if ProviderTag.D_WAVE.__eq__(provider_type):
            logger.debug(
                    f"[DWaveDeviceFactory] Detected D_WAVE provider; resolving device for spec={device_specification}")
            if device_specification in system_devices:
                logger.info(
                        f"[DWaveDeviceFactory] Creating DWaveSystemDevice for spec={device_specification}")
                return DWaveSystemDevice(provider, device_specification)

            if device_specification in hybrid_devices:
                logger.info(
                        f"[DWaveDeviceFactory] Creating DWaveHybridDevice for spec={device_specification}")
                return DWaveHybridDevice(provider, device_specification)

        logger.error(
                f"[DWaveDeviceFactory] Unsupported device: provider_type={provider_type}, "
                f"device_specification={device_specification}, sdk={sdk}")
        raise ValueError("Unsupported device!")
