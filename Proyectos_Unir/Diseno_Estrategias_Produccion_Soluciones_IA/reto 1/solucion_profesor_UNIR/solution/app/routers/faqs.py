"""Endpoint POST /api/faqs/extract."""

from fastapi import APIRouter, HTTPException
from openai import OpenAIError

from app.models.faqs import FAQRequest, FAQResponse
from app.services import seo_service

router = APIRouter(prefix="/api/faqs", tags=["faqs"])


@router.post("/extract", response_model=FAQResponse)
def extract_faqs(request: FAQRequest) -> FAQResponse:
    try:
        return seo_service.extract_faqs(request)
    except OpenAIError as error:
        raise HTTPException(status_code=502, detail=f"Error de la API de OpenAI: {error}") from error
