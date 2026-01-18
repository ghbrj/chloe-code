# backend/utils/ollama_client.py
import json
import httpx
from typing import Optional

# ----------------------------------------------------------------------
# Exceptions spécifiques
# ----------------------------------------------------------------------
class OllamaError(RuntimeError):
    """Exception levée lorsqu’une requête vers Ollama échoue."""
    pass


# ----------------------------------------------------------------------
# Fonction principale – generate_code
# ----------------------------------------------------------------------
def generate_code(
    prompt: str,
    *,
    model: str = "llama2:13b-chat-q4_0",
    max_tokens: int = 1024,
    temperature: float = 0.7,
    timeout: int = 30,
    endpoint: str = "http://ollama:11434/api/generate",
) -> str:
    """
    Envoie le prompt à Ollama et renvoie le texte généré.

    Parameters
    ----------
    prompt: str
        Prompt déjà pré‑processé (voir utils.preprocess.build_prompt).
    model: str, optional
        Nom du modèle installé dans Ollama (par défaut Llama‑2‑13B‑Chat quantifié 4‑bit).
    max_tokens: int, optional
        Nombre maximal de tokens à générer.
    temperature: float, optional
        Paramètre de température (diversité de la génération).
    timeout: int, optional
        Timeout en secondes pour la requête HTTP.
    endpoint: str, optional
        URL de l’API Ollama (dans le réseau Docker, le service s’appelle « ollama »).

    Returns
    -------
    str
        Le texte brut retourné par Ollama (généralement du code entouré de fences).

    Raises
    ------
    OllamaError
        Si la requête échoue, si le code HTTP n’est pas 200,
        ou si la réponse ne contient pas le champ attendu.
    """
    payload = {
        "model": model,
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": False,          # on veut la réponse complète en une fois
    }

    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.post(endpoint, json=payload)
    except httpx.RequestError as exc:
        raise OllamaError(f"Erreur réseau lors de l’appel à Ollama : {exc}") from exc

    if response.status_code != 200:
        raise OllamaError(
            f"Ollama a renvoyé le code HTTP {response.status_code}: {response.text}"
        )

    try:
        data = response.json()
    except json.JSONDecodeError as exc:
        raise OllamaError("Réponse Ollama non‑JSON") from exc

    # Ollama renvoie généralement un champ `response` contenant le texte généré.
    # Certaines versions renvoient `output` – on gère les deux.
    if "response" in data:
        return data["response"]
    if "output" in data:
        return data["output"]

    raise OllamaError("Champ de réponse manquant dans la réponse d’Ollama")