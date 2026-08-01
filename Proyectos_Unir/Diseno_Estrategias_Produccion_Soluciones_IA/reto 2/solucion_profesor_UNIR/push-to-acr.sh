#!/usr/bin/env bash
# Sube la imagen local a Azure Container Registry (ACR), creandolo si no existe.
# Requiere: az login previo y la imagen construida con ./build-image.sh
set -euo pipefail

# ── Variables reutilizables ────────────────────────────────────────────────
VERSION="${VERSION:-1.0.0}"
IMAGE_NAME="${IMAGE_NAME:-fastapi-app}"
# El nombre del ACR debe ser globalmente unico en Azure (solo minusculas y numeros).
ACR_NAME="${ACR_NAME:-acrfastapiseo2026}"
RESOURCE_GROUP="${RESOURCE_GROUP:-rg-fastapi-deploy}"
LOCATION="${LOCATION:-westeurope}"

ACR_SERVER="${ACR_NAME}.azurecr.io"

echo "==> Comprobando resource group ${RESOURCE_GROUP}..."
az group create --name "${RESOURCE_GROUP}" --location "${LOCATION}" --output none

if ! az acr show --name "${ACR_NAME}" --resource-group "${RESOURCE_GROUP}" --output none 2>/dev/null; then
  echo "==> Creando Azure Container Registry ${ACR_NAME} (sku Basic)..."
  az acr create \
    --name "${ACR_NAME}" \
    --resource-group "${RESOURCE_GROUP}" \
    --sku Basic \
    --admin-enabled true \
    --output none
else
  echo "==> El ACR ${ACR_NAME} ya existe."
fi

echo "==> Login en ${ACR_SERVER}..."
az acr login --name "${ACR_NAME}"

echo "==> Etiquetando la imagen local para el registro..."
docker tag "${IMAGE_NAME}:${VERSION}" "${ACR_SERVER}/${IMAGE_NAME}:${VERSION}"
docker tag "${IMAGE_NAME}:latest" "${ACR_SERVER}/${IMAGE_NAME}:latest"

echo "==> Subiendo ${ACR_SERVER}/${IMAGE_NAME}:${VERSION} y :latest..."
docker push "${ACR_SERVER}/${IMAGE_NAME}:${VERSION}"
docker push "${ACR_SERVER}/${IMAGE_NAME}:latest"

echo "==> Imagenes disponibles en el registro:"
az acr repository show-tags \
  --name "${ACR_NAME}" \
  --repository "${IMAGE_NAME}" \
  --output table
