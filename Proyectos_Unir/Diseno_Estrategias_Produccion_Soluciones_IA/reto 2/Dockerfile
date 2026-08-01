# Imagen base oficial de Python, variante slim (ligera y sin sorpresas de compilacion).
# Alternativa aun mas ligera: python:3.12-alpine. No se usa por defecto porque con FastAPI/
# uvicorn suele requerir instalar toolchain de compilacion (apk add build-base musl-dev) para
# ruedas no precompiladas, lo que complica el build. 'slim' cumple el criterio (slim o alpine).
FROM python:3.12-slim

# Logs sin buffer: se ven en tiempo real en el "Log stream" de Azure
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# 1) Copiar SOLO requirements.txt e instalar dependencias.
#    Esta capa se cachea: los cambios de codigo no obligan a reinstalar dependencias.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2) Copiar SOLO el codigo necesario (no todo el contexto), para una imagen mas ligera.
COPY app.py .
# Si en el futuro la app crece a varios modulos, organiza el codigo en src/ y copia solo eso
# (mantiene la imagen pequena y una estructura mas escalable):
# COPY src/ ./src/

# Puerto en el que escucha la API
EXPOSE 8000

# Arranque: uvicorn escuchando en todas las interfaces del contenedor
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
