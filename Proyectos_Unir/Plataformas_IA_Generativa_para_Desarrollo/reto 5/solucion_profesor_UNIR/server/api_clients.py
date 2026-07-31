"""Clientes HTTP para las APIs externas (ExchangeRate-API y Open-Meteo)."""

import logging

import requests

from config import settings

logger = logging.getLogger(__name__)


class ApiClientError(Exception):
    """Error controlado al consultar una API externa."""


def _get_json(url: str, params: dict | None = None) -> dict:
    """GET con timeout y errores de red convertidos a ApiClientError."""
    try:
        response = requests.get(url, params=params, timeout=settings.HTTP_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.Timeout as error:
        raise ApiClientError(f"Timeout consultando {url}") from error
    except requests.HTTPError as error:
        status = error.response.status_code if error.response is not None else "?"
        raise ApiClientError(f"La API devolvio HTTP {status} para {url}") from error
    except requests.RequestException as error:
        raise ApiClientError(f"Error de red consultando {url}: {error}") from error
    except ValueError as error:
        raise ApiClientError(f"Respuesta no valida (no es JSON) de {url}") from error


def fetch_exchange_rates(base_currency: str) -> dict[str, float]:
    """Devuelve las tasas de cambio actuales para una moneda base.

    Con API_KEY_EXCHANGE configurada usa el endpoint oficial v6; sin ella usa
    el endpoint abierto del mismo proveedor (sin API key). Ambos devuelven las
    tasas frente a decenas de monedas.
    """
    if settings.EXCHANGE_API_KEY:
        url = f"{settings.BASE_URL_EXCHANGE_V6}/{settings.EXCHANGE_API_KEY}/latest/{base_currency}"
        data = _get_json(url)
        rates = data.get("conversion_rates")
    else:
        url = f"{settings.BASE_URL_EXCHANGE_OPEN}/latest/{base_currency}"
        data = _get_json(url)
        rates = data.get("rates")

    if data.get("result") != "success" or not isinstance(rates, dict):
        detail = data.get("error-type") or data.get("result") or "respuesta inesperada"
        raise ApiClientError(f"ExchangeRate-API fallo para {base_currency}: {detail}")

    logger.info("Tasas de cambio obtenidas para %s (%d monedas)", base_currency, len(rates))
    return rates


def fetch_geocoding(city: str) -> dict:
    """Devuelve el primer resultado de geocodificacion para una ciudad."""
    data = _get_json(
        settings.BASE_URL_GEOCODING,
        params={"name": city, "count": 1, "language": "es", "format": "json"},
    )
    results = data.get("results")
    if not results:
        raise ApiClientError(f"No se encontro ninguna ciudad llamada '{city}'")
    logger.info("Geocodificada '%s' -> %s", city, results[0].get("name"))
    return results[0]


def fetch_current_weather(latitude: float, longitude: float) -> dict:
    """Devuelve el bloque de clima actual de Open-Meteo para unas coordenadas."""
    data = _get_json(
        f"{settings.BASE_URL_WEATHER}/forecast",
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,"
            "weather_code,wind_speed_10m",
            "timezone": "auto",
        },
    )
    current = data.get("current")
    if not current:
        raise ApiClientError("Open-Meteo no devolvio datos de clima actual")
    return current


def fetch_forecast(latitude: float, longitude: float, days: int) -> dict:
    """Devuelve el bloque diario de pronostico de Open-Meteo."""
    data = _get_json(
        f"{settings.BASE_URL_WEATHER}/forecast",
        params={
            "latitude": latitude,
            "longitude": longitude,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,"
            "weather_code",
            "forecast_days": days,
            "timezone": "auto",
        },
    )
    daily = data.get("daily")
    if not daily:
        raise ApiClientError("Open-Meteo no devolvio datos de pronostico")
    return daily


# Descripciones en español de los codigos meteorologicos WMO de Open-Meteo.
WEATHER_CODES: dict[int, str] = {
    0: "cielo despejado",
    1: "principalmente despejado",
    2: "parcialmente nublado",
    3: "cubierto",
    45: "niebla",
    48: "niebla con escarcha",
    51: "llovizna ligera",
    53: "llovizna moderada",
    55: "llovizna intensa",
    61: "lluvia ligera",
    63: "lluvia moderada",
    65: "lluvia intensa",
    71: "nieve ligera",
    73: "nieve moderada",
    75: "nieve intensa",
    80: "chubascos ligeros",
    81: "chubascos moderados",
    82: "chubascos violentos",
    95: "tormenta",
    96: "tormenta con granizo ligero",
    99: "tormenta con granizo intenso",
}


def describe_weather_code(code: int | None) -> str:
    """Traduce un codigo WMO a una descripcion legible en español."""
    if code is None:
        return "sin datos"
    return WEATHER_CODES.get(int(code), f"codigo WMO {code}")
