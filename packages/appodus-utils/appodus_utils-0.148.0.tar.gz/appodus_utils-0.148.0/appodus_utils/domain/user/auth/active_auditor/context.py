from contextvars import ContextVar, Token
from logging import Logger

from fastapi import BackgroundTasks
from kink import di
from libre_fastapi_jwt import AuthJWT

from appodus_utils.domain.user.auth.active_auditor.models import ActiveAuditor
from appodus_utils.exception.exceptions import NoActiveSessionException

logger: Logger = di['logger']
# Context variable to hold BackgroundTasks, ActiveAuditor and AuthJWT per context
background_tasks_ctx: ContextVar[BackgroundTasks] = ContextVar("background_tasks_ctx")
active_auditor_ctx: ContextVar[ActiveAuditor] = ContextVar("active_auditor_ctx")
authorizer_ctx: ContextVar[AuthJWT] = ContextVar("authorizer_ctx")


class ActiveAuditorContext:

    # ActiveAuditor
    @staticmethod
    def set_active_auditor_context(active_auditor: ActiveAuditor) -> Token[ActiveAuditor]:
        logger.debug(f"Setting active auditor in context: {active_auditor}")
        return active_auditor_ctx.set(active_auditor)

    @staticmethod
    def reset_active_auditor_context(token: Token[ActiveAuditor]):
        return active_auditor_ctx.reset(token)

    @staticmethod
    def get_active_auditor_from_context() -> ActiveAuditor:
        error_msg = (
            "No active_auditor found in context. "
            "Ensure you're within a request/task context that has set this value."
        )
        try:
            active_auditor = active_auditor_ctx.get()
            if not active_auditor:
                logger.error("active_auditor_ctx contains None.")
                raise NoActiveSessionException(error_msg)
            logger.debug(f"Retrieved active auditor from context: {active_auditor}")
            return active_auditor
        except LookupError:
            logger.exception("active_auditor_ctx was not set.")
            raise NoActiveSessionException(error_msg)

    # AuthJWT
    @staticmethod
    def set_authorizer_context(authorizer: AuthJWT) -> Token[AuthJWT]:
        logger.debug(f"Setting active auditor in context: {authorizer}")
        return authorizer_ctx.set(authorizer)

    @staticmethod
    def reset_authorizer_context(token: Token[AuthJWT]):
        return authorizer_ctx.reset(token)

    @staticmethod
    def get_authorizer_from_context() -> AuthJWT:
        error_msg = (
            "No authorizer found in context. "
            "Ensure you're within a request/task context that has set this value."
        )
        try:
            authorizer = authorizer_ctx.get()
            if not authorizer:
                logger.error("authorizer_ctx contains None.")
                raise NoActiveSessionException(error_msg)
            logger.debug(f"Retrieved active auditor from context: {authorizer}")
            return authorizer
        except NoActiveSessionException:
            logger.exception("authorizer_ctx was not set.")
            raise RuntimeError(error_msg)

    # BackgroundTasks
    @staticmethod
    def set_background_tasks_context(background_tasks: BackgroundTasks) -> Token[BackgroundTasks]:
        logger.debug(f"Setting background_tasks in context: {background_tasks}")
        return background_tasks_ctx.set(background_tasks)

    @staticmethod
    def reset_background_tasks_context(token: Token[BackgroundTasks]):
        return background_tasks_ctx.reset(token)

    @staticmethod
    def get_background_tasks_from_context() -> BackgroundTasks:
        error_msg = (
            "No background_tasks found in context. "
            "Ensure you're within a request/task context that has set this value."
        )
        try:
            background_tasks = background_tasks_ctx.get()
            if not background_tasks:
                logger.error("background_tasks_ctx contains None.")
                raise NoActiveSessionException(error_msg)
            logger.debug(f"Retrieved background_tasks from context: {background_tasks}")
            return background_tasks
        except LookupError:
            logger.exception("background_tasks_ctx was not set.")
            raise NoActiveSessionException(error_msg)
