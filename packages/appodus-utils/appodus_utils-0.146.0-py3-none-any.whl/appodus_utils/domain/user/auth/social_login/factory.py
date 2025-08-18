from logging import Logger
from typing import List

from kink import di, inject

from appodus_utils.config.bootstrap import BaseDiBootstrap
from appodus_utils.domain.user.auth.social_login.models import SocialAuthPlatform
from appodus_utils.domain.user.auth.social_login.interface import ISocialAuthProvider
from appodus_utils.exception.exceptions import NotImplementedException

BaseDiBootstrap.register_all_subclasses(ISocialAuthProvider)
logger: Logger = di["logger"]


@inject
class SocialAuthProviderFactory:
    def __init__(self, providers: List[ISocialAuthProvider]):
        self._providers = providers
        self._factory = {}
        self._init_factory()

    def _init_factory(self):
        logger.debug("Initializing SocialAuthProviders...")
        for provider in self._providers:
            logger.debug(f"... initialized: {provider.platform} -> {provider}")
            self._factory[provider.platform] = provider

    def get_auth_provider(self, provider: SocialAuthPlatform) -> ISocialAuthProvider:
        auth_provider = self._factory.get(provider)

        if not auth_provider:
            msg = f"Unsupported provider: {provider}"
            logger.error(msg)
            raise NotImplementedException(message=msg)

        return auth_provider
