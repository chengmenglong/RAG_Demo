"""Process health endpoint."""

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from app import __version__

router = APIRouter()


class HealthResponse(BaseModel):
    """Stable response for the minimal process health check."""

    status: Literal["ok"]
    version: str


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Report that the API process is alive without contacting external services."""

    return HealthResponse(status="ok", version=__version__)
