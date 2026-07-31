"""Interfaz de linea de comandos del cliente."""

import asyncio

from client.openai_client import MCPOpenAIClient
from config import settings
from server.currency_tools import MONEDAS_HABITUALES

AYUDA = """Herramientas disponibles en el servidor MCP:
  - convert_currency: convierte una cantidad entre dos divisas.
  - get_exchange_rates: tasas de cambio de una moneda base.
  - geocode_city: coordenadas de una ciudad por su nombre.
  - get_current_weather: clima actual por coordenadas.
  - get_weather_forecast: pronostico de varios dias por coordenadas.

Ejemplos de consultas en lenguaje natural:
  - Convierte 100 USD a EUR
  - Cual es el clima actual en Madrid?
  - Dame el pronostico del tiempo para Nueva York
  - Que coordenadas tiene Tokio?

Comandos: /ayuda | /monedas | /salir"""


async def run_cli() -> None:
    print("=" * 62)
    print("Cliente OpenAI + servidor MCP local (finanzas y clima)")
    print(f"Servidor MCP: {settings.MCP_URL} | Modelo: {settings.OPENAI_MODEL}")
    print("Escribe tu consulta en lenguaje natural. Comandos: /ayuda /monedas /salir")
    print("=" * 62)

    try:
        async with MCPOpenAIClient() as client:
            print(f"[info] Conectado al servidor MCP. Herramientas: {', '.join(client.tool_names())}")
            await _loop(client)
    except Exception as error:  # noqa: BLE001 - p. ej. servidor MCP apagado
        print(f"[error] No se pudo conectar con el servidor MCP en {settings.MCP_URL}: {error}")
        print("Arranca primero el servidor en otra terminal: python main_server.py")


async def _loop(client: MCPOpenAIClient) -> None:
    while True:
        try:
            user_text = (await asyncio.to_thread(input, "\nTu: ")).strip()
        except (KeyboardInterrupt, EOFError):
            print("\nHasta pronto.")
            return

        if not user_text:
            continue
        if user_text.lower() == "/salir":
            print("Hasta pronto.")
            return
        if user_text.lower() == "/ayuda":
            print(AYUDA)
            continue
        if user_text.lower() == "/monedas":
            print("Codigos de moneda habituales: " + ", ".join(MONEDAS_HABITUALES))
            print("(la API soporta la mayoria de codigos ISO 4217)")
            continue

        try:
            answer = await client.ask(user_text)
        except Exception as error:  # noqa: BLE001 - errores de OpenAI o del servidor
            print(f"[error] No se pudo completar la consulta: {error}")
            continue
        print(f"Asistente: {answer}")
