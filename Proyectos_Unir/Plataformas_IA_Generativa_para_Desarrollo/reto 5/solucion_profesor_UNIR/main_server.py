"""Punto de entrada del servidor MCP local."""

from config import settings
from server.mcp_server import mcp


def main() -> None:
    print(f"Servidor MCP escuchando en {settings.MCP_URL}")
    print("Pulsa Ctrl+C para parar.")
    mcp.run(transport="http", host=settings.MCP_HOST, port=settings.MCP_PORT)


if __name__ == "__main__":
    main()
