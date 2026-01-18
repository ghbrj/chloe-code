# API – chloe‑code

## Health‑check
`GET /healthz` → `{ "status": "ok" }`

## Génération de code
`POST /v1/infer`
```json
{
  "prompt": "string",
  "file_path": "optional string",
  "language": "python|r|julia|javascript|typescript|sql|bash|latex"
}
```
Réponse:
```json
{
  "code": "string",
  "explanation": "optional string",
  "latency_ms": 123,
  "warning": "optional string"
}
```

## Recherche dans la KB
`GET /v1/search?q=<query>&k=<int>`
```json
{
  "results": [
    {
      "title": "string",
      "snippet": "string",
      "url": "optional string",
      "score": 0.97
    }
  ]
}
```

## Exécution de tests sandbox
`POST /v1/run-tests`
```json
{
  "code": "string",
  "language": "python|r|julia|javascript|typescript|sql|bash|latex"
}
```
Réponse :
```json
{
  "status": "passed|failed|error",
  "log": "string",
  "duration_ms": 456
}
```
## Mise à jour du modèle LLM
`POST /v1/update-model`
```json
{
  "message": "Model updated",
  "model": "llama2-13b-chat-q4_0",
  "version": null
}
```
Codes d’erreur HTTP
400 : payload invalide.
502 : problème d’appel à Ollama.
500 : erreur interne (sandbox, Chroma, etc.).
