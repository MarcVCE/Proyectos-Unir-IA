# Imagen base oficial de Python en variante slim (ligera)
FROM python:3.12-slim

WORKDIR /app

# Primero las dependencias: asi los cambios de codigo no invalidan esta capa
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Codigo de la aplicacion
COPY app.py .

# Puerto de la API
EXPOSE 8000

# Arranque con uvicorn escuchando en todas las interfaces del contenedor
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
