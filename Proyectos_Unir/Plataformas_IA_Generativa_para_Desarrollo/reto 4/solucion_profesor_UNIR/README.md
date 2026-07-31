# Chatbot RAG con LangChain y OpenAI (solucion)

Solucion de referencia del reto: chatbot de terminal que responde preguntas sobre una
empresa ficticia (TechNova Solutions) usando RAG (Retrieval-Augmented Generation) con
LangChain, embeddings de OpenAI y un vector store en memoria.

## Estructura

```
├── main.py                  # CLI: indexa documentos y bucle de conversacion
├── documents/
│   ├── documento1.md        # Informacion general de la empresa (ficticia)
│   └── documento2.md        # Politicas internas y procedimientos (ficticios)
├── core/
│   ├── rag_system.py        # OpenAIEmbeddings + InMemoryVectorStore + retrieval
│   └── chatbot.py           # Flujo consulta -> retrieval -> generacion -> respuesta
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

3. Ejecuta el chatbot:

```bash
python main.py
```

## Como funciona

- `RAGSystem` carga los `.md` de `documents/`, los trocea con
  `RecursiveCharacterTextSplitter` (fragmentos de 800 caracteres con solape de 120),
  los vectoriza con `OpenAIEmbeddings` (modelo `text-embedding-3-small`) y los
  guarda en un `InMemoryVectorStore`.
- Para cada pregunta, `retrieve_context` busca por similitud los 4 fragmentos mas
  relevantes y se inyectan en el prompt del modelo (`gpt-4.1`) junto al historial.
- El prompt de sistema restringe las respuestas a la informacion de los documentos:
  si algo no aparece en el contexto, el chatbot lo dice en lugar de inventarlo.
- El historial se mantiene en memoria durante toda la sesion, de modo que puedes
  hacer preguntas de seguimiento que dependan de lo ya hablado.

## Preguntas de ejemplo

- Cuantos dias de vacaciones tengo y con cuanta antelacion se piden?
- Donde esta la sede de la empresa y cuando se fundo?
- Que hago si pierdo el portatil de empresa?
- Y si quiero teletrabajar desde otro pais de la UE?
