import asyncio
import json
import os
from logging import Logger
from typing import List
from unittest import IsolatedAsyncioTestCase

import httpx
import respx
from _pytest.monkeypatch import MonkeyPatch
from fastapi import BackgroundTasks
from httpx import AsyncClient
from kink import di, inject

from appodus_utils import Utils

from appodus_utils.common.utils_settings import utils_settings
from appodus_utils.config.bootstrap import BaseDiBootstrap

from appodus_utils.common.appodus_test_utils import TestUtils
from appodus_utils.db.session import close_db_engine, init_db_engine_and_session
from appodus_utils.decorators.decorate_all_methods import decorate_all_methods
from appodus_utils.decorators.transactional import transactional, TransactionSessionPolicy
from appodus_utils.domain.user.auth.active_auditor.service import ActiveAuditorService
from appodus_utils.domain.user.auth.models import LoginSuccessDto
from appodus_utils.domain.user.device.models import QueryDeviceDto, Device
from appodus_utils.domain.user.device.service import DeviceService
from appodus_utils.domain.user.models import User, QueryUserDto
from appodus_utils.domain.user.service import UserService
from appodus_utils.integrations.messaging.models import MessageRecipientUserId, MessageContextModule, MessageCategory, \
    MessageChannel, MessageRequestRecipient, PushProviderType, BatchResult
from appodus_utils.sdk.appodus_sdk.services.messages.base_message_sender import BaseMessageSender
from appodus_utils.sdk.appodus_sdk.services.messages.message_dispatcher import MessageDispatcher
from appodus_utils.sdk.appodus_sdk.services.messages.message_payload_builder import MessageRecipientBuilder
from tests.appodus_utils.domain.user.device.test_e2e_service import CreateDeviceDtoFactory
from tests.appodus_utils.domain.user.test_e2e_service import CreateUserDtoFactory
from tests.appodus_utils.test_utils import mock_active_auditor_service, mock_http_client

logger: Logger = di["logger"]

@decorate_all_methods(transactional(session_policy=TransactionSessionPolicy.ALWAYS_NEW),
                      exclude=['asyncTearDown', 'asyncSetUp', 'run_background_tasks'])
class TestMessageSender(IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        init_db_engine_and_session()

        self.user_service: UserService = di[UserService]
        self.device_service: DeviceService = di[DeviceService]
        self.sample_message_sender: SampleMessageSender = di[SampleMessageSender]
        self._http_client = di[AsyncClient]
        self.monkeypatch = MonkeyPatch()
        self.background_tasks = BackgroundTasks()
        self.request_url = f"{utils_settings.APPODUS_SERVICES_URL}/v1/messages"
        self.otp = "your otp"

        self.batch_result = BatchResult(
                total=1,
                successes=["pass"],
                failures=["fail"],
                processing_time=323432
            )

        # Enable Messaging
        os.environ["ENABLE_OUT_MESSAGING"] = str(True)

    async def asyncTearDown(self):
        # Disable Messaging
        os.environ["ENABLE_OUT_MESSAGING"] = str(False)

        self.monkeypatch.undo()
        await self._truncate_tables()
        await close_db_engine()

    @staticmethod
    async def _truncate_tables():
        await TestUtils.truncate_entities([User, Device])

    async def run_background_tasks(self):
        # RUN BackgroundTasks
        for task in self.background_tasks.tasks:
            if asyncio.iscoroutinefunction(task.func):
                await task.func(*task.args, **task.kwargs)
            else:
                task.func(*task.args, **task.kwargs)

    async def create_user_and_mock_active_auditor_service(self) -> LoginSuccessDto:

        create_user_dto = CreateUserDtoFactory.build()
        # mock_active_auditor_service
        mock_active_auditor_service(
            monkeypatch=self.monkeypatch,
            user=QueryUserDto.model_copy(create_user_dto),
            background_tasks=self.background_tasks
        )

        await self.user_service.store_verified_email_otp(
            email=create_user_dto.email,
            otp=create_user_dto.otp
        )

        created_user_response = await self.user_service.create_user(create_user_dto)

        return created_user_response

    async def create_device(self, user_id: str, push_provider_type: PushProviderType) -> QueryDeviceDto:
        create_device_dto = CreateDeviceDtoFactory.build()
        create_device_dto.user_id = user_id
        create_device_dto.push_provider_type = push_provider_type

        created_device_response = await self.device_service.create_device(create_device_dto)
        created_device = created_device_response.data

        return created_device

    async def test_send_otp_message(self):
        # Mock MessagingService
        mock_http_client(monkeypatch=self.monkeypatch, http_client=self._http_client, request_url=self.request_url)

        created_user = await self.create_user_and_mock_active_auditor_service()

        for push_provider_type in [PushProviderType.WEB_PUSH, PushProviderType.APNS, PushProviderType.FIREBASE]:
            await self.create_device(user_id=created_user.id, push_provider_type=push_provider_type)

        await self.sample_message_sender.send_otp_message(
                recipient_user_id=MessageRecipientUserId(user_id=created_user.id),
                context_modules=[MessageContextModule.USER],
                extra_context={
                    "otp": self.otp,
                }
            )

        # RUN BackgroundTasks
        await self.run_background_tasks()
        await asyncio.sleep(0.1)  # allow background task to run

    async def test_send_direct_otp_message(self):
        # Mock MessagingService
        mock_http_client(monkeypatch=self.monkeypatch, http_client=self._http_client, request_url=self.request_url)

        created_user = await self.create_user_and_mock_active_auditor_service()
        devices = {}

        for push_provider_type in [PushProviderType.WEB_PUSH, PushProviderType.APNS, PushProviderType.FIREBASE]:
                created_device = await self.create_device(user_id=created_user.id, push_provider_type=push_provider_type)
                devices[push_provider_type] = created_device.push_token


        await self.sample_message_sender.send_direct_otp_message(
                recipient=MessageRequestRecipient(
                    user_id=created_user.id,
                    fullname=created_user.fullname,
                    email=created_user.email,
                    phone=Utils.normalize_phone(f"{created_user.phone_ext}{created_user.phone}"),
                    web_push_token=[devices.get(PushProviderType.WEB_PUSH)],
                    ios_push_token=[devices.get(PushProviderType.APNS)],
                    android_push_token=[devices.get(PushProviderType.FIREBASE)]
                ),
                context={
                    "otp": self.otp,
                }
            )

        # RUN BackgroundTasks
        await self.run_background_tasks()

@inject
class SampleMessageSender(BaseMessageSender):
    """Handles all account security and verification related messages"""
    def __init__(self,
                 messaging_dispatcher: MessageDispatcher,
                 active_auditor_service: ActiveAuditorService,
                 message_recipient_builder: MessageRecipientBuilder
                 ):
        super().__init__(messaging_dispatcher=messaging_dispatcher,
            active_auditor_service=active_auditor_service,
            message_recipient_builder=message_recipient_builder
        )

        self._enable_out_messaging = True


    async def send_otp_message(self, recipient_user_id: MessageRecipientUserId,
                                            context_modules:List[MessageContextModule], extra_context: dict[str, str]):
        await self._send_message(
            recipient_user_id=recipient_user_id,
            template="otp",
            context_modules=context_modules,
            category=MessageCategory.ONBOARDING,
            default_channels=[
                MessageChannel.SMS,
                MessageChannel.WHATSAPP,
                MessageChannel.EMAIL,
                MessageChannel.WEB_PUSH,
                MessageChannel.PUSH
            ],
            extra_context=extra_context
        )

    async def send_direct_otp_message(self, recipient: MessageRequestRecipient,  context: dict[str, str]):
        await self._send_direct_message(
            recipient=recipient,
            template="otp",
            context=context,
            category=MessageCategory.VERIFICATION,
            default_channels=[
                MessageChannel.SMS,
                MessageChannel.WHATSAPP,
                MessageChannel.EMAIL,
                MessageChannel.WEB_PUSH,
                MessageChannel.PUSH
            ]
        )
