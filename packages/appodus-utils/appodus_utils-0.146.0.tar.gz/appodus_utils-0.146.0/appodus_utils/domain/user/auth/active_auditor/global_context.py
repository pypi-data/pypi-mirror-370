from fastapi import Depends, BackgroundTasks
from kink import di
from libre_fastapi_jwt import AuthJWT, AuthJWTBearer
from starlette.requests import Request

from appodus_utils.common.context_utils import ContextUtils
from appodus_utils.domain.user.auth.active_auditor.service import ActiveAuditorService

auth_JWT_bearer: AuthJWTBearer = di[AuthJWTBearer]
active_auditor_service: ActiveAuditorService = di[ActiveAuditorService]

async def init_auth_context(request: Request, background_tasks: BackgroundTasks, authorizer: AuthJWT = Depends(auth_JWT_bearer)):
    di[ContextUtils]  = lambda _di: ContextUtils(request)

    background_tasks_context_token, authorizer_context_token, active_auditor_context_token = await active_auditor_service.init_context(
        background_tasks, authorizer)
    yield
    await active_auditor_service.reset_context(background_tasks_context_token, authorizer_context_token, active_auditor_context_token)
