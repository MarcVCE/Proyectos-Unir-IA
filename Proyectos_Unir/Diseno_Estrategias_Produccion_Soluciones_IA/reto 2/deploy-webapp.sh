#!/usr/bin/env bash
# Script de despliegue de la Web App a partir de la imagen del ACR.
set -euo pipefail

# ── Variables reutilizables ────────────────────────────────────────────────
VERSION="${VERSION:-1.0.0}"
IMAGE_NAME="${IMAGE_NAME:-fastapi-app}"
ACR_NAME="${ACR_NAME:-tunombreunico}"
RESOURCE_GROUP="${RESOURCE_GROUP:-rg-fastapi-deploy}"
LOCATION="${LOCATION:-westeurope}"
PLAN_NAME="${PLAN_NAME:-plan-fastapi-deploy}"
PLAN_SKU="${PLAN_SKU:-B1}"                    # B1 (Basic) o F1 (Free)
WEBAPP_NAME="${WEBAPP_NAME:-tuwebappunica}"  # ⚠️ globalmente unico (forma parte de la URL)
HEALTH_PATH="${HEALTH_PATH:-/health}"        # ruta del endpoint de salud (parametrizable)

# Opciones de linea de comandos (ademas de variables de entorno):
#   ./deploy-webapp.sh --sku F1 --location westeurope
while [ $# -gt 0 ]; do
  case "$1" in
    --sku)       PLAN_SKU="$2"; shift 2 ;;
    --location)  LOCATION="$2"; shift 2 ;;
    -h|--help)
      echo "Uso: ./deploy-webapp.sh [--sku B1|F1] [--location <region>]"
      echo "Variables: VERSION IMAGE_NAME ACR_NAME RESOURCE_GROUP PLAN_NAME WEBAPP_NAME"
      exit 0 ;;
    *) echo "Opcion desconocida: $1"; exit 1 ;;
  esac
done

# Comprobacion de sesion de Azure
if ! az account show >/dev/null 2>&1; then
  echo "❌ No has iniciado sesion en Azure. Ejecuta:  az login"
  exit 1
fi

if [ "${ACR_NAME}" = "tunombreunico" ] || [ "${WEBAPP_NAME}" = "tuwebappunica" ]; then
  echo "❌ Edita ACR_NAME y WEBAPP_NAME (o exportalos): deben ser globalmente unicos."
  exit 1
fi

# Validar formato del nombre de la Web App (minusculas, numeros y guiones; 2-60 chars)
if ! echo "${WEBAPP_NAME}" | grep -Eq '^[a-z0-9][a-z0-9-]{1,59}$'; then
  echo "❌ WEBAPP_NAME='${WEBAPP_NAME}' no es valido: usa solo minusculas, numeros y guiones"
  echo "   (sin empezar por guion, 2-60 caracteres)."
  exit 1
fi

echo "════════════════════════════════════════════════════"
echo "🚀 Despliegue de Web App desde ACR"
echo "   Web App: ${WEBAPP_NAME}  (plan ${PLAN_NAME}, grupo ${RESOURCE_GROUP})"
echo "   Imagen:  ${ACR_NAME}.azurecr.io/${IMAGE_NAME}:${VERSION}"
echo "════════════════════════════════════════════════════"

# 1) Resource group (idempotente)
echo "→ Asegurando resource group '${RESOURCE_GROUP}'..."
az group create --name "${RESOURCE_GROUP}" --location "${LOCATION}" --output none

# 2) App Service Plan Linux (B1) solo si no existe
if az appservice plan show --name "${PLAN_NAME}" --resource-group "${RESOURCE_GROUP}" --output none 2>/dev/null; then
  echo "→ El plan '${PLAN_NAME}' ya existe; se reutiliza."
else
  echo "→ Creando App Service Plan Linux ${PLAN_SKU} '${PLAN_NAME}'..."
  az appservice plan create \
    --name "${PLAN_NAME}" \
    --resource-group "${RESOURCE_GROUP}" \
    --location "${LOCATION}" \
    --is-linux \
    --sku "${PLAN_SKU}" \
    --output none
fi

# 3) Datos y credenciales del ACR (admin habilitado en push-to-acr.sh)
LOGIN_SERVER=$(az acr show --name "${ACR_NAME}" --query loginServer --output tsv)

# Verificar que la version indicada existe en el ACR (evita desplegar una tag inexistente)
echo "→ Verificando que ${IMAGE_NAME}:${VERSION} existe en el ACR..."
if ! az acr repository show-tags --name "${ACR_NAME}" --repository "${IMAGE_NAME}" --output tsv 2>/dev/null | grep -qx "${VERSION}"; then
  echo "❌ La imagen ${IMAGE_NAME}:${VERSION} no esta en el ACR '${ACR_NAME}'. Ejecuta ./push-to-acr.sh primero."
  exit 1
fi

ACR_USER=$(az acr credential show --name "${ACR_NAME}" --query username --output tsv)
ACR_PASS=$(az acr credential show --name "${ACR_NAME}" --query "passwords[0].value" --output tsv)
IMAGEN_COMPLETA="${LOGIN_SERVER}/${IMAGE_NAME}:${VERSION}"

# 4) Crear la Web App basada en contenedor (o actualizar la imagen si ya existe)
if az webapp show --name "${WEBAPP_NAME}" --resource-group "${RESOURCE_GROUP}" --output none 2>/dev/null; then
  echo "→ La Web App ya existe; actualizando la imagen a ${IMAGEN_COMPLETA}..."
  az webapp config container set \
    --name "${WEBAPP_NAME}" \
    --resource-group "${RESOURCE_GROUP}" \
    --container-image-name "${IMAGEN_COMPLETA}" \
    --container-registry-url "https://${LOGIN_SERVER}" \
    --container-registry-user "${ACR_USER}" \
    --container-registry-password "${ACR_PASS}" \
    --output none
else
  echo "→ Creando Web App '${WEBAPP_NAME}' con la imagen del ACR..."
  az webapp create \
    --name "${WEBAPP_NAME}" \
    --resource-group "${RESOURCE_GROUP}" \
    --plan "${PLAN_NAME}" \
    --container-image-name "${IMAGEN_COMPLETA}" \
    --container-registry-url "https://${LOGIN_SERVER}" \
    --container-registry-user "${ACR_USER}" \
    --container-registry-password "${ACR_PASS}" \
    --output none
fi

# 5) Puerto del contenedor: la Web App enruta el trafico al 8000
echo "→ Configurando WEBSITES_PORT=8000..."
az webapp config appsettings set \
  --name "${WEBAPP_NAME}" \
  --resource-group "${RESOURCE_GROUP}" \
  --settings WEBSITES_PORT=8000 \
  --output none

# 6) CORS: permitir peticiones desde cualquier origen
echo "→ Habilitando CORS para cualquier origen..."
az webapp cors add \
  --name "${WEBAPP_NAME}" \
  --resource-group "${RESOURCE_GROUP}" \
  --allowed-origins "*" \
  --output none

# 7) Reiniciar para aplicar y mostrar la URL final
az webapp restart --name "${WEBAPP_NAME}" --resource-group "${RESOURCE_GROUP}" --output none

URL="https://${WEBAPP_NAME}.azurewebsites.net"
echo ""
echo "════════════════════════════════════════════════════"
echo "✅ Despliegue completado."
echo "   🌐 URL:    ${URL}"
echo "   ❤️  Salud: ${URL}${HEALTH_PATH}"
echo "════════════════════════════════════════════════════"

# Comprobacion de estado: sondear el endpoint de salud (el primer arranque tarda en descargar la imagen)
echo "→ Esperando a que la app responda en ${URL}${HEALTH_PATH} (hasta ~3 min)..."
for intento in $(seq 1 18); do
  codigo=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "${URL}${HEALTH_PATH}" || echo "000")
  if [ "${codigo}" = "200" ]; then
    echo "✅ La app responde correctamente (HTTP 200 en /health)."
    break
  fi
  echo "   intento ${intento}/18: HTTP ${codigo}; reintentando en 10 s..."
  sleep 10
done
if [ "${codigo}" != "200" ]; then
  echo "⚠️  Aun no responde 200. Es normal en el primer arranque; revisa el Log stream en Azure"
  echo "    o vuelve a probar ${URL}${HEALTH_PATH} en unos minutos."
fi
