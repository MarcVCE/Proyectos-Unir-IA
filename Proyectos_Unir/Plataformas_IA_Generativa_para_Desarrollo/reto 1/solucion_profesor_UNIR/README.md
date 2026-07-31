# Chatbot multiproveedor con fallback automatico

Solucion de referencia del reto: chatbot de terminal en Python con cascada de proveedores
OpenAI -> Anthropic Claude -> Google Gemini, historial completo de conversacion y respuesta
preconfigurada si los tres proveedores fallan.

## Estructura

```
├── main.py                    # CLI interactiva (bucle de conversacion, /salir)
├── providers/
│   ├── openai_provider.py     # API Responses de OpenAI en streaming
│   ├── anthropic_provider.py  # API Messages de Anthropic en streaming
│   └── gemini_provider.py     # google-genai en streaming
├── core/
│   ├── chatbot.py             # Cascada de fallback y notificaciones al usuario
│   └── conversation.py        # Historial de mensajes en memoria
└── requirements.txt
```

## Puesta en marcha

1. Crea y activa un entorno virtual e instala dependencias:

```bash
python -m venv .venv
source .venv/bin/activate   # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. Crea un archivo `.env` en la raiz del proyecto con tus claves (no lo subas a git):

```
OPENAI_API_KEY=tu_clave
ANTHROPIC_API_KEY=tu_clave
GOOGLE_API_KEY=tu_clave
```

No hace falta tener las tres: si una falta o falla, el chatbot hace fallback automatico
al siguiente proveedor y te avisa por consola.

3. Ejecuta el chatbot:

```bash
python main.py
```

## Como funciona el fallback

`core/chatbot.py` recorre los proveedores en orden de prioridad. Cada proveedor recibe el
historial completo (gestionado por `core/conversation.py`), por lo que la conversacion
mantiene el contexto aunque cambie el proveedor a mitad de dialogo. Si un proveedor lanza
cualquier excepcion (sin conectividad, limite de API, clave invalida), se avisa al usuario
y se prueba el siguiente. Si fallan los tres, responde una respuesta preconfigurada y la
conversacion continua.
