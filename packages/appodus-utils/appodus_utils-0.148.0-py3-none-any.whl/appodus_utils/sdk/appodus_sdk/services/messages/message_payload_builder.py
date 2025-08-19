from typing import List, Dict, Any

from appodus_utils import Utils
from kink import inject

from appodus_utils.decorators.decorate_all_methods import decorate_all_methods
from appodus_utils.decorators.method_trace_logger import method_trace_logger
from appodus_utils.decorators.transactional import transactional
from appodus_utils.domain.user.device.models import SearchDeviceDto
from appodus_utils.domain.user.device.service import DeviceService
from appodus_utils.domain.user.service import UserService
from appodus_utils.integrations.messaging.models import MessageRecipientUserId, MessageRequestRecipient, \
    MessageContextModule, PushProviderType, PushToken, EmailParty


@inject
@decorate_all_methods(transactional())
@decorate_all_methods(method_trace_logger)
class MessageRecipientBuilder:
    def __init__(self,
                 user_service: UserService,
                 device_service: DeviceService
                 ):
        self._user_service = user_service
        self._device_service = device_service

    async def build_recipient(self, recipient: MessageRecipientUserId) -> MessageRequestRecipient:

        user_response = await self._user_service.get_user(recipient.user_id)
        user = user_response.data

        web_push_token, ios_push_token, android_push_token = await self._get_user_devices_push_tokens(recipient.user_id)

        email_cc_recipients = await self._get_email_recipients(recipient.cc_recipients)

        email_bcc_recipients = await self._get_email_recipients(recipient.bcc_recipients)

        phone_number = Utils.normalize_phone(f"{user.phone_ext}{user.phone}")

        return MessageRequestRecipient(
            user_id=recipient.user_id,
            fullname=user.fullname,
            email=user.email,
            phone=phone_number,
            ios_push_token=ios_push_token,
            android_push_token=android_push_token,
            web_push_token=web_push_token,
            cc_recipient=email_cc_recipients,
            bcc_recipient=email_bcc_recipients
        )

    async def build_context(self, user_id: str, context_modules: List[MessageContextModule]) -> Dict[str, Any]:
        context = {"today": Utils.datetime_now()}

        for context_module in context_modules:
            if context_module == MessageContextModule.USER:
                user_context = await self._get_user_context(user_id)
                context.update(user_context)

        return context

    async def _get_user_context(self, user_id):
        user_response = await self._user_service.get_user(user_id)
        user = user_response.data
        return user.model_dump(exclude={"password"}, exclude_none=True,  exclude_unset=True)

    async def _get_email_recipients(self, user_ids: List[str] = None)  -> List[EmailParty]:
        email_recipients: List[EmailParty] = []
        if user_ids:
            for user_id in user_ids:
                user_response = await self._user_service.get_user(user_id)
                user = user_response.data
                email_recipient = EmailParty(email=user.email, fullname=user.fullname)
                email_recipients.append(email_recipient)

        return email_recipients

    async def _get_user_devices_push_tokens(self, user_id: str) -> tuple[List[PushToken], List[PushToken], List[PushToken]]:
        web_push_token: List[PushToken] = []
        ios_push_token: List[PushToken] = []
        android_push_token: List[PushToken] = []

        search_dto: SearchDeviceDto = SearchDeviceDto(page=0, page_size=10, user_id=user_id, query_fields="push_provider_type, push_token")
        devices = await self._device_service.get_device_page(search_dto)
        for device in devices.data:
            if device.push_provider_type == PushProviderType.WEB_PUSH:
                web_push_token.append(device.push_token)
            elif device.push_provider_type == PushProviderType.APNS:
                ios_push_token.append(device.push_token)
            elif device.push_provider_type == PushProviderType.FIREBASE:
                android_push_token.append(device.push_token)

        return web_push_token, ios_push_token, android_push_token
