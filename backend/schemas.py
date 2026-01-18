# backend/schemas.py
from __future__ import annotations
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


# ----------------------------------------------------------------------
# 1️⃣  Payloads pour la génération de code
# ----------------------------------------------------------------------
class InferRequest(BaseModel):
    """Requête provenant de l’extension VS Code."""
    prompt: str = Field(..., description="Instruction naturelle de l’utilisateur")
    file_path: Optional[str] = Field(
        None,
        description="Chemin du fichier actif (pour le contexte du prompt)"
    )
    language: Optional[Literal[
        "python", "r", "julia", "javascript", "typescript",
        "sql", "bash", "latex"
    ]] = Field(
        None,
        description="Langage cible (facultatif, aide le LLM à choisir le bon fence)"
    )


class InferResponse(BaseModel):
    """Réponse renvoyée à l’extension VS Code."""
    code: str = Field(..., description="Snippet de code généré")
    explanation: Optional[str] = Field(
        None,
        description="Courte explication du modèle (facultatif)"
    )
    latency_ms: int = Field(..., description="Temps d’inférence en millisecondes")
    warning: Optional[str] = Field(
        None,
        description="Avertissement éventuel (ex. tests échoués, code dangereux)"
    )


# ----------------------------------------------------------------------
# 2️⃣  Recherche dans la base de connaissances
# ----------------------------------------------------------------------
class SearchRequest(BaseModel):
    query: str = Field(..., description="Texte de la recherche")
    k: int = Field(5, ge=1, le=20, description="Nombre de résultats à retourner")

class SearchResult(BaseModel):
    title: str = Field(..., description="Titre du document/source")
    snippet: str = Field(..., description="Extrait pertinent")
    url: Optional[str] = Field(None, description="URL source (si disponible)")
    score: float = Field(..., description="Score de similarité (0‑1)")

class SearchResponse(BaseModel):
    results: List[SearchResult]


# ----------------------------------------------------------------------
# 3️⃣  Exécution de tests dans le sandbox
# ----------------------------------------------------------------------
class RunTestsRequest(BaseModel):
    code: str = Field(..., description="Snippet à tester")
    language: Literal[
        "python", "r", "julia", "javascript", "typescript",
        "sql", "bash", "latex"
    ] = Field(..., description="Langage du snippet")

class RunTestsResult(BaseModel):
    status: Literal["passed", "failed", "error"]
    log: str = Field(..., description="Stdout + stderr du sandbox")
    duration_ms: int = Field(..., description="Temps d’exécution du sandbox")


# ----------------------------------------------------------------------
# 4️⃣  Mise à jour du modèle LLM (pull‑on‑demand)
# ----------------------------------------------------------------------
class UpdateModelResponse(BaseModel):
    message: str = Field(..., description="Message de confirmation")
    model: str = Field(..., description="Nom du modèle mis à jour")
    version: Optional[str] = Field(
        None,
        description="Version du modèle (ex. tag Git ou date)"
    )


# ----------------------------------------------------------------------
# 5️⃣  Health‑check
# ----------------------------------------------------------------------
class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"