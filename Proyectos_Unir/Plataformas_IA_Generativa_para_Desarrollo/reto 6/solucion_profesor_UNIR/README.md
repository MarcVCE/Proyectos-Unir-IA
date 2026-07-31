# Agentes especializados con OpenAI Agents SDK (solucion)

Solucion de referencia del reto: chatbot de terminal que genera publicaciones de
LinkedIn delegando en agentes especializados (marketing, programacion y
juridico-legal) mediante handoffs del OpenAI Agents SDK, con salida estructurada
Pydantic (`LinkedinPost`: title, content, hashtags, category).

## Estructura

```
├── main.py                        # CLI: bucle de conversacion y /salir
├── post_agents/
│   ├── main_agent.py              # Agente principal (triage + handoffs)
│   └── specialized_agents.py      # 3 agentes especializados + modelo LinkedinPost
├── core/
│   ├── chatbot.py                 # Runner, indicador de agente activo y render del post
│   └── conversation.py            # Historial entre turnos (to_input_list)
└── requirements.txt
```

Nota sobre la carpeta `post_agents/`: el enunciado sugiere `agents/`, pero ese
nombre colisiona con el modulo `agents` del propio OpenAI Agents SDK (el import
`from agents import Agent` cargaria la carpeta local y el programa no arrancaria).
Por eso el paquete local se llama `post_agents/`, con los mismos ficheros.

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

- El **agente principal** analiza cada peticion y hace handoff automatico al
  especialista adecuado; si el tema no esta claro, pide concrecion al usuario.
- Cada **agente especializado** genera la publicacion con `output_type=LinkedinPost`,
  de modo que el SDK garantiza la estructura title/content/hashtags/category.
- La clase `Conversation` conserva el historial entre turnos con
  `result.to_input_list()`, asi que puedes pedir variaciones sobre el post anterior.
- Tras cada turno se muestra el **indicador del agente** que ha procesado la
  consulta (`result.last_agent.name`).

## Peticiones de ejemplo

- Quiero un post sobre las ventajas de las pruebas automatizadas en Python.
- Ahora uno sobre como lanzar una campaña de email marketing para una academia.
- Hazme un post sobre las claves del RGPD para una startup.
