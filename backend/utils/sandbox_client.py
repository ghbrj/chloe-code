# backend/utils/sandbox_client.py
import subprocess
import shlex
import time
from typing import Tuple

class SandboxError(RuntimeError):
    """Erreur lors de l’exécution dans le conteneur sandbox."""


def run_tests_in_sandbox(code: str, language: str) -> Tuple[str, str, int]:
    """
    Exécute `code` dans le conteneur `sandbox` via `docker exec`.

    Returns
    -------
    status : "passed" | "failed" | "error"
    log    : stdout+stderr du processus
    duration_ms : temps d’exécution
    """
    # Crée un fichier temporaire dans le répertoire partagé /workspace
    tmp_path = f"/workspace/tmp_{int(time.time()*1000)}.{_ext_for(language)}"
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(code)

    # Commande docker exec
    exec_cmd = (
        f"docker exec -i chloe-code-sandbox-1 "
        f"/bin/bash -c '{_run_cmd(language, tmp_path)}'"
    )
    start = time.time()
    try:
        proc = subprocess.run(
            exec_cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except subprocess.TimeoutExpired as exc:
        raise SandboxError("Timeout") from exc

    duration = int((time.time() - start) * 1000)
    log = proc.stdout + proc.stderr

    if proc.returncode == 0:
        status = "passed"
    elif proc.returncode > 0:
        status = "failed"
    else:
        status = "error"

    # Nettoyage du fichier temporaire
    subprocess.run(
        f"docker exec chloe-code-sandbox-1 rm -f {tmp_path}",
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return status, log, duration


def _ext_for(lang: str) -> str:
    return {
        "python": "py",
        "r": "R",
        "julia": "jl",
        "javascript": "js",
        "typescript": "ts",
        "bash": "sh",
        "sql": "sql",
        "latex": "tex",
    }.get(lang, "txt")


def _run_cmd(lang: str, path: str) -> str:
    """Commande à exécuter dans le sandbox selon le langage."""
    cmds = {
        "python": f"python3 {path}",
        "r": f"Rscript {path}",
        "julia": f"julia {path}",
        "javascript": f"node {path}",
        "typescript": f"ts-node {path}",
        "bash": f"bash {path}",
        "sql": f"psql -f {path}",
        "latex": f"pdflatex -interaction=nonstopmode -halt-on-error {path}",
    }
    return cmds.get(lang, f"cat {path}")