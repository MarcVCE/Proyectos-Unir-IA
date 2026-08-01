#!/usr/bin/env bash
# Script de push de la imagen a Azure Container Registry (ACR).
set -euo pipefail

# ── Variables reutilizables ────────────────────────────────────────────────
VERSION="${VERSION:-1.0.0}"
IMAGE_NAME="${IMAGE_NAME:-fastapi-app}"
ACR_NAME="${ACR_NAME:-tunombreunico}"        # ⚠️ globalmente unico, solo minusculas/numeros
RESOURCE_GROUP="${RESOURCE_GROUP:-rg-fastapi-deploy}"
LOCATION="${LOCATION:-westeurope}"
ACR_SKU="${ACR_SKU:-Basic}"                   # Basic | Standard | Premium

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  cat <<'AYUDA'
Uso: ./push-to-acr.sh [ACR_NAME] [RESOURCE_GROUP] [LOCATION]
Crea el ACR si no existe, hace login y sube la imagen (version + latest).
Variables de entorno: VERSION IMAGE_NAME ACR_NAME RESOURCE_GROUP LOCATION ACR_SKU
Ejemplo:  ACR_NAME=miacr123 ./push-to-acr.sh
AYUDA
  exit 0
fi

# Argumentos posicionales opcionales (ademas de variables de entorno):
#   ./push-to-acr.sh [ACR_NAME] [RESOURCE_GROUP] [LOCATION]
ACR_NAME="${1:-$ACR_NAME}"
RESOURCE_GROUP="${2:-$RESOURCE_GROUP}"
LOCATION="${3:-$LOCATION}"

# Comprobacion de sesion de Azure
if ! az account show >/dev/null 2>&1; then
  echo "❌ No has iniciado sesion en Azure. Ejecuta:  az login"
  exit 1
fi

if [ "${ACR_NAME}" = "tunombreunico" ]; then
  echo "❌ Edita ACR_NAME (o exportalo): debe ser un nombre globalmente unico."
  exit 1
fi

# Comprobacion previa: las imagenes locales deben existir (build previo)
for tag in "${VERSION}" "latest"; do
  if ! docker image inspect "${IMAGE_NAME}:${tag}" >/dev/null 2>&1; then
    echo "❌ No existe la imagen local ${IMAGE_NAME}:${tag}. Ejecuta primero ./build-image.sh"
    exit 1
  fi
done

echo "════════════════════════════════════════════════════"
echo "📦 Push a Azure Container Registry"
echo "   ACR:      ${ACR_NAME}  (grupo ${RESOURCE_GROUP}, ${LOCATION})"
echo "   Imagen:   ${IMAGE_NAME}:${VERSION} y :latest"
echo "════════════════════════════════════════════════════"

# 1) Resource group (az group create es idempotente)
echo "→ Asegurando resource group '${RESOURCE_GROUP}'..."
az group create --name "${RESOURCE_GROUP}" --location "${LOCATION}" --output none

# 2) Crear el ACR solo si no existe
if az acr show --name "${ACR_NAME}" --resource-group "${RESOURCE_GROUP}" --output none 2>/dev/null; then
  echo "→ El ACR '${ACR_NAME}' ya existe; se reutiliza."
else
  echo "→ Creando ACR '${ACR_NAME}' (SKU ${ACR_SKU}, admin habilitado)..."
  az acr create \
    --name "${ACR_NAME}" \
    --resource-group "${RESOURCE_GROUP}" \
    --sku "${ACR_SKU}" \
    --admin-enabled true \
    --output none
fi

# 3) Login en el registro
echo "→ Login en ACR..."
az acr login --name "${ACR_NAME}"

# 4) Re-etiquetar la imagen local para el registro
LOGIN_SERVER=$(az acr show --name "${ACR_NAME}" --query loginServer --output tsv)
echo "→ Re-etiquetando para ${LOGIN_SERVER}..."
docker tag "${IMAGE_NAME}:${VERSION}" "${LOGIN_SERVER}/${IMAGE_NAME}:${VERSION}"
docker tag "${IMAGE_NAME}:latest"     "${LOGIN_SERVER}/${IMAGE_NAME}:latest"

# 5) Subir ambas tags
echo "→ Subiendo ${LOGIN_SERVER}/${IMAGE_NAME}:${VERSION} ..."
docker push "${LOGIN_SERVER}/${IMAGE_NAME}:${VERSION}"
echo "→ Subiendo ${LOGIN_SERVER}/${IMAGE_NAME}:latest ..."
docker push "${LOGIN_SERVER}/${IMAGE_NAME}:latest"

# 6) Verificacion: listar imagenes y tags en el ACR
echo ""
echo "✅ Imagenes en el registro '${ACR_NAME}':"
az acr repository list --name "${ACR_NAME}" --output table
echo ""
echo "✅ Tags de '${IMAGE_NAME}':"
az acr repository show-tags --name "${ACR_NAME}" --repository "${IMAGE_NAME}" --output table
echo ""
echo "🔗 Referencias completas de las imagenes subidas:"
echo "   ${LOGIN_SERVER}/${IMAGE_NAME}:${VERSION}"
echo "   ${LOGIN_SERVER}/${IMAGE_NAME}:latest"
