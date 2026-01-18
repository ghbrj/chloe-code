# backend/logger_util.py
import os
from pathlib import Path
from loguru import logger

# ----------------------------------------------------------------------
# 1️⃣  Où placer les logs ?
# ----------------------------------------------------------------------
# LOG_ROOT peut être fourni via l’environnement (ex. Docker, CI, tests).
# Sinon on utilise le répertoire de travail courant (cwd) – qui est toujours
# accessible en écriture, que ce soit sur l’hôte ou dans le conteneur.
LOG_ROOT = Path(os.getenv("LOG_ROOT", os.getcwd()))
LOG_DIR = LOG_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# ----------------------------------------------------------------------
# 2️⃣  Configuration de Loguru
# ----------------------------------------------------------------------
logger.remove()  # désactive la configuration par défaut de Loguru

# On écrit les logs au format JSONL (un objet JSON par ligne)
logger.add(
    LOG_DIR / "app.log",
    rotation="30 days",          # rotation quotidienne, suppression après 30 jours
    retention="30 days",
    serialize=True,              # JSONL → chaque ligne est un JSON
    level="INFO",
)

# ----------------------------------------------------------------------
# 3️⃣  Fonctions utilitaires (appelées depuis main.py)
# ----------------------------------------------------------------------
def log_request(endpoint: str, payload: dict):
    """Log d’une requête entrante."""
    logger.info("request", endpoint=endpoint, payload=payload)


def log_response(endpoint: str, response: dict, latency_ms: int):
    """Log de la réponse renvoyée au client."""
    logger.info(
        "response",
        endpoint=endpoint,
        response=response,
        latency_ms=latency_ms,
    )


def log_error(endpoint: str, error: str):
    """Log d’une erreur interne."""
    logger.error("error", endpoint=endpoint, error=error)