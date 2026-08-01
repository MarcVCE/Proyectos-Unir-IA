# Despliegue de FastAPI en Azure con Docker y Azure CLI (solucion)

Solucion de referencia del reto: contenerizar una API FastAPI con Docker y
automatizar por scripts bash su publicacion en Azure Container Registry (ACR) y
su despliegue en una Azure Web App, sin usar el portal grafico.

## Estructura

```
azure-fastapi-deployment/
├── app.py               # API proporcionada (endpoints / y /health)
├── requirements.txt     # fastapi + uvicorn
├── Dockerfile           # python:3.12-slim, capas cacheables, puerto 8000
├── build-image.sh       # docker build + tags (version semantica y latest)
├── push-to-acr.sh       # crea el ACR si no existe, login, tag y push
└── deploy-webapp.sh     # resource group + plan B1 + Web App con la imagen del ACR
```

Nota sobre `.dockerignore` (opcional del enunciado): los ficheros que empiezan por
punto no viajan en este zip; si lo quieres, crea un `.dockerignore` con:

```
.venv
__pycache__
*.pyc
.git
```

## Uso

```bash
# 0. Requisitos: docker, az (Azure CLI) y sesion iniciada
az login
az account show

# 1. Construir la imagen en local (cambia la version sin editar el script)
chmod +x build-image.sh push-to-acr.sh deploy-webapp.sh
./build-image.sh                 # o VERSION=1.1.0 ./build-image.sh

# 2. Probar en local antes de desplegar
docker run -p 8000:8000 fastapi-app:1.0.0
curl http://localhost:8000/health

# 3. Subir la imagen a ACR (crea el registro si no existe)
ACR_NAME=tunombreunico ./push-to-acr.sh

# 4. Desplegar la Web App con la imagen del ACR
ACR_NAME=tunombreunico WEBAPP_NAME=tuwebappunica ./deploy-webapp.sh
```

Los tres scripts comparten variables reutilizables (VERSION, IMAGE_NAME, ACR_NAME,
RESOURCE_GROUP, LOCATION...) sobreescribibles por entorno, usan `set -euo pipefail`
como manejo basico de errores y muestran mensajes informativos en cada paso.

Recuerda que `ACR_NAME` y `WEBAPP_NAME` deben ser **globalmente unicos** en Azure:
cambia los valores por defecto por los tuyos. Con Azure for Students, el tier B1
del App Service Plan entra en el credito; puedes usar F1 (gratuito) cambiando
`--sku B1` por `--sku F1` si tu suscripcion lo permite.

Al terminar, `deploy-webapp.sh` imprime la URL publica
(`https://<WEBAPP_NAME>.azurewebsites.net`); comprueba `/` y `/health`.

Para no consumir credito cuando termines, elimina todo el resource group:

```bash
az group delete --name rg-fastapi-deploy --yes --no-wait
```
