from typing import Dict, Any

from kink import inject

from appodus_utils.exception.exceptions import TemplateRenderingException
from appodus_utils.integrations.messaging.models import MessageChannel
from appodus_utils.sdk.appodus_sdk.services.messages.templating.factory import TemplateEngineProviderFactory
from appodus_utils.sdk.appodus_sdk.services.messages.templating.interface import ITemplateEngineProvider


@inject
class TemplateService:
    def __init__(self, template_engine_provider_factory: TemplateEngineProviderFactory):
        self._template_engine_provider: ITemplateEngineProvider = template_engine_provider_factory.get_active_provider()

    async def render_message(
            self,
            channel: MessageChannel,
            template_name: str,
            context: Dict[str, Any]
    ) -> str:
        full_template_path = f"{channel.value}/{template_name}.{self._template_engine_provider.template_extension}"

        try:
            if not self._template_engine_provider.supports_template(full_template_path):
                raise TemplateRenderingException(f"Template not found: {full_template_path}")

            return self._template_engine_provider.render(full_template_path, context)
        except ValueError as e:
            raise TemplateRenderingException(str(e))
