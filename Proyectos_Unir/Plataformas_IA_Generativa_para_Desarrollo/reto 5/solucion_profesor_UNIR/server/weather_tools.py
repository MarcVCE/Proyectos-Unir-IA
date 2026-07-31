"""Herramientas de clima (Open-Meteo): requieren coordenadas (lat/lon)."""

import logging

from server.api_clients import describe_weather_code, fetch_current_weather, fetch_forecast

logger = logging.getLogger(__name__)


def _validar_coordenadas(latitude: float, longitude: float) -> None:
    if not -90 <= latitude <= 90:
        raise ValueError(f"latitude debe estar entre -90 y 90; recibido {latitude}")
    if not -180 <= longitude <= 180:
        raise ValueError(f"longitude debe estar entre -180 y 180; recibido {longitude}")


def get_current_weather(latitude: float, longitude: float) -> dict:
    """Devuelve el clima actual para unas coordenadas.

    Args:
        latitude: latitud en grados decimales (-90 a 90).
        longitude: longitud en grados decimales (-180 a 180).

    Returns:
        Diccionario con temperatura, sensacion termica, humedad, viento y descripcion.
    """
    _validar_coordenadas(latitude, longitude)
    current = fetch_current_weather(latitude, longitude)
    logger.info("Clima actual obtenido para (%s, %s)", latitude, longitude)
    return {
        "temperature_c": current.get("temperature_2m"),
        "feels_like_c": current.get("apparent_temperature"),
        "humidity_pct": current.get("relative_humidity_2m"),
        "wind_speed_kmh": current.get("wind_speed_10m"),
        "description": describe_weather_code(current.get("weather_code")),
        "measured_at": current.get("time"),
    }


def get_weather_forecast(latitude: float, longitude: float, days: int = 5) -> dict:
    """Devuelve el pronostico diario para unas coordenadas.

    Args:
        latitude: latitud en grados decimales (-90 a 90).
        longitude: longitud en grados decimales (-180 a 180).
        days: numero de dias de pronostico (1 a 7).

    Returns:
        Diccionario con la lista de dias, temperaturas maxima y minima,
        probabilidad de precipitacion y descripcion.
    """
    _validar_coordenadas(latitude, longitude)
    if not 1 <= days <= 7:
        raise ValueError(f"days debe estar entre 1 y 7; recibido {days}")

    daily = fetch_forecast(latitude, longitude, days)
    forecast = [
        {
            "date": daily["time"][i],
            "temp_max_c": daily["temperature_2m_max"][i],
            "temp_min_c": daily["temperature_2m_min"][i],
            "precipitation_probability_pct": daily["precipitation_probability_max"][i],
            "description": describe_weather_code(daily["weather_code"][i]),
        }
        for i in range(len(daily.get("time", [])))
    ]
    logger.info("Pronostico de %d dias obtenido para (%s, %s)", len(forecast), latitude, longitude)
    return {"days": forecast}
