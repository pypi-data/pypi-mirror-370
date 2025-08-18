import ast
import enum
from typing import Dict, Any, Type, TypeVar, Union

from kink import inject
from pydantic import ValidationError

from appodus_utils import Object
from appodus_utils.exception.exceptions import TemplateRenderingException, ValidationException
from appodus_utils.integrations.messaging.models import MessageChannel, PushPayload, WebPushPayload, WhatsappPayload
from appodus_utils.sdk.appodus_sdk.services.messages.templating.models import AvailableTemplate
from appodus_utils.sdk.appodus_sdk.services.messages.templating.service import TemplateService

T = TypeVar('T', bound=Union[Object, str])


@inject
class ModelTemplateService:
    def __init__(self, template_service: TemplateService):
        self.template_service = template_service

    async def render_model(
            self,
            model_class: Type[T],
            channel: MessageChannel,
            template: Union[AvailableTemplate, str],
            context: Dict[str, Any],
            **kwargs
    ) -> T:
        """
        Renders any Pydantic model from a template

        Args:
            model_class: The Pydantic model class to instantiate
            channel: Which message channel the template belongs to
            template: Name of the template (without extension)
            context: Dictionary of template variables
            model_kwargs: Additional arguments to pass to model constructor

        Returns:
            Fully validated instance of the requested model

        Raises:
            TemplateRenderingException: If template rendering fails
            InvalidPayloadException: If rendered output doesn't validate
        """
        template_name = template.value if isinstance(template, enum.Enum) else template

        try:
            # Render the template

            rendered_content = await self.template_service.render_message(
                channel=channel,
                template_name=template_name,
                context=context
            )

            if model_class == str:
                return rendered_content

            # Parse the rendered content
            payload_data = self._parse_rendered_content(rendered_content)

            # Create and validate the model instance
            return model_class(**{**payload_data, **kwargs})

        except ValidationError as e:
            raise ValidationException(
                message=f"Invalid {model_class.__name__} payload: {str(e)}"
            )
        except ValueError as e:
            raise ValidationException(message=f"Invalid content format: {str(e)}")
        except Exception as e:
            raise TemplateRenderingException(
                f"Failed to render {template_name} template: {str(e)}"
            )

    def _parse_rendered_content(self, content: str) -> Dict[str, Any]:
        """
        Parses rendered template content into a dictionary.
        Can be overridden by subclasses for custom formats.

        Args:
            content: Rendered template string

        Returns:
            Dictionary suitable for model creation
        """
        return ast.literal_eval(content)

    async def render_push_payload(
            self,
            template: Union[AvailableTemplate, str],
            context: Dict[str, Any],
            **kwargs
    ) -> PushPayload:
        """Convenience method specifically for rendering PushPayload"""
        return await self.render_model(
            model_class=PushPayload,
            channel=MessageChannel.PUSH,
            template=template,
            context=context,
            **kwargs
        )

    async def render_web_push_payload(
            self,
            template: Union[AvailableTemplate, str],
            context: Dict[str, Any],
            **kwargs
    ) -> WebPushPayload:
        """Convenience method specifically for rendering WebPushPayload"""
        return await self.render_model(
            model_class=WebPushPayload,
            channel=MessageChannel.WEB_PUSH,
            template=template,
            context=context,
            **kwargs
        )

    async def render_whatsapp_payload(
            self,
            template: Union[AvailableTemplate, str],
            context: Dict[str, Any],
            **kwargs
    ) -> WhatsappPayload:
        """Convenience method specifically for rendering WhatsappPayload"""
        return await self.render_model(
            model_class=WhatsappPayload,
            channel=MessageChannel.WHATSAPP,
            template=template,
            context=context,
            **kwargs
        )

    async def render_sms_payload(
            self,
            template: Union[AvailableTemplate, str],
            context: Dict[str, Any],
            **kwargs
    ) -> str:
        """Convenience method specifically for rendering WhatsappPayload"""
        return await self.render_model(
            model_class=str,
            channel=MessageChannel.SMS,
            template=template,
            context=context,
            **kwargs
        )

    async def render_email_payload(
            self,
            template: Union[AvailableTemplate, str],
            context: Dict[str, Any],
            **kwargs
    ) -> str:
        """Convenience method specifically for rendering WhatsappPayload"""
        return await self.render_model(
            model_class=str,
            channel=MessageChannel.EMAIL,
            template=template,
            context=context,
            **kwargs
        )
