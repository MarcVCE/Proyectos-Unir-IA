# Servidor MCP + cliente OpenAI (solucion)

Solucion de referencia del reto: servidor MCP local (FastMCP) con 5 herramientas que
integran 2 APIs publicas reales (ExchangeRate-API y Open-Meteo) y un cliente que usa
la API Responses de OpenAI para conversar en lenguaje natural, ejecutando las
herramientas del servidor MCP cuando hace falta (incluidas llamadas secuenciales
geocodificacion -> clima).

## Estructura

```
├── server/
│   ├── mcp_server.py        # Servidor FastMCP con las 5 herramientas registradas
│   ├── currency_tools.py    # convert_currency y get_exchange_rates
│   ├── weather_tools.py     # get_current_weather y get_weather_forecast (por coordenadas)
│   ├── geocoding_tools.py   # geocode_city (ciudad -> coordenadas)
│   └── api_clients.py       # HTTP a las APIs externas + errores + codigos WMO
├── client/
│   ├── openai_client.py     # API Responses + function tools descubiertas por MCP
│   └── cli_interface.py     # CLI interactiva (/ayuda, /monedas, /salir)
├── config/
│   └── settings.py          # Variables de entorno y URLs
├── main_server.py           # Arranca el servidor MCP (localhost:8000)
├── main_client.py           # Arranca el cliente CLI
└── requirements.txt
```

## Puesta en marcha

1. Crea y activa un entorno virtual e instala dependencias:

```bash
python -m venv .venv
source .venv/bin/activate   # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. Crea un archivo `.env` en la raiz del proyecto (no lo subas a git):

```
OPENAI_API_KEY=tu_clave
# Opcional: API key de https://www.exchangerate-api.com/ (si no se define,
# se usa el endpoint abierto open.er-api.com del mismo proveedor, sin key)
API_KEY_EXCHANGE=
# Opcionales:
MCP_HOST=127.0.0.1
MCP_PORT=8000
OPENAI_MODEL=gpt-4o-mini
```

3. Arranca el servidor MCP en una terminal:

```bash
python main_server.py
```

4. Arranca el cliente en otra terminal:

```bash
python main_client.py
```

## Como funciona

- El servidor registra 5 herramientas MCP con parametros tipados, docstrings en
  español, validacion de entrada (codigos ISO 4217, rangos de coordenadas, dias
  de pronostico) y manejo de errores de red/API con mensajes claros.
- El cliente descubre las herramientas por el protocolo MCP (`list_tools`) y se
  las pasa a la API Responses de OpenAI como function tools. Cuando el modelo
  pide una llamada, el cliente la ejecuta contra el servidor MCP
  (`call_tool`) y devuelve el resultado al modelo, en bucle, hasta obtener la
  respuesta final. Asi "Que tiempo hace en Madrid?" encadena automaticamente
  geocode_city("Madrid") y despues get_current_weather(lat, lon).
- Incluye reintentos ante fallos transitorios de la API de OpenAI y timeout por
  herramienta.

## Consultas de ejemplo

- Convierte 100 USD a EUR
- Cual es el clima actual en Madrid?
- Dame el pronostico del tiempo para Nueva York
- Que coordenadas tiene Tokio?
