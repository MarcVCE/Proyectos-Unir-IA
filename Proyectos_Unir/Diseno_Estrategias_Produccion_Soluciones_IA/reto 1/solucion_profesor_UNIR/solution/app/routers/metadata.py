"""Endpoint POST /api/metadata/generate."""

from fastapi import APIRouter, HTTPException
from openai import OpenAIError

from app.models.metadata import MetadataRequest, MetadataResponse
from app.services import seo_service

router = APIRouter(prefix="/api/metadata", tags=["metadata"])


@router.post("/generate", response_model=MetadataResponse)
def generate_metadata(request: MetadataRequest) -> MetadataResponse:
    try:
        return seo_service.generate_metadata(request)
    except OpenAIError as error:
        raise HTTPException(status_code=502, detail=f"Error de la API de OpenAI: {error}") from error
