"""Servidor MCP con las 5 herramientas de APIs externas (FastMCP)."""

import logging

from fastmcp import FastMCP

from server.currency_tools import convert_currency, get_exchange_rates
from server.geocoding_tools import geocode_city
from server.weather_tools import get_current_weather, get_weather_forecast

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)

mcp = FastMCP(
    name="finanzas-y-clima",
    instructions=(
        "Herramientas de conversion de monedas (ExchangeRate-API) y de clima "
        "(Open-Meteo). Para el clima de una ciudad, primero usa geocode_city "
        "para obtener sus coordenadas y despues get_current_weather o "
        "get_weather_forecast con esas coordenadas."
    ),
)

# Registro de las 5 herramientas: 2 de monedas + 1 de geocodificacion + 2 de clima.
mcp.tool(convert_currency)
mcp.tool(get_exchange_rates)
mcp.tool(geocode_city)
mcp.tool(get_current_weather)
mcp.tool(get_weather_forecast)
