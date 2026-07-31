"""Endpoint POST /api/articles/generate."""

from fastapi import APIRouter, HTTPException
from openai import OpenAIError

from app.models.articles import ArticleRequest, ArticleResponse
from app.services import seo_service

router = APIRouter(prefix="/api/articles", tags=["articles"])


@router.post("/generate", response_model=ArticleResponse)
def generate_article(request: ArticleRequest) -> ArticleResponse:
    try:
        return seo_service.generate_article(request)
    except OpenAIError as error:
        raise HTTPException(status_code=502, detail=f"Error de la API de OpenAI: {error}") from error
