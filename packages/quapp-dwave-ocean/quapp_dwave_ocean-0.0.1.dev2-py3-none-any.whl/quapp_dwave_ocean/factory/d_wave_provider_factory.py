#  Quapp Platform Project
#  d_wave_provider_factory.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.
from quapp_common.config.logging_config import job_logger
from quapp_common.enum.provider_tag import ProviderTag
from quapp_common.enum.sdk import Sdk
from quapp_common.factory.provider_factory import ProviderFactory

from ..model.provider.d_wave_system_provider import DWaveSystemProvider
from ..model.provider.quapp_d_wave_provider import QuappDWaveProvider

logger = job_logger(__name__)


class DWaveProviderFactory(ProviderFactory):
    @staticmethod
    def create_provider(provider_type: ProviderTag, sdk: Sdk,
                        authentication: dict):
        """
        Creates and returns a provider based on the specified provider type and SDK.

        Args:
            provider_type: The type of provider to create, identified by a ProviderTag.
            sdk: The SDK to use for the provider, identified by a Sdk.
            authentication: A dictionary containing authentication details such as token and endpoint.

        Returns:
            An instance of DWaveSystemProvider or QuappDWaveProvider based on the matching criteria.

        Raises:
            Exception: If the provider type or SDK is not supported.
        """
        logger.debug(
                "[DWaveProviderFactory] create_provider called with provider_type=%s, sdk=%s, auth_provided=%s",
                provider_type, sdk, authentication is not None
        )

        if ProviderTag.QUAO_QUANTUM_SIMULATOR.__eq__(provider_type):
            logger.debug(
                    "[DWaveProviderFactory] Detected QUAO_QUANTUM_SIMULATOR")
            if Sdk.D_WAVE_OCEAN.__eq__(sdk):
                logger.info(
                        "[DWaveProviderFactory] Creating QuappDWaveProvider")
                return QuappDWaveProvider()

        if ProviderTag.D_WAVE.__eq__(provider_type):
            logger.debug("[DWaveProviderFactory] Detected D_WAVE provider")
            if authentication is None:
                logger.error(
                        "[DWaveProviderFactory] Missing authentication for D-Wave provider")
                raise ValueError(
                        "Authentication details are required for D-Wave provider.")

            token = authentication.get("token")
            endpoint = authentication.get("endpoint")
            if token is None or endpoint is None:
                missing_details = []
                if token is None:
                    missing_details.append("token")
                if endpoint is None:
                    missing_details.append("endpoint")
                error_message = "Missing authentication details: {0}".format(
                        ", ".join(missing_details))
                logger.error("[DWaveProviderFactory] %s", error_message)
                raise ValueError(error_message)

            logger.info(
                    "[DWaveProviderFactory] Creating DWaveSystemProvider with provided endpoint")
            return DWaveSystemProvider(token, endpoint)

        logger.error(
                "[DWaveProviderFactory] Unsupported provider: provider_type=%s, sdk=%s",
                provider_type, sdk)
        raise ValueError("Unsupported provider!")
