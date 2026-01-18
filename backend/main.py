# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import time

# ----- IMPORTS ABSOLUS -----
from schemas import (
    InferRequest, InferResponse,
    SearchRequest, SearchResponse,
    RunTestsRequest, RunTestsResult,
    UpdateModelResponse, HealthResponse,
)
from utils.preprocess import build_prompt
from utils.postprocess import postprocess_code
from utils.ollama_client import generate_code, OllamaError
from utils.chroma_client import search_kb, add_documents
from utils.sandbox_client import run_tests_in_sandbox, SandboxError
from logger_util import log_request, log_response, log_error

# ---------------------------

app = FastAPI(title="chloe‑code API", version="0.1.0")

# -------------------------------------------------
# Health‑check
# -------------------------------------------------
@app.get("/healthz", response_model=HealthResponse)
async def health_check():
    return HealthResponse()


# -------------------------------------------------
# 1️⃣  Génération de code
# -------------------------------------------------
@app.post("/v1/infer", response_model=InferResponse)
async def infer(req: InferRequest):
    start = time.time()
    log_request("infer", req.dict())
    try:
        prompt = build_prompt(req.prompt, req.file_path, req.language)
        raw = generate_code(prompt)                     # Ollama
        code, warning = postprocess_code(
            raw, req.language or "python", block_dangerous=False
        )
        latency = int((time.time() - start) * 1000)
        resp = InferResponse(
            code=code,
            explanation=None,
            latency_ms=latency,
            warning=warning,
        )
        log_response("infer", resp.dict(), latency)
        return resp
    except OllamaError as exc:
        log_error("infer", str(exc))
        raise HTTPException(status_code=502, detail=str(exc))


# -------------------------------------------------
# 2️⃣  Recherche KB
# -------------------------------------------------
@app.get("/v1/search", response_model=SearchResponse)
async def search(q: str, k: int = 5):
    start = time.time()
    log_request("search", {"q": q, "k": k})
    results = search_kb(q, k)
    resp = SearchResponse(results=results)
    latency = int((time.time() - start) * 1000)
    log_response("search", resp.dict(), latency)
    return resp


# -------------------------------------------------
# 3️⃣  Exécution de tests sandbox
# -------------------------------------------------
@app.post("/v1/run-tests", response_model=RunTestsResult)
async def run_tests(req: RunTestsRequest):
    start = time.time()
    log_request("run-tests", req.dict())
    try:
        status, log, duration = run_tests_in_sandbox(req.code, req.language)
        resp = RunTestsResult(
            status=status,
            log=log,
            duration_ms=duration,
        )
        latency = int((time.time() - start) * 1000)
        log_response("run-tests", resp.dict(), latency)
        return resp
    except SandboxError as exc:
        log_error("run-tests", str(exc))
        raise HTTPException(status_code=500, detail=str(exc))


# -------------------------------------------------
# 4️⃣  Mise à jour du modèle (pull‑on‑demand)
# -------------------------------------------------
@app.post("/v1/update-model", response_model=UpdateModelResponse)
async def update_model():
    # Simple appel à Ollama via docker exec
    import subprocess, shlex
    try:
        subprocess.run(
            "docker exec chloe-code-ollama-1 ollama pull llama2-13b-chat-q4_0",
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return UpdateModelResponse(
            message="Model updated",
            model="llama2-13b-chat-q4_0",
            version=None,
        )
    except subprocess.CalledProcessError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Ollama pull failed: {exc.stderr.decode()}",
        )