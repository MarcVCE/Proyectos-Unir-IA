"""Endpoint POST /api/social/summaries."""

from fastapi import APIRouter, HTTPException
from openai import OpenAIError

from app.models.social import SocialRequest, SocialResponse
from app.services import seo_service

router = APIRouter(prefix="/api/social", tags=["social"])


@router.post("/summaries", response_model=SocialResponse)
def generate_social(request: SocialRequest) -> SocialResponse:
    try:
        return seo_service.generate_social(request)
    except OpenAIError as error:
        raise HTTPException(status_code=502, detail=f"Error de la API de OpenAI: {error}") from error
