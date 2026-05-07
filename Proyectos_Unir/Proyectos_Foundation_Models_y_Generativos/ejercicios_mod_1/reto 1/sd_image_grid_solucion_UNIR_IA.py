import os
import torch
import warnings
from PIL import Image
from diffusers import StableDiffusionPipeline, EulerDiscreteScheduler

warnings.filterwarnings('ignore')  # Para evitar warnings innecesarios

###################################
# 1. Configuración de parámetros
###################################
MODEL_ID = "runwayml/stable-diffusion-v1-5"  # Puedes elegir otro modelo
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Carpeta de salida para guardar las imágenes
OUTPUT_DIR = "generated_outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Prompt principal y negativo
PROMPT = "A steampunk city with airships flying between tall buildings"
NEGATIVE_PROMPT = "cartoon, blurry, text, watermark"  # restringe estilos indeseados

# Número de imágenes y configuración de generación
NUM_IMAGES = 4
GUIDANCE_SCALE = 7.0
NUM_INFERENCE_STEPS = 50
IMAGE_HEIGHT = 512
IMAGE_WIDTH = 512

###################################
# 2. Creación de la pipeline
###################################
def create_pipeline(model_id=MODEL_ID):
    """
    Crea un pipeline de Stable Diffusion con un scheduler específico.
    Por defecto, utiliza EulerDiscreteScheduler.
    """
    scheduler = EulerDiscreteScheduler.from_pretrained(
        model_id,
        subfolder="scheduler",
    )

    pipeline = StableDiffusionPipeline.from_pretrained(
        model_id,
        scheduler=scheduler,
        torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32
    )
    pipeline = pipeline.to(DEVICE)
    return pipeline

###################################
# 3. Función para crear una cuadrícula
###################################
def image_grid(imgs, rows, cols):
    """
    Toma una lista de imágenes (PIL) y las acomoda en una cuadrícula (rows x cols).
    Devuelve una sola imagen (PIL) con la cuadrícula resultante.
    """
    assert len(imgs) == rows * cols
    w, h = imgs[0].size
    grid = Image.new('RGB', size=(cols * w, rows * h))
    for i, img in enumerate(imgs):
        grid.paste(img, box=((i % cols) * w, (i // cols) * h))
    return grid

###################################
# 4. Función para generar imágenes y mostrarlas en grid
###################################
def generate_images_grid(
    pipeline, 
    prompt, 
    negative_prompt, 
    num_images=4, 
    guidance_scale=7.5, 
    steps=50, 
    width=512, 
    height=512
):
    """
    Genera 'num_images' imágenes a partir de un 'prompt' y un 'negative_prompt',
    luego crea y devuelve una cuadrícula de dichas imágenes.
    """
    # Generamos las imágenes
    with torch.autocast(DEVICE):
        outputs = pipeline(
            prompt=prompt,
            negative_prompt=negative_prompt,
            guidance_scale=guidance_scale,
            num_inference_steps=steps,
            width=width,
            height=height,
            num_images_per_prompt=num_images
        )
    images = outputs.images
    
    # Creamos una cuadrícula (ej.: 2 filas x 2 columnas si num_images=4)
    # Ajusta rows y cols según prefieras
    rows = 2
    cols = 2
    if num_images == 1:
        rows, cols = 1, 1
    elif num_images == 2:
        rows, cols = 1, 2
    elif num_images == 3:
        rows, cols = 1, 3
    elif num_images == 4:
        rows, cols = 2, 2
    # Para más imágenes, calcula rows/cols en función de num_images
    # (por ejemplo, rows = int(num_images**0.5), cols = int(num_images**0.5), etc.)

    grid = image_grid(images, rows, cols)
    return grid, images

###################################
# 5. Ejecución del script principal
###################################
if __name__ == "__main__":
    # 5.1 Crear la pipeline
    pipe = create_pipeline(MODEL_ID)

    # 5.2 Generar la cuadrícula
    grid_image, all_images = generate_images_grid(
        pipeline=pipe,
        prompt=PROMPT,
        negative_prompt=NEGATIVE_PROMPT,
        num_images=NUM_IMAGES,
        guidance_scale=GUIDANCE_SCALE,
        steps=NUM_INFERENCE_STEPS,
        width=IMAGE_WIDTH,
        height=IMAGE_HEIGHT
    )

    # 5.3 Guardar y mostrar resultados
    # Guardamos la imagen de la cuadrícula
    grid_filename = os.path.join(OUTPUT_DIR, "grid_result.png")
    grid_image.save(grid_filename)
    print(f"Cuadrícula guardada en: {grid_filename}")
    
    # Guardar cada imagen individualmente (opcional)
    for i, img in enumerate(all_images):
        img_filename = os.path.join(OUTPUT_DIR, f"image_{i}.png")
        img.save(img_filename)
        print(f"Imagen individual {i} guardada en: {img_filename}")

    # Si ejecutas esto en un entorno interactivo (como Jupyter Notebook),
    # puedes usar 'display(grid_image)' para visualizar. En un script,
    # se mostrará la ruta de guardado.
    print("Proceso completado. ¡Imágenes generadas con éxito!")