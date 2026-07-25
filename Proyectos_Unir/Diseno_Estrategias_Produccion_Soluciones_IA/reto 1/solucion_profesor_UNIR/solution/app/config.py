"""Configuracion: variables de entorno y cliente de OpenAI (Azure o directo)."""

import os
from functools import lru_cache

from dotenv import load_dotenv
from openai import AzureOpenAI, OpenAI

load_dotenv()

# Con Azure for students usa AZURE_OPENAI_* (gpt-4o / gpt-4o-mini).
# Si defines solo OPENAI_API_KEY se usa la API directa de OpenAI.
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION", "2024-10-21")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


@lru_cache
def get_client() -> OpenAI:
    """Devuelve el cliente adecuado segun la configuracion del entorno."""
    if AZURE_OPENAI_ENDPOINT:
        return AzureOpenAI(
            api_key=AZURE_OPENAI_API_KEY,
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_version=OPENAI_API_VERSION,
        )
    # Cliente directo: lee OPENAI_API_KEY del entorno.
    return OpenAI()
