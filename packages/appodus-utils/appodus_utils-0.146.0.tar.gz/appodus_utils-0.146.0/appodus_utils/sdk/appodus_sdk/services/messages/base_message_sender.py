from logging import Logger
from typing import Union, List, Dict, Any

from fastapi import BackgroundTasks
from kink import di

from appodus_utils.common.utils_settings import utils_settings
from appodus_utils.domain.user.auth.active_auditor.service import ActiveAuditorService
from appodus_utils.integrations.messaging.models import MessageRecipientUserId, MessageContextModule, MessageCategory, \
    MessageChannel, MessageRequestRecipient, MultiChannelMessageRequest
from appodus_utils.sdk.appodus_sdk.services.messages.message_dispatcher import MessageDispatcher
from appodus_utils.sdk.appodus_sdk.services.messages.message_payload_builder import MessageRecipientBuilder
from appodus_utils.sdk.appodus_sdk.services.messages.templating.models import AvailableTemplate

logger: Logger = di['logger']

class BaseMessageSender:
    def __init__(self,
                 messaging_dispatcher: MessageDispatcher,
                 active_auditor_service: ActiveAuditorService,
                 message_recipient_builder: MessageRecipientBuilder
                 ):
        self._messaging_dispatcher = messaging_dispatcher
        self._active_auditor_service = active_auditor_service
        self._message_recipient_builder = message_recipient_builder
        self._enable_out_messaging = utils_settings.ENABLE_OUT_MESSAGING

    async def _send_message(
            self,
            recipient_user_id: MessageRecipientUserId,
            template: Union[AvailableTemplate, str],
            context_modules: List[MessageContextModule],
            category: MessageCategory,
            default_channels: List[MessageChannel],
            extra_context: dict[str, str] = None
    ) -> None:
        """Core method to handle all message sending logic."""
        recipient = await self._message_recipient_builder.build_recipient(recipient_user_id)
        template_context = await self._message_recipient_builder.build_context(recipient_user_id.user_id, context_modules)

        if extra_context:
            template_context.update(extra_context)

        await self._send_direct_message(
            recipient=recipient,
            template=template,
            context=template_context,
            category=category,
            default_channels=default_channels
        )

    async def _send_direct_message(self,
                                   recipient: MessageRequestRecipient,
                                   template: Union[AvailableTemplate, str],
                                   context: Dict[str, Any],
                                   category: MessageCategory,
                                   default_channels: List[MessageChannel]):

        channels = self._get_available_channels(recipient, default_channels)
        if not channels:
            logger.info(f"Message send to '{recipient}', for '{template}' cannot continue: no available configured channel")
            return

        final_context = self._build_context(
            context=context,
            category=category
        )

        request = MultiChannelMessageRequest(
            recipient=recipient,
            template=template,
            context=final_context,
            channels=channels
        )

        if self._enable_out_messaging:
            background_tasks: BackgroundTasks = await self._active_auditor_service.get_background_tasks_from_context()
            background_tasks.add_task(self._messaging_dispatcher.dispatch_to_channels, request)

    @staticmethod
    def _get_available_channels(
            recipient: MessageRequestRecipient,
            default_channels: List[MessageChannel]
    ) -> List[MessageChannel]:
        """Filter default channels based on recipient's available contact methods."""
        channel_checks = {
            MessageChannel.EMAIL: bool(recipient.email),
            MessageChannel.SMS: bool(recipient.phone),
            MessageChannel.WHATSAPP: bool(recipient.phone),
            MessageChannel.PUSH: bool(recipient.ios_push_token or recipient.android_push_token),
            MessageChannel.WEB_PUSH: bool(recipient.web_push_token),
        }

        return [
            channel for channel in default_channels
            if channel_checks.get(channel, False)
        ]

    def _build_context(
            self,
            context: Dict[str, Any],
            category: MessageCategory
    ) -> Dict[str, Any]:
        """Build the final context dictionary with defaults and overrides."""
        context = context.copy()
        context.update({
            "categories": [category]
        })
        context.update(self._messaging_dispatcher.config.model_dump(exclude={"subjects, _normalized_subjects, _required_subjects"}))
        return context
