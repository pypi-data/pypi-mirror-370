from logging import Logger
from typing import List

from kink import di, inject

from appodus_utils.integrations.messaging.models import MessageRecipientUserId, MessageContextModule, MessageCategory, \
    MessageChannel, MessageRequestRecipient
from appodus_utils.sdk.appodus_sdk.services.messages.base_message_sender import BaseMessageSender
from appodus_utils.sdk.appodus_sdk.services.messages.templating.models import AvailableTemplate

logger: Logger = di["logger"]


@inject
class AccountSecurityMessages(BaseMessageSender):
    """Handles all account security and verification related messages"""

    async def send_new_user_welcome_message(self, recipient_user_id: MessageRecipientUserId,
                                            context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.NEW_USER_WELCOME,
            context_modules=context_modules,
            category=MessageCategory.ONBOARDING,
            default_channels=[
                MessageChannel.WHATSAPP,
                MessageChannel.EMAIL,
                MessageChannel.PUSH
            ]
        )

    async def send_email_verification_message(self, recipient_user_id: MessageRecipientUserId,
                                              context_modules:List[MessageContextModule], extra_context: dict[str, str]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.EMAIL_VERIFICATION,
            context_modules=context_modules,
            category=MessageCategory.VERIFICATION,
            default_channels=[
                MessageChannel.WHATSAPP,
                MessageChannel.EMAIL
            ],
            extra_context=extra_context
        )

    async def send_direct_email_verification_message(self, recipient: MessageRequestRecipient,  context: dict[str, str]):
        await self._send_direct_message(
            recipient=recipient,
            template=AvailableTemplate.NEW_USER_EMAIL_VERIFICATION,
            context=context,
            category=MessageCategory.VERIFICATION,
            default_channels=[
                MessageChannel.EMAIL
            ]
        )

    async def send_phone_verification_message(self, recipient_user_id: MessageRecipientUserId,
                                              context_modules:List[MessageContextModule], extra_context: dict[str, str]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.PHONE_VERIFICATION,
            context_modules=context_modules,
            category=MessageCategory.VERIFICATION,
            default_channels=[
                MessageChannel.SMS,
                MessageChannel.WHATSAPP
            ],
            extra_context=extra_context
        )

    async def send_login_security_alert_message(self, recipient_user_id: MessageRecipientUserId,
                                                context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.LOGIN_DIFF_DEVICE_SECURITY_ALERT,
            context_modules=context_modules,
            category=MessageCategory.SECURITY,
            default_channels=[
                MessageChannel.SMS,
                MessageChannel.WHATSAPP,
                MessageChannel.EMAIL,
                MessageChannel.PUSH
            ]
        )

    async def send_password_reset_request_message(self, recipient_user_id: MessageRecipientUserId,
                                                  context_modules:List[MessageContextModule], extra_context: dict[str, str]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.PASSWORD_RESET_REQUEST,
            context_modules=context_modules,
            category=MessageCategory.SECURITY,
            default_channels=[
                MessageChannel.SMS,
                MessageChannel.EMAIL
            ],
            extra_context=extra_context
        )

    async def send_password_updated_message(self, recipient_user_id: MessageRecipientUserId,
                                            context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.PASSWORD_UPDATE_SUCCESS,
            context_modules=context_modules,
            category=MessageCategory.SECURITY,
            default_channels=[MessageChannel.EMAIL]
        )

    async def send_name_updated_message(self, recipient_user_id: MessageRecipientUserId,
                                            context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.NAME_UPDATE_SUCCESS,
            context_modules=context_modules,
            category=MessageCategory.SECURITY,
            default_channels=[MessageChannel.EMAIL]
        )

    async def send_2fa_message(self, recipient_user_id: MessageRecipientUserId,
                               context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.TWO_FA,
            context_modules=context_modules,
            category=MessageCategory.SECURITY,
            default_channels=[
                MessageChannel.SMS,
                MessageChannel.EMAIL,
                MessageChannel.WHATSAPP
            ]
        )

    async def send_account_deactivation_message(self, recipient_user_id: MessageRecipientUserId,
                                                context_modules:List[MessageContextModule], extra_context: dict[str, str]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.ACCOUNT_DEACTIVATION,
            context_modules=context_modules,
            category=MessageCategory.ADMIN,
            default_channels=[MessageChannel.EMAIL],
            extra_context=extra_context
        )

    async def send_account_activation_message(self, recipient_user_id: MessageRecipientUserId,
                                                context_modules:List[MessageContextModule], extra_context: dict[str, str]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.ACCOUNT_ACTIVATION,
            context_modules=context_modules,
            category=MessageCategory.ADMIN,
            default_channels=[MessageChannel.EMAIL],
            extra_context=extra_context
        )

    async def send_property_upload_reminder_message(self, recipient_user_id: MessageRecipientUserId,
                                                    context_modules:List[MessageContextModule]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template=AvailableTemplate.PROPERTY_LISTING_COMPLETION_REMINDER,
            context_modules=context_modules,
            category=MessageCategory.REMINDER,
            default_channels=[
                MessageChannel.EMAIL,
                MessageChannel.WHATSAPP,
                MessageChannel.PUSH
            ]
        )
