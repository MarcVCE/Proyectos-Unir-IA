#!/usr/bin/env bash
# Script de build y tag de la imagen Docker.
set -euo pipefail

# ── Variables reutilizables (versionamiento semantico) ────────────────────
# Sobrescribibles por entorno:  VERSION=1.1.0 ./build-image.sh
VERSION="${VERSION:-1.0.0}"
IMAGE_NAME="${IMAGE_NAME:-fastapi-app}"
DOCKERFILE="${DOCKERFILE:-Dockerfile}"        # ruta del Dockerfile a usar

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  cat <<'AYUDA'
Uso: ./build-image.sh
Construye la imagen Docker con doble tag (version + latest).
Variables de entorno:
  VERSION      version semantica (por defecto 1.0.0)
  IMAGE_NAME   nombre de la imagen (por defecto fastapi-app)
  DOCKERFILE   ruta del Dockerfile (por defecto Dockerfile)
Ejemplo:  VERSION=1.1.0 ./build-image.sh
AYUDA
  exit 0
fi

# Validar que VERSION tenga formato semantico X.Y.Z (evita tags accidentales)
if ! echo "${VERSION}" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+$'; then
  echo "❌ VERSION='${VERSION}' no es semantica (formato esperado X.Y.Z, p. ej. 1.0.0)."
  exit 1
fi

# Comprobacion previa de dependencias
if ! command -v docker >/dev/null 2>&1; then
  echo "❌ Docker no esta instalado o no esta en el PATH. Instala Docker Desktop y reabre la terminal."
  exit 1
fi
if ! docker info >/dev/null 2>&1; then
  echo "❌ El demonio de Docker no responde. Arranca Docker Desktop y espera a que este 'running'."
  exit 1
fi

echo "════════════════════════════════════════════════════"
echo "🔨 Build de la imagen Docker"
echo "   Imagen:  ${IMAGE_NAME}"
echo "   Version: ${VERSION} (+ latest)"
echo "════════════════════════════════════════════════════"

# Build con DOBLE tag en un solo paso: version especifica y latest
docker build -f "${DOCKERFILE}" -t "${IMAGE_NAME}:${VERSION}" -t "${IMAGE_NAME}:latest" .

echo ""
echo "✅ Build completado. Tags creadas:"
docker images "${IMAGE_NAME}" --format "   {{.Repository}}:{{.Tag}}  ({{.Size}})"

echo ""
echo "▶️  Prueba local:  docker run -p 8000:8000 ${IMAGE_NAME}:${VERSION}"
echo "    y abre http://localhost:8000 y http://localhost:8000/health"
