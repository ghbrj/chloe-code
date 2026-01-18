#!/usr/bin/env bash
# ==============================================================================
# install.sh – Installation automatisée de chloe‑code (macOS Apple Silicon)
# ==============================================================================
set -euo pipefail

# ---------- 0. Helpers --------------------------------------------------------
log()   { echo -e "\033[1;34m[install]\033[0m $*"; }
error() { echo -e "\033[1;31m[error]\033[0m $*" >&2; exit 1; }

# ---------- 1. Vérification des pré‑requis -----------------------------------
log "Vérification des pré‑requis système..."

# Homebrew
if ! command -v brew >/dev/null 2>&1; then
    error "Homebrew n’est pas installé. Visitez https://brew.sh et réessayez."
fi

# Python 3.12 (ou supérieur)
if ! command -v python3 >/dev/null 2>&1; then
    error "Python 3 n’est pas installé. Exécutez 'brew install python' puis relancez."
fi

PY_VER=$(python3 -c 'import sys; print(sys.version_info[:2])')
if [[ "$PY_VER" < "(3, 12)" ]]; then
    log "Python version < 3.12 détectée – mise à jour via Homebrew."
    brew upgrade python || true
fi

# npm
if ! command -v npm >/dev/null 2>&1; then
    error "npm n’est pas installé. Exécutez 'brew install node' puis relancez."
fi

# Docker + Docker‑Compose
if ! command -v docker >/dev/null 2>&1; then
    error "Docker n’est pas installé. Installez Docker Desktop pour macOS."
fi
if ! docker info >/dev/null 2>&1; then
    error "Docker daemon ne tourne pas. Lancez Docker Desktop."
fi
if ! docker compose version >/dev/null 2>&1; then
    log "Docker‑Compose non trouvé – il est inclus dans Docker Desktop 4.x."
fi

# ---------- 2. Installation d’Ollama -----------------------------------------
log "Installation d’Ollama (si absent)…"
if ! command -v ollama >/dev/null 2>&1; then
    brew install ollama
else
    log "Ollama déjà présent."
fi

# Démarrer le service Ollama (nécessaire avant le pull du modèle)
log "Démarrage du démon Ollama…"
if ! pgrep -x ollama >/dev/null 2>&1; then
    nohup ollama serve > /dev/null 2>&1 &
    sleep 2
fi

# ---------- 3. Environnement Python virtuel ----------------------------------
PYENV_DIR=".venv"
log "Création / activation de l’environnement virtuel Python ($PYENV_DIR)…"
if [[ ! -d "$PYENV_DIR" ]]; then
    python3 -m venv "$PYENV_DIR"
fi
# shellcheck disable=SC1091
source "$PYENV_DIR/bin/activate"

log "Installation des dépendances Python (FastAPI, loguru, etc.)…"
pip install --upgrade pip setuptools wheel
pip install -r backend/requirements.txt

# ---------- 4. Installation des dépendances Node (extension VS Code) ----------
log "Installation des dépendances Node pour l’extension VS Code…"
pushd extensions/vscode-chloe-code >/dev/null
npm ci
popd >/dev/null

# ---------- 5 Construction & lancement des services Docker --------------------
log "Construction des images Docker (API + Sandbox)…"
docker compose build

log "Lancement des services (api, ollama, chroma, sandbox)…"
docker compose up -d

# ---------- 6. Pull du modèle Llama‑2‑13B‑Chat (Q4_0) -------------------------
MODEL_NAME="llama2:13b-chat-q4_0"
log "Vérification du modèle $MODEL_NAME dans le conteneur Ollama …"

# Utiliser docker compose exec pour interroger le conteneur
if ! docker compose exec -T ollama ollama list | grep -q "$MODEL_NAME"; then
    log "Téléchargement du modèle $MODEL_NAME (cela peut prendre plusieurs minutes)…"
    # Le -T désactive l’allocation pseudo‑TTY (nécessaire dans les scripts)
    docker compose exec -T ollama ollama pull "$MODEL_NAME"
else
    log "Modèle $MODEL_NAME déjà présent dans le conteneur Ollama."
fi

# Attendre que l’API soit prête (poll /healthz)
log "Attente du health‑check de l’API (max 30 s)…"
for i in {1..30}; do
    if curl -s http://localhost:8000/healthz | grep -q '"status":"ok"'; then
        log "API prête."
        break
    fi
    sleep 1
done

# ---------- 7. Fin et instructions post‑install ------------------------------
log "✅ Installation terminée !"

cat <<EOF

=== Prochaines étapes =========================================================

1️⃣ Ouvrez VS Code dans le répertoire du projet :
   cd $(pwd)
   code .

2️⃣ Activez l’extension « chloe‑code » (elle devrait apparaître dans le
   Marketplace locale). Si elle n’apparaît pas, cliquez sur
   *Extensions → … → Reload Window*.

3️⃣ Test rapide :
   - Ouvrez la palette de commandes (⇧⌘P) → « Chloe‑code : Generate Code ».
   - Saisissez une requête simple, par ex. « Create a Python function that returns the factorial of n ».
   - Le code devrait apparaître dans l’éditeur après quelques secondes.

4️⃣ Vérifiez le health‑check si besoin :
   curl http://localhost:8000/healthz

5️⃣ Pour mettre à jour le modèle ultérieurement :
   - Ouvrez la palette de commandes → « Chloe‑code : Update Model ».

🛠️ En cas d’erreur, consultez les logs :
   - FastAPI : docker compose logs api
   - Ollama   : docker compose logs ollama
   - Sandbox  : docker compose logs sandbox

==========================================================================

EOF

# Désactivation du venv (facultatif, le script se termine ici)
deactivate