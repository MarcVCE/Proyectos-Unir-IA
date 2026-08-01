#!/usr/bin/env bash
# Crea (si hace falta) el plan y la Web App de Azure y despliega la imagen del ACR.
# Requiere: az login previo y la imagen subida con ./push-to-acr.sh
set -euo pipefail

# ── Variables reutilizables ────────────────────────────────────────────────
VERSION="${VERSION:-1.0.0}"
IMAGE_NAME="${IMAGE_NAME:-fastapi-app}"
ACR_NAME="${ACR_NAME:-acrfastapiseo2026}"
RESOURCE_GROUP="${RESOURCE_GROUP:-rg-fastapi-deploy}"
LOCATION="${LOCATION:-westeurope}"
PLAN_NAME="${PLAN_NAME:-plan-fastapi-deploy}"
# El nombre de la Web App debe ser globalmente unico (forma parte de la URL).
WEBAPP_NAME="${WEBAPP_NAME:-webapp-fastapi-seo-2026}"

ACR_SERVER="${ACR_NAME}.azurecr.io"
IMAGE_FULL="${ACR_SERVER}/${IMAGE_NAME}:${VERSION}"

echo "==> Comprobando resource group ${RESOURCE_GROUP}..."
az group create --name "${RESOURCE_GROUP}" --location "${LOCATION}" --output none

if ! az appservice plan show --name "${PLAN_NAME}" --resource-group "${RESOURCE_GROUP}" --output none 2>/dev/null; then
  echo "==> Creando App Service Plan ${PLAN_NAME} (Linux, tier B1)..."
  az appservice plan create \
    --name "${PLAN_NAME}" \
    --resource-group "${RESOURCE_GROUP}" \
    --is-linux \
    --sku B1 \
    --output none
else
  echo "==> El plan ${PLAN_NAME} ya existe."
fi

echo "==> Obteniendo credenciales de admin del ACR..."
ACR_USER=$(az acr credential show --name "${ACR_NAME}" --query username --output tsv)
ACR_PASS=$(az acr credential show --name "${ACR_NAME}" --query 'passwords[0].value' --output tsv)

if ! az webapp show --name "${WEBAPP_NAME}" --resource-group "${RESOURCE_GROUP}" --output none 2>/dev/null; then
  echo "==> Creando Web App ${WEBAPP_NAME} con la imagen ${IMAGE_FULL}..."
  az webapp create \
    --name "${WEBAPP_NAME}" \
    --resource-group "${RESOURCE_GROUP}" \
    --plan "${PLAN_NAME}" \
    --container-image-name "${IMAGE_FULL}" \
    --container-registry-url "https://${ACR_SERVER}" \
    --container-registry-user "${ACR_USER}" \
    --container-registry-password "${ACR_PASS}" \
    --output none
else
  echo "==> La Web App ya existe; actualizando la imagen del contenedor..."
  az webapp config container set \
    --name "${WEBAPP_NAME}" \
    --resource-group "${RESOURCE_GROUP}" \
    --container-image-name "${IMAGE_FULL}" \
    --container-registry-url "https://${ACR_SERVER}" \
    --container-registry-user "${ACR_USER}" \
    --container-registry-password "${ACR_PASS}" \
    --output none
fi

echo "==> Configurando el puerto 8000 (WEBSITES_PORT)..."
az webapp config appsettings set \
  --name "${WEBAPP_NAME}" \
  --resource-group "${RESOURCE_GROUP}" \
  --settings WEBSITES_PORT=8000 \
  --output none

echo "==> Habilitando CORS para cualquier origen..."
az webapp cors add \
  --name "${WEBAPP_NAME}" \
  --resource-group "${RESOURCE_GROUP}" \
  --allowed-origins '*' \
  --output none

echo "==> Reiniciando la Web App para aplicar la configuracion..."
az webapp restart --name "${WEBAPP_NAME}" --resource-group "${RESOURCE_GROUP}" --output none

echo ""
echo "==> Despliegue completado. URL de la aplicacion:"
echo "    https://${WEBAPP_NAME}.azurewebsites.net"
echo "    (puede tardar 1-2 minutos en arrancar el contenedor la primera vez)"
