"""Logica de negocio: prompts especificos + llamadas al SDK de OpenAI.

Todas las funciones usan salidas estructuradas (``chat.completions.parse`` con
``response_format`` = modelo Pydantic), de modo que la respuesta de la IA llega
ya validada contra el contrato del endpoint. Funciona igual con ``OpenAI`` y
con ``AzureOpenAI`` (gpt-4o / gpt-4o-mini de Azure for students).
"""

import json
from typing import TypeVar

from pydantic import BaseModel

from app.config import OPENAI_MODEL, get_client
from app.models.articles import ArticleRequest, ArticleResponse
from app.models.faqs import FAQ, FAQRequest, FAQResponse
from app.models.keywords import KeywordRequest, KeywordResponse
from app.models.metadata import MetadataRequest, MetadataResponse
from app.models.social import SocialRequest, SocialResponse

T = TypeVar("T", bound=BaseModel)


def _generate(system_prompt: str, user_prompt: str, response_model: type[T]) -> T:
    """Llamada generica con salida estructurada validada por Pydantic."""
    client = get_client()
    completion = client.chat.completions.parse(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format=response_model,
    )
    parsed = completion.choices[0].message.parsed
    if parsed is None:
        raise ValueError("La IA no devolvio una respuesta estructurada valida")
    return parsed


def generate_keywords(request: KeywordRequest) -> KeywordResponse:
    return _generate(
        system_prompt=(
            "Eres un especialista SEO. Genera keywords en el idioma indicado: "
            "keywords semilla, variantes long-tail, preguntas que la gente busca "
            "y la clasificacion de intencion (informacional o transaccional) de "
            "cada keyword semilla y long-tail."
        ),
        user_prompt=(
            f"Tema principal: {request.topic}\n"
            f"Industria: {request.industry}\n"
            f"Idioma: {request.language}"
        ),
        response_model=KeywordResponse,
    )


def generate_article(request: ArticleRequest) -> ArticleResponse:
    return _generate(
        system_prompt=(
            "Eres un redactor SEO senior. Escribe un articulo con estructura SEO: "
            "un titulo H1 con la keyword principal, secciones H2 con subsecciones H3 "
            "jerarquicas, densidad natural de keywords (sin keyword stuffing, entre "
            "1 y 2 por ciento), cubriendo la intencion de busqueda, y llamadas a la "
            "accion coherentes con el contenido. Estima keyword_density en %."
        ),
        user_prompt=(
            f"Keyword principal: {request.main_keyword}\n"
            f"Keywords secundarias: {', '.join(request.secondary_keywords) or 'ninguna'}\n"
            f"Longitud objetivo: {request.word_count} palabras\n"
            f"Tono: {request.tone}"
        ),
        response_model=ArticleResponse,
    )


def generate_metadata(request: MetadataRequest) -> MetadataResponse:
    return _generate(
        system_prompt=(
            "Eres un especialista en SEO on-page. Genera entre 3 y 5 variantes de "
            "meta title (maximo 60 caracteres) y entre 3 y 5 de meta description "
            "(maximo 160 caracteres), optimizadas para CTR, incluyendo la keyword "
            "principal y lenguaje persuasivo. Rellena char_count con la longitud real."
        ),
        user_prompt=(
            f"Titulo del articulo: {request.article_title}\n"
            f"Keyword principal: {request.main_keyword}\n"
            f"Extracto: {request.article_excerpt or '(no disponible)'}"
        ),
        response_model=MetadataResponse,
    )


def _faq_json_ld(faqs: list[FAQ]) -> str:
    """Construye el esquema JSON-LD FAQPage de forma determinista."""
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": faq.question,
                "acceptedAnswer": {"@type": "Answer", "text": faq.answer},
            }
            for faq in faqs
        ],
    }
    return json.dumps(schema, ensure_ascii=False, indent=2)


def extract_faqs(request: FAQRequest) -> FAQResponse:
    response = _generate(
        system_prompt=(
            "Eres un especialista SEO. Extrae del articulo las preguntas mas "
            "relevantes y naturales que responderia (rich snippets FAQPage) y "
            "redacta una respuesta corta y util (50-150 palabras) por pregunta. "
            f"Genera como maximo {request.max_questions} preguntas. Deja "
            "json_ld_schema como cadena vacia: se calcula despues."
        ),
        user_prompt=f"Articulo:\n{request.article_content}",
        response_model=FAQResponse,
    )
    # El JSON-LD se construye en el servidor a partir de las FAQs validadas:
    # asi el codigo para rich snippets siempre es JSON valido.
    response.json_ld_schema = _faq_json_ld(response.faqs)
    return response


def generate_social(request: SocialRequest) -> SocialResponse:
    platforms = ", ".join(request.target_platforms)
    response = _generate(
        system_prompt=(
            "Eres un community manager profesional. Genera contenido especifico "
            f"SOLO para estas plataformas: {platforms}. Adapta tono, longitud y "
            "formato a cada red: Twitter/X maximo 280 caracteres con hashtags; "
            "LinkedIn profesional con parrafos y CTA; Instagram caption cercana "
            "con emojis moderados y hashtags; Facebook conversacional. Deja a "
            "null las plataformas no solicitadas. Hashtags sin el simbolo #."
        ),
        user_prompt=(
            f"Titulo: {request.article_title}\n\nContenido:\n{request.article_content}"
        ),
        response_model=SocialResponse,
    )
    # Garantia dura: no devolver plataformas que no se pidieron.
    for platform in ("twitter", "linkedin", "instagram", "facebook"):
        if platform not in request.target_platforms:
            setattr(response, platform, None)
    return response
