"""FastAPI application assembly and request tracking middleware."""

from collections.abc import Awaitable, Callable
from uuid import uuid4

from fastapi import FastAPI, Request, Response

from app.api.v1.router import router as api_router

REQUEST_ID_HEADER = "X-Request-ID"
_REQUEST_ID_MAX_LENGTH = 128


def _is_valid_request_id(value: str | None) -> bool:
    """Accept a bounded, printable request ID without trusting arbitrary input."""

    if not value or len(value) > _REQUEST_ID_MAX_LENGTH:
        return False
    return all(character.isalnum() or character in "._:-" for character in value)


def create_app() -> FastAPI:
    """Build the application and register the versioned API router exactly once."""

    application = FastAPI(title="RAG Demo Backend", version="0.1.0")
    application.include_router(api_router)

    @application.middleware("http")
    async def request_id_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        incoming_request_id = request.headers.get(REQUEST_ID_HEADER)
        if incoming_request_id is not None and _is_valid_request_id(incoming_request_id):
            request_id = incoming_request_id
        else:
            request_id = str(uuid4())

        response = await call_next(request)
        response.headers[REQUEST_ID_HEADER] = request_id
        return response

    return application


app = create_app()
