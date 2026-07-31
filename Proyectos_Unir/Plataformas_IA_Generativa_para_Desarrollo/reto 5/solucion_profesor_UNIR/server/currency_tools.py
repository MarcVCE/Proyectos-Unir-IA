"""Herramientas de conversion de monedas (ExchangeRate-API)."""

import logging

from server.api_clients import ApiClientError, fetch_exchange_rates

logger = logging.getLogger(__name__)

# Monedas mostradas por defecto al pedir las tasas de una moneda base.
MONEDAS_HABITUALES = ["EUR", "USD", "GBP", "JPY", "CHF", "MXN", "ARS", "COP", "BRL", "CNY"]


def _validar_codigo(codigo: str, campo: str) -> str:
    codigo = (codigo or "").strip().upper()
    if len(codigo) != 3 or not codigo.isalpha():
        raise ValueError(
            f"{campo} debe ser un codigo ISO 4217 de 3 letras (p. ej. USD, EUR); recibido: {codigo!r}"
        )
    return codigo


def convert_currency(amount: float, from_currency: str, to_currency: str) -> dict:
    """Convierte una cantidad entre dos divisas con la tasa de cambio actual.

    Args:
        amount: cantidad a convertir (mayor que 0).
        from_currency: codigo ISO 4217 de la moneda origen (p. ej. USD).
        to_currency: codigo ISO 4217 de la moneda destino (p. ej. EUR).

    Returns:
        Diccionario con la cantidad original, la tasa aplicada y el resultado.
    """
    if amount <= 0:
        raise ValueError("amount debe ser mayor que 0")
    origen = _validar_codigo(from_currency, "from_currency")
    destino = _validar_codigo(to_currency, "to_currency")

    rates = fetch_exchange_rates(origen)
    if destino not in rates:
        raise ApiClientError(f"La moneda destino {destino} no esta disponible en la API")

    rate = float(rates[destino])
    converted = round(amount * rate, 2)
    logger.info("Conversion %s %s -> %s %s (tasa %s)", amount, origen, converted, destino, rate)
    return {
        "amount": amount,
        "from_currency": origen,
        "to_currency": destino,
        "exchange_rate": rate,
        "converted_amount": converted,
    }


def get_exchange_rates(base_currency: str, currencies: list[str] | None = None) -> dict:
    """Devuelve las tasas de cambio actuales de una moneda base frente a otras.

    Args:
        base_currency: codigo ISO 4217 de la moneda base (p. ej. EUR).
        currencies: lista opcional de codigos a incluir; si se omite se
            devuelven las monedas mas habituales.

    Returns:
        Diccionario con la moneda base y las tasas solicitadas.
    """
    base = _validar_codigo(base_currency, "base_currency")
    rates = fetch_exchange_rates(base)

    solicitadas = [_validar_codigo(c, "currencies") for c in (currencies or MONEDAS_HABITUALES)]
    seleccion = {codigo: rates[codigo] for codigo in solicitadas if codigo in rates and codigo != base}
    if not seleccion:
        raise ApiClientError("Ninguna de las monedas solicitadas esta disponible en la API")

    return {"base_currency": base, "rates": seleccion}
