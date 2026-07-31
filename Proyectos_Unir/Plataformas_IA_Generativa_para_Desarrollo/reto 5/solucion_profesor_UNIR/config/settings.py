"""Configuracion y variables de entorno del proyecto."""

import os

from dotenv import load_dotenv

load_dotenv()

# Servidor MCP local
MCP_HOST = os.getenv("MCP_HOST", "127.0.0.1")
MCP_PORT = int(os.getenv("MCP_PORT", "8000"))
MCP_URL = f"http://{MCP_HOST}:{MCP_PORT}/mcp/"

# Modelo de OpenAI para el cliente (gpt-4o-mini es el mas economico)
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# ExchangeRate-API: con API key se usa el endpoint v6 oficial; sin ella se usa
# el endpoint abierto del mismo proveedor (open.er-api.com), que no requiere key.
EXCHANGE_API_KEY = os.getenv("API_KEY_EXCHANGE", "").strip()
BASE_URL_EXCHANGE_V6 = "https://v6.exchangerate-api.com/v6"
BASE_URL_EXCHANGE_OPEN = "https://open.er-api.com/v6"

# Open-Meteo: completamente gratuita, sin API key
BASE_URL_WEATHER = "https://api.open-meteo.com/v1"
BASE_URL_GEOCODING = "https://geocoding-api.open-meteo.com/v1/search"

# Timeout por defecto para llamadas HTTP a APIs externas (segundos)
HTTP_TIMEOUT = 10
