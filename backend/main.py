# backend/main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import time

# Import des schémas que nous avons déjà définis (à créer dans l'étape suivante)
from .schemas import (
    InferRequest, InferResponse,
    SearchRequest, SearchResponse,
    RunTestsRequest, RunTestsResult,
    UpdateModelResponse, HealthResponse
)

# Import des utilitaires (à créer dans les étapes suivantes)
# from .utils.preprocess import preprocess_prompt
# from .utils.postprocess import postprocess_code
# from .utils.ollama_client import generate_code
# from .utils.chroma_client import search_kb, add_documents
# from .utils.sandbox_client import run_tests_in_sandbox

# Import du logger
# from .logging import logger

app = FastAPI(title="chloe‑code API", version="0.1.0")

# ----------------------------------------------------------------------
# 1️⃣  Health‑check
# ----------------------------------------------------------------------
@app.get("/healthz", response_model=HealthResponse)
async def health_check():
    return HealthResponse()


# ----------------------------------------------------------------------
# 2️⃣  Génération de code (POST /v1/infer)
# ----------------------------------------------------------------------
@app.post("/v1/infer", response_model=InferResponse)
async def infer(request: InferRequest):
    start = time.time()
    # 1. Pré‑processing du prompt
    # processed_prompt = preprocess_prompt(request.prompt, request.file_path, request.language)

    # 2. Appel à Ollama (LLM)
    # raw_output = await generate_code(processed_prompt)

    # 3. Post‑processing du code (strip fences, formatters, warnings)
    # code, warning = postprocess_code(raw_output)

    # 4. Log + métriques
    latency_ms = int((time.time() - start) * 1000)
    # logger.info("infer", prompt=request.prompt, latency_ms=latency_ms)

    # 5. Réponse (placeholder tant que les utils ne sont pas implémentés)
    return InferResponse(
        code="# Code généré (placeholder)\nprint('Hello, world!')",
        explanation="Placeholder – implémentation du LLM à venir.",
        latency_ms=latency_ms,
        warning=None
    )


# ----------------------------------------------------------------------
# 3️⃣  Recherche dans la base de connaissances (GET /v1/search)
# ----------------------------------------------------------------------
@app.get("/v1/search", response_model=SearchResponse)
async def search(q: str, k: int = 5):
    # results = await search_kb(q, k)
    # placeholder
    dummy = [{
        "title": "Doc example",
        "snippet": "def foo(): pass",
        "url": None,
        "score": 0.95
    } for _ in range(k)]
    return SearchResponse(results=dummy)


# ----------------------------------------------------------------------
# 4️⃣  Exécution de tests dans le sandbox (POST /v1/run-tests)
# ----------------------------------------------------------------------
@app.post("/v1/run-tests", response_model=RunTestsResult)
async def run_tests(payload: RunTestsRequest):
    # result = await run_tests_in_sandbox(payload.code, payload.language)
    # placeholder
    return RunTestsResult(
        status="passed",
        log="All tests passed (placeholder).",
        duration_ms=123
    )


# ----------------------------------------------------------------------
# 5️⃣  Mise à jour du modèle LLM (POST /v1/update-model)
# ----------------------------------------------------------------------
@app.post("/v1/update-model", response_model=UpdateModelResponse)
async def update_model():
    # Ici on invoque `docker exec` ou `ollama pull` depuis le conteneur
    # placeholder
    return UpdateModelResponse(
        message="Model update triggered (placeholder).",
        model="llama2-13b-chat-q4_0",
        version=None
    )