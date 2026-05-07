# sd_image_grid_v4.py -- Stable Diffusion Image Grid
# Requisito: pip install diffusers transformers accelerate pillow torch
#
# Uso basico:
#   python sd_image_grid.py
#
# Con argumentos:
#   python sd_image_grid.py --prompt "a snowy mountain at dawn" --num 6 --cols 3 --batch
#   python sd_image_grid.py --prompt "portrait of a samurai" --seed 42 --width 768 --height 512
#   python sd_image_grid.py --no-show --output resultado.png
#   python sd_image_grid.py --seed 1234   # reproduce exactamente un grid anterior

import argparse
import math
import sys
import torch
from diffusers import StableDiffusionPipeline
from PIL import Image

# -- Valores por defecto ----------------------------------------------------
DEFAULT_MODEL    = "runwayml/stable-diffusion-v1-5"
DEFAULT_PROMPT   = (
    "a futuristic cityscape at sunset, neon lights reflecting on wet streets, "
    "cinematic, highly detailed, concept art, 4k"
)
DEFAULT_NEG      = (
    "blurry, low quality, watermark, text, signature, ugly, deformed, "
    "cartoon, anime, sketch, flat colors, oversaturated, noisy"
)
DEFAULT_NUM      = 4
DEFAULT_COLS     = 2
DEFAULT_OUTPUT   = "grid_output.png"
DEFAULT_STEPS    = 30
DEFAULT_GUIDANCE = 7.5
DEFAULT_SEED     = 42
DEFAULT_WIDTH    = 512
DEFAULT_HEIGHT   = 512
DEFAULT_GAP      = 8

# -- Argumentos de linea de comandos ----------------------------------------
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Genera un grid de imagenes con Stable Diffusion.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Modelo y prompts
    parser.add_argument("--model",           type=str,   default=DEFAULT_MODEL,
                        help="ID del modelo en HuggingFace")
    parser.add_argument("--prompt",          type=str,   default=DEFAULT_PROMPT,
                        help="Prompt de generacion")
    parser.add_argument("--negative-prompt", type=str,   default=DEFAULT_NEG,
                        dest="negative_prompt", help="Negative prompt")

    # Cantidad y layout
    parser.add_argument("--num",   type=int, default=DEFAULT_NUM,
                        help="Numero de imagenes a generar")
    parser.add_argument("--cols",  type=int, default=DEFAULT_COLS,
                        help="Columnas del grid")

    # Tamano de cada imagen
    parser.add_argument("--width",  type=int, default=DEFAULT_WIDTH,
                        help="Ancho de cada imagen generada en pixeles")
    parser.add_argument("--height", type=int, default=DEFAULT_HEIGHT,
                        help="Alto de cada imagen generada en pixeles")

    # Estetica del grid
    parser.add_argument("--gap", type=int, default=DEFAULT_GAP,
                        help="Separacion en pixeles entre imagenes del grid")

    # Parametros de inferencia
    parser.add_argument("--steps",    type=int,   default=DEFAULT_STEPS,
                        help="Pasos de inferencia")
    parser.add_argument("--guidance", type=float, default=DEFAULT_GUIDANCE,
                        help="Guidance scale")

    # Seed reproducible
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED,
                        help=(
                            "Seed base para la generacion. Las seeds de cada imagen "
                            "se derivan como seed + i*1000, permitiendo reproducir "
                            "exactamente un grid anterior con el mismo valor."
                        ))

    # Modo batch
    parser.add_argument("--batch", action="store_true",
                        help="Usar num_images_per_prompt en una sola llamada (mas rapido en GPU)")

    # Salida
    parser.add_argument("--output",   type=str, default=DEFAULT_OUTPUT,
                        help="Ruta del archivo de salida")
    parser.add_argument("--no-show",  action="store_true", dest="no_show",
                        help="No abrir el visor grafico al terminar (util en servidores sin GUI)")

    return parser.parse_args()

# -- Pipeline ---------------------------------------------------------------
def load_pipeline(model_id: str) -> StableDiffusionPipeline:
    """Carga el pipeline detectando GPU/CPU automaticamente."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype  = torch.float16 if device == "cuda" else torch.float32
    print(f"[INFO] Dispositivo: {device} | dtype: {dtype}")

    try:
        pipe = StableDiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=dtype,
            safety_checker=None,
            requires_safety_checker=False,
        ).to(device)
    except OSError as e:
        print(f"[ERROR] No se pudo cargar el modelo '{model_id}': {e}")
        print("  Comprueba tu conexion a internet o la ruta del modelo.")
        sys.exit(1)
    except RuntimeError as e:
        print(f"[ERROR] Fallo al mover el modelo al dispositivo: {e}")
        print("  Posible causa: VRAM insuficiente. Prueba con CPU o un modelo mas ligero.")
        sys.exit(1)

    return pipe

# -- Generacion: modo batch -------------------------------------------------
def generate_batch(
    pipe: StableDiffusionPipeline,
    prompt: str,
    negative_prompt: str,
    num_images: int,
    steps: int,
    guidance: float,
    width: int,
    height: int,
) -> list:
    """Genera todas las imagenes en una sola llamada (mas eficiente en GPU).
    Nota: en modo batch no se pueden fijar seeds individuales por imagen."""
    print(f"[INFO] Modo batch: {num_images} imagenes en una sola llamada...")
    try:
        result = pipe(
            prompt                = prompt,
            negative_prompt       = negative_prompt,
            num_images_per_prompt = num_images,
            num_inference_steps   = steps,
            guidance_scale        = guidance,
            width                 = width,
            height                = height,
        )
        return result.images
    except RuntimeError as e:
        print(f"[ERROR] Fallo en modo batch: {e}")
        print("  Prueba a reducir --num o elimina --batch.")
        sys.exit(1)

# -- Generacion: modo seeds individuales ------------------------------------
def generate_images(
    pipe: StableDiffusionPipeline,
    prompt: str,
    negative_prompt: str,
    num_images: int,
    steps: int,
    guidance: float,
    width: int,
    height: int,
    base_seed: int,
) -> list:
    """Genera imagenes con seeds derivadas de base_seed para variaciones reproducibles.

    La seed de cada imagen es: base_seed + i * 1000
    Para reproducir exactamente un grid anterior basta con pasar el mismo --seed.
    """
    images = []
    print(f"[INFO] Seed base: {base_seed} | Seeds: {[base_seed + i*1000 for i in range(num_images)]}")

    for i in range(num_images):
        seed      = base_seed + i * 1000
        generator = torch.Generator().manual_seed(seed)
        print(f"[INFO] Generando imagen {i+1}/{num_images} (seed={seed})...")
        try:
            result = pipe(
                prompt              = prompt,
                negative_prompt     = negative_prompt,
                num_inference_steps = steps,
                guidance_scale      = guidance,
                width               = width,
                height              = height,
                generator           = generator,
            )
            images.append(result.images[0])
        except RuntimeError as e:
            print(f"[WARN] Imagen {i+1} fallida (seed={seed}): {e}")
            print("  Se omite esta imagen y se continua.")

    if not images:
        print("[ERROR] No se genero ninguna imagen. Abortando.")
        sys.exit(1)
    return images

# -- Validacion de tamanos --------------------------------------------------
def validate_sizes(images: list) -> None:
    """Comprueba que todas las imagenes tienen el mismo tamano."""
    ref = images[0].size
    mismatches = [
        (i + 1, img.size)
        for i, img in enumerate(images[1:], start=1)
        if img.size != ref
    ]
    if mismatches:
        details = ", ".join(f"img {idx}: {size}" for idx, size in mismatches)
        print(f"[ERROR] Tamanos inconsistentes (referencia {ref}): {details}")
        print("  Todas las imagenes deben tener el mismo tamano para construir el grid.")
        sys.exit(1)
    print(f"[INFO] Tamano uniforme: {ref[0]}x{ref[1]} px")

# -- Grid -------------------------------------------------------------------
def make_grid(images: list, cols: int, gap: int) -> Image.Image:
    """Une las imagenes en un grid de `cols` columnas separadas por `gap` pixeles."""
    validate_sizes(images)
    rows   = math.ceil(len(images) / cols)
    w, h   = images[0].size
    grid_w = cols * w + (cols - 1) * gap
    grid_h = rows * h + (rows - 1) * gap
    grid   = Image.new("RGB", (grid_w, grid_h), (20, 20, 20))
    for idx, img in enumerate(images):
        col = idx % cols
        row = idx // cols
        grid.paste(img, (col * (w + gap), row * (h + gap)))
    return grid

# -- Main -------------------------------------------------------------------
def main() -> None:
    """Punto de entrada principal. Separado para facilitar pruebas e importacion."""
    args = parse_args()

    print(f"[INFO] Prompt      : {args.prompt[:80]}{'...' if len(args.prompt) > 80 else ''}")
    print(f"[INFO] Imagenes    : {args.num} | Cols: {args.cols} | Gap: {args.gap}px")
    print(f"[INFO] Tamano      : {args.width}x{args.height} px")
    print(f"[INFO] Modo        : {'batch' if args.batch else f'seeds (base={args.seed})'}")
    print(f"[INFO] Visor GUI   : {'no' if args.no_show else 'si'}")

    pipe = load_pipeline(args.model)

    if args.batch:
        images = generate_batch(
            pipe, args.prompt, args.negative_prompt,
            args.num, args.steps, args.guidance,
            args.width, args.height,
        )
    else:
        images = generate_images(
            pipe, args.prompt, args.negative_prompt,
            args.num, args.steps, args.guidance,
            args.width, args.height,
            args.seed,
        )

    grid = make_grid(images, args.cols, args.gap)
    grid.save(args.output)
    print(f"[OK] Grid guardado en: {args.output}")

    if not args.no_show:
        grid.show()
    else:
        print("[INFO] Visor omitido (--no-show activo).")


if __name__ == "__main__":
    main()
