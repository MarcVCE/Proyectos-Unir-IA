# img2img.py -- Image-to-Image con diffusers (compatible con transformers 5.x)
# Requisito: pip install diffusers transformers accelerate pillow requests torch
#
# Uso basico:
#   python img2img.py
#
# Con argumentos:
#   python img2img.py --prompt "a cat wearing a wizard hat, fantasy art"
#   python img2img.py --image ruta/local/imagen.png --strength 0.6 --no-show
#   python img2img.py --seed 123 --width 768 --height 768 --output result.png
#   python img2img.py --model kandinsky-community/kandinsky-2-2-decoder
#
# Modelos recomendados para img2img:
#   - runwayml/stable-diffusion-v1-5          (por defecto, ligero)
#   - stabilityai/stable-diffusion-2-1        (mayor calidad, mas VRAM)
#   - kandinsky-community/kandinsky-2-2-decoder (estilo artistico, sin NSFW filter)

import argparse
import sys
import requests
import torch
from io import BytesIO
from PIL import Image

# Importacion directa del pipeline img2img -- evita el import de AutoPipeline
# que arrastra HunyuanDiT y falla con transformers 5.x por MT5Tokenizer
from diffusers import StableDiffusionImg2ImgPipeline
from diffusers.utils import make_image_grid

# -- Valores por defecto ----------------------------------------------------
# Cambia DEFAULT_MODEL a kandinsky-community/kandinsky-2-2-decoder
# si quieres alinearte con el modelo del enunciado del ejercicio
DEFAULT_MODEL     = "runwayml/stable-diffusion-v1-5"
DEFAULT_IMAGE_URL = (
    "https://huggingface.co/datasets/huggingface/documentation-images"
    "/resolve/main/diffusers/cat.png"
)
DEFAULT_PROMPT    = (
    "a cat in a fantasy forest, oil painting style, "
    "detailed fur, warm golden light, highly detailed"
)
DEFAULT_NEG       = (
    "blurry, low quality, watermark, ugly, deformed, "
    "flat colors, oversaturated, noisy"
)
DEFAULT_STRENGTH  = 0.75
DEFAULT_GUIDANCE  = 7.5
DEFAULT_STEPS     = 30
DEFAULT_SEED      = 42
DEFAULT_OUTPUT    = "img2img_output.png"

# -- Validacion de argumentos -----------------------------------------------
def validate_args(args: argparse.Namespace) -> None:
    """Valida rangos de strength y steps antes de ejecutar nada."""
    errors = []

    if not (0.0 <= args.strength <= 1.0):
        errors.append(
            f"  --strength {args.strength} fuera de rango. Debe estar en [0.0, 1.0]."
        )

    if args.steps <= 0:
        errors.append(
            f"  --steps {args.steps} no valido. Debe ser un entero positivo."
        )
    elif args.steps < 10:
        print(f"[WARN] --steps={args.steps} es muy bajo; la calidad puede verse afectada. "
              "Se recomienda un minimo de 10-20.")

    if args.guidance <= 0:
        errors.append(
            f"  --guidance {args.guidance} no valido. Debe ser un valor positivo."
        )

    if errors:
        print("[ERROR] Argumentos invalidos:")
        for msg in errors:
            print(msg)
        sys.exit(1)

# -- Sugerencia de multiplos de 64 ------------------------------------------
def nearest_multiple_of_64(value: int) -> int:
    """Devuelve el multiplo de 64 mas cercano a value."""
    return round(value / 64) * 64

def warn_if_not_multiple_of_64(width: int, height: int) -> None:
    """Avisa si las dimensiones no son multiplos de 64 y sugiere alternativas."""
    warnings = []
    if width % 64 != 0:
        suggested = nearest_multiple_of_64(width)
        warnings.append(f"  ancho {width}px -> sugerido: {suggested}px")
    if height % 64 != 0:
        suggested = nearest_multiple_of_64(height)
        warnings.append(f"  alto  {height}px -> sugerido: {suggested}px")

    if warnings:
        print("[WARN] Las dimensiones no son multiplos de 64. Algunos modelos de "
              "difusion pueden producir artefactos o errores:")
        for msg in warnings:
            print(msg)
        print("  Usa --width y --height con multiplos de 64 (ej: 512, 576, 640, 768).")

# -- Argumentos de linea de comandos ----------------------------------------
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Genera una variacion Image-to-Image con Stable Diffusion.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--model", type=str, default=DEFAULT_MODEL,
        help=(
            "Modelo HuggingFace compatible con img2img. Ejemplos: "
            "'runwayml/stable-diffusion-v1-5' (por defecto), "
            "'stabilityai/stable-diffusion-2-1', "
            "'kandinsky-community/kandinsky-2-2-decoder'"
        ),
    )
    parser.add_argument("--image", type=str, default=DEFAULT_IMAGE_URL,
                        help="URL o ruta local de la imagen base")
    parser.add_argument("--prompt", type=str, default=DEFAULT_PROMPT,
                        help="Prompt para guiar la variacion")
    parser.add_argument("--negative-prompt", type=str, default=DEFAULT_NEG,
                        dest="negative_prompt", help="Negative prompt")
    parser.add_argument(
        "--strength", type=float, default=DEFAULT_STRENGTH,
        help="Fuerza de la transformacion en rango [0.0, 1.0]. "
             "0.0 = identica a la original; 1.0 = ignorar imagen base.",
    )
    parser.add_argument("--guidance", type=float, default=DEFAULT_GUIDANCE,
                        help="Guidance scale (valor positivo)")
    parser.add_argument(
        "--steps", type=int, default=DEFAULT_STEPS,
        help="Pasos de inferencia (entero positivo; recomendado >= 20)",
    )
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED,
                        help="Seed para reproducibilidad")
    parser.add_argument(
        "--width", type=int, default=None,
        help="Ancho de salida en pixeles. Sin --height se mantiene proporcion. "
             "Recomendado: multiplo de 64 (512, 640, 768...).",
    )
    parser.add_argument(
        "--height", type=int, default=None,
        help="Alto de salida en pixeles. Sin --width se mantiene proporcion. "
             "Recomendado: multiplo de 64 (512, 640, 768...).",
    )
    parser.add_argument("--output", type=str, default=DEFAULT_OUTPUT,
                        help="Ruta del archivo de salida")
    parser.add_argument("--no-show", action="store_true", dest="no_show",
                        help="No abrir el visor grafico al terminar")
    return parser.parse_args()

# -- Carga y resize de imagen base ------------------------------------------
def load_image(source: str, width, height) -> Image.Image:
    """Carga una imagen desde una URL o ruta local, la convierte a RGB
    y aplica resize si se han especificado --width y/o --height.

    Modos de resize:
    - Solo --width  -> altura proporcional
    - Solo --height -> ancho proporcional
    - Ambos         -> resize exacto al tamano indicado

    Avisa si las dimensiones finales no son multiplos de 64.
    """
    if source.startswith("http://") or source.startswith("https://"):
        print(f"[INFO] Descargando imagen desde: {source}")
        try:
            response = requests.get(source, timeout=15)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content)).convert("RGB")
        except requests.RequestException as e:
            print(f"[ERROR] No se pudo descargar la imagen: {e}")
            sys.exit(1)
    else:
        print(f"[INFO] Cargando imagen local: {source}")
        try:
            image = Image.open(source).convert("RGB")
        except (FileNotFoundError, OSError) as e:
            print(f"[ERROR] No se pudo abrir la imagen: {e}")
            sys.exit(1)

    orig_w, orig_h = image.size
    print(f"[INFO] Imagen base cargada: {orig_w}x{orig_h} px")

    if width is not None or height is not None:
        if width is not None and height is None:
            height = round(orig_h * width / orig_w)
        elif height is not None and width is None:
            width = round(orig_w * height / orig_h)
        image = image.resize((width, height), Image.LANCZOS)
        print(f"[INFO] Imagen redimensionada a: {width}x{height} px")
        warn_if_not_multiple_of_64(width, height)
    else:
        # Avisar tambien si el tamano original no es multiplo de 64
        warn_if_not_multiple_of_64(orig_w, orig_h)

    return image

# -- Pipeline ---------------------------------------------------------------
def load_pipeline(model_id: str) -> StableDiffusionImg2ImgPipeline:
    """Carga el pipeline img2img detectando GPU/CPU automaticamente."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype  = torch.float16 if device == "cuda" else torch.float32
    print(f"[INFO] Dispositivo: {device} | dtype: {dtype}")

    try:
        pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
            model_id,
            torch_dtype=dtype,
            safety_checker=None,
            requires_safety_checker=False,
        ).to(device)
    except OSError as e:
        print(f"[ERROR] No se pudo cargar el modelo '{model_id}': {e}")
        print("  Comprueba tu conexion a internet o el nombre del modelo.")
        sys.exit(1)
    except RuntimeError as e:
        print(f"[ERROR] Fallo al mover el modelo al dispositivo: {e}")
        print("  Posible causa: VRAM insuficiente. Prueba con CPU.")
        sys.exit(1)

    return pipe

# -- Generacion img2img -----------------------------------------------------
def run_img2img(pipe, init_image, prompt, negative_prompt,
                strength, guidance, steps, seed):
    """Aplica la transformacion Image-to-Image sobre init_image."""
    generator = torch.Generator().manual_seed(seed)
    print(f"[INFO] Generando variacion (seed={seed}, strength={strength})...")

    try:
        result = pipe(
            prompt              = prompt,
            negative_prompt     = negative_prompt,
            image               = init_image,
            strength            = strength,
            guidance_scale      = guidance,
            num_inference_steps = steps,
            generator           = generator,
        )
    except RuntimeError as e:
        print(f"[ERROR] Fallo durante la generacion: {e}")
        print("  Revisa la VRAM disponible o reduce --steps.")
        sys.exit(1)

    return result.images[0]

# -- Main -------------------------------------------------------------------
def main():
    """Punto de entrada principal."""
    args = parse_args()

    # Validar rangos antes de cargar nada
    validate_args(args)

    print(f"[INFO] Modelo   : {args.model}")
    print(f"[INFO] Prompt   : {args.prompt[:80]}{'...' if len(args.prompt) > 80 else ''}")
    print(f"[INFO] Strength : {args.strength} | Steps: {args.steps} | Seed: {args.seed}")

    init_image   = load_image(args.image, args.width, args.height)
    pipe         = load_pipeline(args.model)
    output_image = run_img2img(
        pipe,
        init_image      = init_image,
        prompt          = args.prompt,
        negative_prompt = args.negative_prompt,
        strength        = args.strength,
        guidance        = args.guidance,
        steps           = args.steps,
        seed            = args.seed,
    )

    grid = make_image_grid([init_image, output_image], rows=1, cols=2)
    grid.save(args.output)
    print(f"[OK] Grid guardado en: {args.output}")

    if not args.no_show:
        grid.show()
    else:
        print("[INFO] Visor omitido (--no-show activo).")


if __name__ == "__main__":
    main()
