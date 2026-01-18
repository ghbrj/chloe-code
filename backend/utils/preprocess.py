# backend/utils/preprocess.py
import re
from pathlib import Path
from typing import Optional

def _clean_prompt(raw: str) -> str:
    """
    Nettoie le texte brut fourni par l'utilisateur.
    - Collapse les espaces multiples en un seul espace.
    - Supprime les sauts de ligne inutiles en début/fin.
    - Normalise les tabulations en 4 espaces.
    """
    # Remplace les tabulations par 4 espaces
    cleaned = raw.replace("\t", "    ")
    # Collapse les espaces multiples
    cleaned = re.sub(r"[ ]{2,}", " ", cleaned)
    # Supprime les sauts de ligne en tête et queue
    cleaned = cleaned.strip()
    return cleaned


def _extract_file_context(file_path: Optional[str]) -> dict:
    """
    Retourne un dictionnaire contenant des informations utiles sur le fichier actif.
    - `filename` : nom du fichier (ex. `script.py`)
    - `imports` : liste des imports détectés (simple regex, suffisant pour un prototype)
    """
    context = {"filename": None, "imports": []}
    if not file_path:
        return context

    path = Path(file_path)
    context["filename"] = path.name

    try:
        content = path.read_text(encoding="utf-8")
        # Recherche très simple d'import statements (Python, R, Julia, JS/TS)
        imports = re.findall(r"^\s*(?:import|using|require|library)\s+([^\s;]+)", content, flags=re.MULTILINE)
        context["imports"] = list(set(imports))
    except Exception:
        # Si le fichier n’est pas accessible, on ignore silencieusement
        pass

    return context


def build_prompt(user_prompt: str, file_path: Optional[str] = None, language: Optional[str] = None) -> str:
    """
    Construit le prompt final envoyé à Ollama.
    - Nettoie le prompt utilisateur.
    - Ajoute le contexte du fichier (si fourni).
    - Enveloppe le tout dans un template explicite.
    """
    cleaned = _clean_prompt(user_prompt)
    ctx = _extract_file_context(file_path)

    # Template de base – on indique le rôle du modèle et le langage cible
    template = (
        "You are a senior software engineer specialized in {lang}. "
        "Generate clean, well‑documented code that fulfills the user's request.\n\n"
    )

    # Remplace `{lang}` par le langage demandé ou par « general programming » si inconnu
    lang_token = language if language else "general programming"
    prompt_header = template.format(lang=lang_token)

    # Ajout du contexte du fichier (facultatif)
    if ctx["filename"]:
        prompt_header += f"The user is editing the file **{ctx['filename']}**.\n"
    if ctx["imports"]:
        imports_str = ", ".join(ctx["imports"])
        prompt_header += f"The current file imports: {imports_str}.\n"

    # Corps du prompt
    final_prompt = f"{prompt_header}\nUser request:\n{cleaned}"
    return final_prompt