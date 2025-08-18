from contextlib import asynccontextmanager
from logging import Logger

from libre_fastapi_jwt.exceptions import AuthJWTException
from starlette import status




from appodus_utils.common.utils_settings import utils_settings
from appodus_utils.config.bootstrap import BaseDiBootstrap

from appodus_utils.db.session import close_db_engine
from appodus_utils.domain import utils_router
from appodus_utils.domain.client.controller import client_router
from appodus_utils.domain.user.auth.active_auditor.global_context import init_auth_context
from appodus_utils.exception.exception_handlers import (
    appodus_exception_handler,
    http_error_handler,
    validation_exception_handler,
    generic_exception_handler,
    authjwt_exception_handler
)
from appodus_utils.exception.exceptions import AppodusBaseException
from appodus_utils.middleware.db_session_middleware import DBSessionMiddleware
from appodus_utils.middleware.request_logging_middleware import RequestLoggingMiddleware
from fastapi import FastAPI, Depends
from fastapi.exceptions import RequestValidationError
from httpx import AsyncClient
from kink import di
from starlette.exceptions import HTTPException

logger: Logger = di['logger']
httpx_client: AsyncClient = di[AsyncClient]


@asynccontextmanager
async def lifespan_event(app: FastAPI):
    logger.debug("Running lifespan..")

    logger.debug("Done running lifespan")
    yield
    await close_db_engine()
    await httpx_client.aclose()


fast_api_app = FastAPI(lifespan=lifespan_event, dependencies=[Depends(init_auth_context)])

# Routers
fast_api_app.include_router(client_router)
fast_api_app.include_router(utils_router)

# Exception Handlers
# Custom appodus exceptions
fast_api_app.add_exception_handler(AppodusBaseException, appodus_exception_handler)
# AuthJWTException
fast_api_app.add_exception_handler(AuthJWTException, authjwt_exception_handler)
# FastAPI built-in ones
fast_api_app.add_exception_handler(HTTPException, http_error_handler)
fast_api_app.add_exception_handler(RequestValidationError, validation_exception_handler)
# Catch-all fallback
fast_api_app.add_exception_handler(Exception, generic_exception_handler)
#
# # Middlewares
# app.add_middleware(ClientAuthMiddleware)
fast_api_app.add_middleware(DBSessionMiddleware)
fast_api_app.add_middleware(RequestLoggingMiddleware)


@fast_api_app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    # logger.logger.error("Starting dev server:")
    uvicorn.run(fast_api_app, host="127.0.0.1", port=8000)
