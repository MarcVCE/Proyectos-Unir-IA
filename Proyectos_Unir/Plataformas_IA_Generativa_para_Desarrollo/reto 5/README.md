# Servidor MCP (FastMCP) + Cliente OpenAI — Monedas y Clima

Servidor **MCP con FastMCP** que expone **5 herramientas** sobre 2 APIs públicas
(**ExchangeRate-API** para divisas y **Open-Meteo** para geocodificación + clima) y un
**cliente OpenAI** (recurso de Azure, modelo `gpt-5`) que descubre esas herramientas y las
usa con *function calling*, encadenando llamadas (geocodificación → clima). Incluye una
**CLI** en lenguaje natural.

Todo el proyecto está implementado en el notebook `chatbot_mcp_monedas_clima.ipynb`, con
cada sección rotulada con su archivo equivalente (`server/…`, `client/…`, `config/…`,
`main_server.py`, `main_client.py`).

## Las 5 herramientas

1. `convert_currency(amount, from_currency, to_currency)` — conversión entre divisas (ExchangeRate).
2. `get_exchange_rates(base_currency)` — tasas de una moneda base frente a muchas (ExchangeRate).
3. `geocode_city(city)` — ciudad → lat/lon, país, zona horaria (Open-Meteo).
4. `get_current_weather(latitude, longitude)` — clima actual (Open-Meteo).
5. `get_weather_forecast(latitude, longitude, days)` — pronóstico de varios días (Open-Meteo).

## Requisitos previos

- Python 3.11+ (probado en 3.13).
- Una clave gratuita de **ExchangeRate-API** (https://www.exchangerate-api.com/) para las
  herramientas de divisas. **Open-Meteo no necesita clave.**
- Acceso a un modelo OpenAI `gpt-4o` / `gpt-4.1` / `gpt-5` (aquí, vía recurso de Azure).

## Instalación

```bash
# 1) Crear y activar un entorno virtual
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# 2) Instalar dependencias
pip install -r requirements.txt
```

> En Windows, `pywin32` se instala automáticamente (lo requiere el paquete `mcp`). Si al
> importar FastMCP ves un error de `win32api`, ejecuta una vez:
> `python -m pywin32_postinstall -install` y reinicia el kernel.

## Configuración (`.env`)

Copia `.env.example` a `.env` y rellena tus valores:

```dotenv
# OpenAI vía Azure (cliente)
AZURE_OPENAI_ENDPOINT=https://TU-RECURSO.services.ai.azure.com/openai/v1/
AZURE_OPENAI_API_KEY=tu_clave_de_azure
OPENAI_MODEL=gpt-5

# ExchangeRate-API (clave gratuita)
API_KEY_EXCHANGE=tu_api_key_de_exchangerate

# Open-Meteo: NO necesita clave
MCP_HOST=127.0.0.1
MCP_PORT=8000

# Opcionales (límites del cliente)
MCP_MAX_PASOS=8
MCP_MAX_REINTENTOS=2
```

## Ejecución

El proyecto está pensado para ejecutarse en el notebook, de arriba abajo:

1. Instalar dependencias (celda 2) y reiniciar el kernel.
2. Cargar configuración, definir herramientas y **arrancar el servidor** (sección 8 →
   equivale a `main_server.py`: `mcp.run_http_async(host, port)` en `localhost:8000`).
3. **Opción A**: consultas directas con `await cliente.ask("...")`.
4. **Opción B**: CLI interactiva con `await run_cli()` (equivale a `main_client.py`).
5. Sección 11: probar el servidor MCP sin OpenAI. Sección 12: pruebas automatizadas.

### Ejemplos de comandos en la CLI

```
Convierte 100 USD a EUR
¿Cuál es el clima actual en Madrid?
Dame el pronóstico del tiempo para Nueva York
¿Qué coordenadas tiene Tokio?
/ayuda        (ayuda y ejemplos)
/monedas      (códigos de moneda habituales)
/salir        (terminar)
```

## Pruebas

La sección 12 del notebook ejecuta pruebas con `ipytest`/`pytest` que verifican la
geocodificación, el flujo geocodificación → clima, la normalización del pronóstico, la
conversión de divisas (se omite si no hay `API_KEY_EXCHANGE`) y la validación de códigos
de moneda.
