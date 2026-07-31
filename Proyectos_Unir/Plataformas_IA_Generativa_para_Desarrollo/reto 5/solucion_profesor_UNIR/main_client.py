"""Punto de entrada del cliente con interfaz CLI interactiva."""

import asyncio

from client.cli_interface import run_cli


def main() -> None:
    asyncio.run(run_cli())


if __name__ == "__main__":
    main()
