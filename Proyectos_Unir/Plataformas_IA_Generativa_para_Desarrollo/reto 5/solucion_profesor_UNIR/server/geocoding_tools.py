"""Herramienta de geocodificacion (Open-Meteo): ciudad -> coordenadas."""

import logging

from server.api_clients import fetch_geocoding

logger = logging.getLogger(__name__)


def geocode_city(city: str) -> dict:
    """Devuelve las coordenadas y datos basicos de una ciudad por su nombre.

    Args:
        city: nombre de la ciudad (p. ej. Madrid, Nueva York, Tokio).

    Returns:
        Diccionario con nombre normalizado, latitud, longitud, pais y zona horaria.
    """
    city = (city or "").strip()
    if not city:
        raise ValueError("city no puede estar vacio")

    result = fetch_geocoding(city)
    return {
        "city": result.get("name"),
        "latitude": result.get("latitude"),
        "longitude": result.get("longitude"),
        "country": result.get("country"),
        "timezone": result.get("timezone"),
    }
