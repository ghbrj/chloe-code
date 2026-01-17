# -------------------------------------------------
# backend/Dockerfile – API FastAPI (Python 3.12)
# -------------------------------------------------
    FROM python:3.12-slim

    # ----------------------------------------------------------------------
    # 1️⃣  Install des outils de compilation et des headers Python
    # ----------------------------------------------------------------------
    #   - build-essential → gcc, g++, make, etc.
    #   - python3-dev   → headers nécessaires pour les extensions Cython/Cpp
    #   - libffi-dev, libssl-dev → requis par certaines wheels (pydantic, cryptography)
    # ----------------------------------------------------------------------
    RUN apt-get update && \
        DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
            build-essential \
            python3-dev \
            libffi-dev \
            libssl-dev \
            ca-certificates && \
        rm -rf /var/lib/apt/lists/*
    
    # ----------------------------------------------------------------------
    # 2️⃣  Copie du fichier requirements.txt et installation des dépendances Python
    # ----------------------------------------------------------------------
    WORKDIR /app
    COPY requirements.txt .
    #   --prefer-binary : essaye d’utiliser les wheels pré‑compilées quand elles existent
    #   --no-cache-dir  : évite de garder le cache pip dans l’image finale
    RUN pip install --upgrade pip && \
        pip install --no-cache-dir --prefer-binary -r requirements.txt
    
    # ----------------------------------------------------------------------
    # 3️⃣  Copie du code source de l’API
    # ----------------------------------------------------------------------
    COPY . .
    
    # ----------------------------------------------------------------------
    # 4️⃣  Exposition du port Uvicorn (FastAPI)
    # ----------------------------------------------------------------------
    EXPOSE 8000
    
    # ----------------------------------------------------------------------
    # 5️⃣  Commande de démarrage
    # ----------------------------------------------------------------------
    CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]