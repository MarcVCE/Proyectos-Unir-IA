"""Logica principal del chatbot: entrada por terminal, llamada y visualizacion."""

from openai import APIConnectionError, APIError, LengthFinishReasonError
from pydantic import ValidationError

from core.api_client import OpenAIClient, RechazoAPIError
from models.linkedin_post import LinkedinPost


class Chatbot:
    """Chatbot de terminal que genera posts de LinkedIn estructurados."""

    def __init__(self, api_client: OpenAIClient | None = None) -> None:
        self.api_client = api_client or OpenAIClient()

    def pedir_idea(self) -> str:
        """Solicita al usuario la idea del post por terminal."""
        return input("\nDescribe la idea de tu post de LinkedIn (o 'salir'): ").strip()

    def procesar(self, idea: str) -> LinkedinPost | None:
        """Genera el post y gestiona los errores informando con claridad."""
        try:
            return self.api_client.generar_post(idea)
        except RechazoAPIError as error:
            print(f"\n[rechazo] El modelo no ha querido generar este contenido: {error}")
        except LengthFinishReasonError:
            print("\n[tokens] La respuesta se corto por limite de tokens. Simplifica la idea.")
        except ValidationError as error:
            print(f"\n[validacion] La respuesta no cumple el esquema LinkedinPost:\n{error}")
        except APIConnectionError:
            print("\n[conexion] No se pudo conectar con la API de OpenAI. Revisa tu red.")
        except APIError as error:
            print(f"\n[api] Error de la API de OpenAI: {error}")
        return None

    def mostrar(self, post: LinkedinPost) -> None:
        """Muestra los campos del post validado de forma organizada."""
        print("\n" + "=" * 60)
        print("POST GENERADO")
        print("=" * 60)
        print(f"Titulo    : {post.title}")
        print(f"Categoria : {post.category}")
        print("\nContenido:\n")
        print(post.content)
        print("\nHashtags  : " + " ".join(f"#{tag}" for tag in post.hashtags))
        print("=" * 60)
