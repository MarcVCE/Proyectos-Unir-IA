"""Endpoint POST /api/keywords/generate."""

from fastapi import APIRouter, HTTPException
from openai import OpenAIError

from app.models.keywords import KeywordRequest, KeywordResponse
from app.services import seo_service

router = APIRouter(prefix="/api/keywords", tags=["keywords"])


@router.post("/generate", response_model=KeywordResponse)
def generate_keywords(request: KeywordRequest) -> KeywordResponse:
    try:
        return seo_service.generate_keywords(request)
    except OpenAIError as error:
        raise HTTPException(status_code=502, detail=f"Error de la API de OpenAI: {error}") from error
