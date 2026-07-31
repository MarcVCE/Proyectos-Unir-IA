# SEO Content API con FastAPI y OpenAI (solucion)

Solucion de referencia del reto: API REST con FastAPI que integra el SDK de OpenAI
para generar contenido SEO: keywords, articulos estructurados, metadatos, FAQs con
JSON-LD FAQPage y resumenes para redes sociales. Todas las respuestas de la IA usan
salidas estructuradas validadas con Pydantic.

## Estructura

```
seo-content-api/
├── app/
│   ├── main.py              # FastAPI app y routers
│   ├── config.py            # Cliente OpenAI o AzureOpenAI segun entorno
│   ├── models/              # Modelos Pydantic Request/Response por funcionalidad
│   ├── services/
│   │   └── seo_service.py   # Prompts + chat.completions.parse (salida estructurada)
│   └── routers/             # Un router por endpoint
└── requirements.txt
```

## Puesta en marcha

1. Crea y activa un entorno virtual e instala dependencias:

```bash
python -m venv .venv
source .venv/bin/activate   # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. Crea un archivo `.env` en la raiz del proyecto (no lo subas a git). Dos opciones:

```
# Opcion A: Azure OpenAI (Azure for students: usa gpt-4o o gpt-4o-mini)
AZURE_OPENAI_API_KEY=tu_clave
AZURE_OPENAI_ENDPOINT=https://tu-recurso.openai.azure.com/
OPENAI_API_VERSION=2024-10-21
OPENAI_MODEL=gpt-4o-mini

# Opcion B: OpenAI directo
OPENAI_API_KEY=tu_clave
OPENAI_MODEL=gpt-4o-mini
```

3. Arranca la API y abre la documentacion Swagger en http://127.0.0.1:8000/docs

```bash
uvicorn app.main:app --reload
```

## Endpoints

- `POST /api/keywords/generate`: keywords semilla, long-tail, preguntas e intencion.
- `POST /api/articles/generate`: articulo con H1/H2/H3, densidad y CTAs.
- `POST /api/metadata/generate`: 3-5 meta titles (max 60) y descriptions (max 160).
- `POST /api/faqs/extract`: FAQs del articulo + JSON-LD FAQPage (construido en el
  servidor a partir de las FAQs validadas, siempre JSON valido).
- `POST /api/social/summaries`: contenido adaptado a Twitter/X (max 280), LinkedIn,
  Instagram y Facebook segun las plataformas solicitadas.

## Puntos clave

- `services/seo_service.py` centraliza la llamada generica con
  `client.chat.completions.parse(response_format=<ModeloPydantic>)`: la respuesta
  llega ya validada contra el contrato del endpoint.
- Los limites duros (60/160 caracteres en metadatos, 280 en Twitter) se garantizan
  ademas con validadores Pydantic que truncan si la IA se excede.
- Manejo de errores: los fallos del SDK se devuelven como HTTP 502 con detalle.
