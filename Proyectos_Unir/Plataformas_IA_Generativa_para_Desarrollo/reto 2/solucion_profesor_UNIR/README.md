# Chatbot de expertos tematicos con Ollama (solucion)

Solucion de referencia del reto: chatbot de consola con tres expertos tematicos
(Programacion, Marketing y Juridico-Legal) sobre el modelo local `gemma3:1b` via
Ollama SDK, funcionando completamente offline.

## Estructura

```
├── main.py                   # Menu de expertos, bucle de conversacion y comandos
├── experts/
│   └── expert_prompts.py     # Prompts de sistema de cada experto
├── core/
│   ├── chatbot.py            # Conexion con Ollama SDK y manejo de errores
│   └── conversation.py       # Historial, contexto y experto activo
└── requirements.txt
```

## Requisitos previos

1. Tener instalado [Ollama](https://ollama.com) y el servicio arrancado
   (la aplicacion de escritorio o `ollama serve`).
2. Descargar el modelo local:

```bash
ollama pull gemma3:1b
```

## Puesta en marcha

```bash
python -m venv .venv
source .venv/bin/activate   # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Uso

- Al arrancar se comprueba que Ollama responde y que `gemma3:1b` esta descargado;
  si no, se muestra un mensaje claro con la solucion.
- Elige un experto en el menu (1 Programacion, 2 Marketing, 3 Juridico-Legal).
- Conversa con normalidad: el historial se conserva entre mensajes.
- Comandos durante la conversacion:
  - `/experto`: cambiar de experto manteniendo el contexto de lo hablado.
  - `/reiniciar`: borrar el dialogo conservando el experto activo.
  - `/salir`: terminar.
