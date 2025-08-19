import os
from typing import List

from kink import inject

from appodus_utils import Utils
from appodus_utils.common.utils_settings import utils_settings
from appodus_utils.config.bootstrap import BaseDiBootstrap
from appodus_utils.sdk.appodus_sdk.services.messages.templating.interface import ITemplateEngineProvider

BaseDiBootstrap.register_all_subclasses(ITemplateEngineProvider)


@inject
class TemplateEngineProviderFactory:
    def __init__(self, providers: List[ITemplateEngineProvider]):
        self.ACTIVE_TEMPLATING_ENGINE = utils_settings.ACTIVE_TEMPLATING_ENGINE

        self._providers = providers
        self._factory = {}
        self._init_factory()

    def _init_factory(self):
        for provider in self._providers:
            self._factory[provider.template_engine] = provider

    def get_active_provider(self) -> ITemplateEngineProvider:
        return self._factory.get(self.ACTIVE_TEMPLATING_ENGINE)
