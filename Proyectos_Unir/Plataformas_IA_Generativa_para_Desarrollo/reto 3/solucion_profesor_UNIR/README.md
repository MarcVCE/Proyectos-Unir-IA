# Generador de posts de LinkedIn con salidas estructuradas (solucion)

Solucion de referencia del reto: chatbot de terminal que genera posts de LinkedIn
usando la API de OpenAI con Structured Outputs (`responses.parse()`) y un modelo
Pydantic (`LinkedinPost`) con validacion estricta.

## Estructura

```
├── main.py                  # Bucle principal por terminal
├── models/
│   └── linkedin_post.py     # Modelo Pydantic LinkedinPost (validacion estricta)
├── core/
│   ├── api_client.py        # responses.parse() con text_format y manejo de refusals
│   └── chatbot.py           # Entrada de usuario, errores y visualizacion
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
```

3. Ejecuta la aplicacion:

```bash
python main.py
```

## Puntos clave de la solucion

- `LinkedinPost` define `title`, `content`, `hashtags` y `category` con
  `extra="forbid"`: la respuesta debe cumplir exactamente el esquema.
- `responses.parse()` con `text_format=LinkedinPost` delega en la API la
  generacion estructurada y el SDK devuelve directamente el objeto Pydantic
  en `response.output_parsed`.
- Manejo de errores separado por tipo: rechazos del modelo (refusal), errores
  de validacion de Pydantic, problemas de conexion, limites de tokens y errores
  genericos de API, siempre con mensajes claros para el usuario.
