"""Cliente OpenAI conectado al servidor MCP local.

Flujo: descubre las herramientas del servidor MCP, se las presenta al modelo
como function tools de la API Responses y, cuando el modelo pide una llamada,
la ejecuta contra el servidor MCP y devuelve el resultado al modelo. Asi el
modelo puede encadenar llamadas secuenciales (p. ej. geocode_city y despues
get_current_weather) hasta poder responder al usuario.
"""

import asyncio
import json
import logging

from fastmcp import Client as MCPClient
from openai import APIConnectionError, APIStatusError, OpenAI

from config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "Eres un asistente financiero y meteorologico en español. Usa las "
    "herramientas disponibles para responder con datos reales y actuales. "
    "Para el clima de una ciudad, primero llama a geocode_city para obtener "
    "sus coordenadas y despues a get_current_weather o get_weather_forecast. "
    "Responde de forma clara y breve, indicando unidades."
)

MAX_TOOL_ROUNDS = 8
MAX_RETRIES = 3


class MCPOpenAIClient:
    """Orquesta la conversacion entre el usuario, OpenAI y el servidor MCP."""

    def __init__(self, mcp_url: str = settings.MCP_URL, model: str = settings.OPENAI_MODEL) -> None:
        self.model = model
        self.openai = OpenAI()
        self.mcp = MCPClient(mcp_url)
        self.tools: list[dict] = []
        self._history: list = [
            {"role": "developer", "content": SYSTEM_PROMPT},
        ]

    async def __aenter__(self) -> "MCPOpenAIClient":
        await self.mcp.__aenter__()
        await self._load_tools()
        return self

    async def __aexit__(self, *exc_info) -> None:
        await self.mcp.__aexit__(*exc_info)

    async def _load_tools(self) -> None:
        """Descubre las herramientas MCP y las convierte a function tools."""
        mcp_tools = await self.mcp.list_tools()
        self.tools = [
            {
                "type": "function",
                "name": tool.name,
                "description": tool.description or tool.name,
                "parameters": tool.inputSchema,
            }
            for tool in mcp_tools
        ]
        logger.info("Herramientas MCP disponibles: %s", [t["name"] for t in self.tools])

    def tool_names(self) -> list[str]:
        return [tool["name"] for tool in self.tools]

    async def ask(self, user_text: str) -> str:
        """Ejecuta un turno completo: usuario -> modelo -> herramientas -> respuesta."""
        self._history.append({"role": "user", "content": user_text})

        for _ in range(MAX_TOOL_ROUNDS):
            response = self._create_with_retries()
            # Añadimos al historial los items de salida del modelo (incluye
            # las peticiones de function_call con su call_id).
            self._history.extend(item.model_dump(exclude_none=True) for item in response.output)

            calls = [item for item in response.output if item.type == "function_call"]
            if not calls:
                return response.output_text

            for call in calls:
                result_text = await self._run_mcp_tool(call.name, call.arguments)
                print(f"  [herramienta] {call.name}({call.arguments}) ejecutada")
                self._history.append(
                    {
                        "type": "function_call_output",
                        "call_id": call.call_id,
                        "output": result_text,
                    }
                )

        return "No he podido completar la consulta en un numero razonable de pasos."

    def _create_with_retries(self):
        """Llama a la API Responses con reintentos ante fallos transitorios."""
        last_error: Exception | None = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                return self.openai.responses.create(
                    model=self.model,
                    input=self._history,
                    tools=self.tools,
                )
            except (APIConnectionError, APIStatusError) as error:
                retryable = isinstance(error, APIConnectionError) or error.status_code in (429, 500, 502, 503)
                last_error = error
                if not retryable or attempt == MAX_RETRIES:
                    raise
                wait = attempt * 2
                logger.warning("Fallo transitorio de OpenAI (%s); reintento en %ss", error, wait)
                import time

                time.sleep(wait)
        raise last_error  # inalcanzable, por claridad

    async def _run_mcp_tool(self, name: str, arguments: str) -> str:
        """Ejecuta una herramienta en el servidor MCP y devuelve el resultado como texto."""
        try:
            args = json.loads(arguments or "{}")
        except json.JSONDecodeError:
            return f"Error: argumentos no validos para {name}: {arguments!r}"

        try:
            result = await asyncio.wait_for(self.mcp.call_tool(name, args), timeout=30)
        except asyncio.TimeoutError:
            return f"Error: la herramienta {name} tardo demasiado en responder"
        except Exception as error:  # noqa: BLE001 - el modelo decide como continuar
            return f"Error ejecutando {name}: {error}"

        parts = [block.text for block in result.content if getattr(block, "text", None)]
        return "\n".join(parts) if parts else "(sin contenido)"
