import json
from contextvars import Token
from datetime import timedelta, datetime
from logging import Logger
from typing import Any, Union, Dict, Optional, List

from fastapi import BackgroundTasks
from fastapi.encoders import jsonable_encoder
from kink import inject, di
from libre_fastapi_jwt import AuthJWT

from appodus_utils import Utils
from appodus_utils.db.redis_utils import RedisUtils
from appodus_utils.domain.user.auth.active_auditor.context import ActiveAuditorContext
from appodus_utils.domain.user.auth.active_auditor.models import ActiveAuditor
from appodus_utils.domain.user.models import UserPersona
from appodus_utils.exception.exceptions import NoActiveSessionException

logger: Logger = di['logger']


@inject
class ActiveAuditorService:

    @staticmethod
    async def login(user_id: str, auth_json: Any) -> ActiveAuditor:
        access_token_expire_seconds = Utils.get_from_env_fail_if_not_exists("ACCESS_TOKEN_EXPIRE_SECONDS")
        time_to_live = timedelta(seconds=int(access_token_expire_seconds))
        active_auditor = ActiveAuditor(**auth_json)
        active_auditor_json = jsonable_encoder(active_auditor)
        active_auditor_str = json.dumps(active_auditor_json)
        await RedisUtils.set_redis(user_id, active_auditor_str, time_to_live)

        return active_auditor

    async def init_context(self, background_tasks: BackgroundTasks, authorizer: AuthJWT) -> tuple[
        Optional[Token[BackgroundTasks]], Optional[Token[AuthJWT]], Optional[Token[ActiveAuditor]]]:
        background_tasks_context_token: Token[BackgroundTasks] = ActiveAuditorContext.set_background_tasks_context(
            background_tasks)
        authorizer_context_token: Token[AuthJWT] = ActiveAuditorContext.set_authorizer_context(authorizer)

        user_id = await self.get_active_user_id(authorizer, False)
        if not user_id:
            return background_tasks_context_token, authorizer_context_token, None

        active_auditor_data = await RedisUtils.get_redis(user_id)
        if not active_auditor_data:
            from appodus_utils.common.auth_utils import JwtAuthUtils
            await JwtAuthUtils.revoke_token(authorizer=authorizer)
            raise NoActiveSessionException()
        active_auditor_data = json.loads(active_auditor_data)

        active_auditor = ActiveAuditor(**active_auditor_data)
        active_auditor_context_token: Token[ActiveAuditor] = ActiveAuditorContext.set_active_auditor_context(
            active_auditor)

        return background_tasks_context_token, authorizer_context_token, active_auditor_context_token

    @staticmethod
    async def reset_context(background_tasks_context_token: Optional[Token[BackgroundTasks]],
                            authorizer_context_token: Optional[Token[AuthJWT]],
                            active_auditor_context_token: Optional[Token[ActiveAuditor]]):
        if background_tasks_context_token:
            ActiveAuditorContext.reset_background_tasks_context(background_tasks_context_token)
        if authorizer_context_token:
            ActiveAuditorContext.reset_authorizer_context(authorizer_context_token)
        if active_auditor_context_token:
            ActiveAuditorContext.reset_active_auditor_context(active_auditor_context_token)

    @staticmethod
    async def get_background_tasks_from_context() -> BackgroundTasks:
        background_tasks: BackgroundTasks = ActiveAuditorContext.get_background_tasks_from_context()
        return background_tasks

    @staticmethod
    async def get_combined_authorizer_from_context() -> tuple[ActiveAuditor, AuthJWT]:
        active_auditor: ActiveAuditor = ActiveAuditorContext.get_active_auditor_from_context()
        authorizer: AuthJWT = ActiveAuditorContext.get_authorizer_from_context()
        return active_auditor, authorizer


    async def get_active_user_id(self, authorizer: AuthJWT = None, jwt_required: bool = True) -> Optional[str]:
        try:
            if not authorizer:
                authorizer = await self.get_authorizer_from_context()
            authorizer.jwt_required()
            return authorizer.get_jwt_subject()
        except Exception as e:
            if jwt_required:
                raise
            return None

    @staticmethod
    async def get_authorizer_from_context() -> AuthJWT:
        return ActiveAuditorContext.get_authorizer_from_context()

    async def get_user_id(self) -> Optional[str]:
        user, _ = await self.get_combined_authorizer_from_context()
        if user:
            return user.id

        return None

    async def get_dob(self) -> Optional[datetime]:
        user, _ = await self.get_combined_authorizer_from_context()
        if user:
            return user.dob

        return None

    async def get_firstname(self) -> Optional[str]:
        user, _ = await self.get_combined_authorizer_from_context()
        if user:
            return user.firstname

        return None

    async def get_lastname(self) -> Optional[str]:
        user, _ = await self.get_combined_authorizer_from_context()
        if user:
            return user.lastname

        return None

    async def get_fullname(self) -> Optional[str]:
        user, _ = await self.get_combined_authorizer_from_context()
        if user:
            return user.fullname

        return None

    async def get_phone(self) -> Optional[str]:
        user, _ = await self.get_combined_authorizer_from_context()
        if user:
            return user.phone

        return None

    async def get_email(self) -> Optional[str]:
        user, _ = await self.get_combined_authorizer_from_context()
        if user:
            return user.email

        return None

    async def get_user_type(self) -> Optional[str]:
        user, _ = await self.get_combined_authorizer_from_context()
        if user:
            return user.user_type

        return None

    async def get_personas(self) -> Optional[List[UserPersona]]:
        user, _ = await self.get_combined_authorizer_from_context()
        if user:
            return user.personas

        return None

    async def get_last_active_date(self) -> Optional[datetime]:
        user, _ = await self.get_combined_authorizer_from_context()
        if user:
            return user.last_active_date

        return None

    async def has_profile_picture(self) -> Optional[bool]:
        user, _ = await self.get_combined_authorizer_from_context()
        if user:
            return user.has_profile_picture

        return None

    async def has_selfie_picture(self) -> Optional[bool]:
        user, _ = await self.get_combined_authorizer_from_context()
        if user:
            return user.has_selfie_picture

        return None

    async def is_phone_validated(self) -> Optional[bool]:
        user, _ = await self.get_combined_authorizer_from_context()
        if user:
            return user.phone_validated

        return None

    async def is_email_validated(self) -> Optional[bool]:
        user, _ = await self.get_combined_authorizer_from_context()
        if user:
            return user.email_validated

        return None

    async def get_languages(self) -> Optional[List[str]]:
        user, _ = await self.get_combined_authorizer_from_context()
        if user:
            return user.languages

        return None

    async def is_bvn_validated(self) -> Optional[bool]:
        user, _ = await self.get_combined_authorizer_from_context()
        if user:
            return user.bvn_validated

        return None

    async def is_identity_validated(self) -> Optional[bool]:
        user, _ = await self.get_combined_authorizer_from_context()
        if user:
            return user.identity_validated

        return None

    async def is_address_validated(self) -> Optional[bool]:
        user, _ = await self.get_combined_authorizer_from_context()
        if user:
            return user.address_validated

        return None

    async def get_profile_id(self) -> Optional[str]:
        user, _ = await self.get_combined_authorizer_from_context()
        if user:
            return user.profile_id

        return None

    async def get_wallet_id(self) -> Optional[str]:
        user, _ = await self.get_combined_authorizer_from_context()
        if user:
            return user.wallet_id

        return None

    async def get_escrow_id(self) -> Optional[str]:
        user, _ = await self.get_combined_authorizer_from_context()
        if user:
            return user.escrow_id

        return None

    async def get_lien_id(self) -> Optional[str]:
        user, _ = await self.get_combined_authorizer_from_context()
        if user:
            return user.lien_id

        return None

    async def get_inbox_id(self) -> Optional[str]:
        user, _ = await self.get_combined_authorizer_from_context()
        if user:
            return user.inbox_id

        return None

    async def update(self, obj_in: Union[Any, Dict[str, Any]]) -> ActiveAuditor:
        active_auditor, _ = await self.get_combined_authorizer_from_context()
        active_auditor_data = jsonable_encoder(active_auditor)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True, exclude_none=True)

        for field in active_auditor_data:
            if field in update_data:
                try:
                    setattr(active_auditor, field, update_data[field])
                except AttributeError as e:
                    pass

        active_auditor_data = jsonable_encoder(active_auditor)
        return await self.login(active_auditor.id, active_auditor_data)
