#!/usr/bin/env bash
# Construye y etiqueta la imagen Docker en local.
# Uso: ./build-image.sh            (usa la VERSION definida abajo)
#      VERSION=1.1.0 ./build-image.sh   (cambia de version sin editar el script)
set -euo pipefail

# ── Variables reutilizables ────────────────────────────────────────────────
VERSION="${VERSION:-1.0.0}"     # versionamiento semantico: MAYOR.MENOR.PARCHE
IMAGE_NAME="${IMAGE_NAME:-fastapi-app}"

echo "==> Construyendo ${IMAGE_NAME}:${VERSION} (y tag latest)..."
docker build -t "${IMAGE_NAME}:${VERSION}" -t "${IMAGE_NAME}:latest" .

echo "==> Imagen construida y etiquetada:"
docker images "${IMAGE_NAME}"

echo "==> Listo. Prueba en local con:"
echo "    docker run -p 8000:8000 ${IMAGE_NAME}:${VERSION}"
