# Contract Risk Scoring Engine — FastAPI Backend

**Fresnel Fabian | MPS Applied Machine Intelligence | Northeastern Roux Institute**

---

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

Open **http://localhost:8080/docs** — interactive Swagger UI with all endpoints.

---

## Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/analyze` | Score a contract → risk scorecard |
| `GET` | `/health` | Liveness check |
| `GET` | `/clauses` | All 41 clause types with risk weights |
| `GET` | `/docs` | Swagger UI |
| `GET` | `/redoc` | ReDoc |

### POST /analyze

```bash
curl -X POST http://localhost:8080/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "This Agreement is between Vendor Inc. and Customer Corp..."}'
```

```json
{
  "score": 82,
  "triage": "URGENT REVIEW",
  "triage_description": "High-risk clauses detected. Requires immediate legal review.",
  "clauses": [
    {
      "clause": "Uncapped Liability",
      "text": "Vendor's liability shall not be limited under any circumstances.",
      "confidence": 0.882,
      "risk_weight": 10
    }
  ],
  "word_count": 847,
  "n_clauses_detected": 9,
  "model": "roberta-base fine-tuned on CUAD",
  "threshold": 0.1
}
```

Optional `threshold` field overrides the default per-request:
```json
{"text": "...", "threshold": 0.05}
```

---

## Model Loading

The API auto-detects which model to use at startup — no code changes needed.

**RoBERTa (primary):** Loaded when `models/roberta-finetuned/` exists and
`torch` + `transformers` are installed. Uses direct class imports
(`RobertaForQuestionAnswering`) — not `AutoModel` — to avoid the
`ernie_m` registry scan that breaks on Python 3.12.

**LR fallback (automatic):** Used when the model directory doesn't exist or
torch isn't installed. Trains on 510 synthetic contracts at startup (~5 s).
Returns confidence scores instead of extracted text spans.

### Connecting your Colab-trained model

1. Download `pytorch_model.bin` from Google Drive
2. Place it at `models/roberta-finetuned/pytorch_model.bin`
3. Create `models/roberta-finetuned/config.json`:
   ```json
   { "model_type": "roberta", "best_threshold": 0.10 }
   ```
4. `pip install torch transformers`
5. Restart the server — RoBERTa loads automatically

---

## Full Stack (backend + frontend)

```bash
# Terminal 1 — backend
uvicorn app.main:app --port 8080

# Terminal 2 — Next.js frontend (contract-risk-ui/)
USE_MOCK=false BACKEND_URL=http://localhost:8080 npm run dev
# Open http://localhost:3000
```

---

## Tests

```bash
pip install pytest pytest-asyncio httpx
pytest tests/ -v
```

15 tests covering health, clauses, analyze (happy path + edge cases).

---

## Project Structure

```
contract-risk-api/
├── app/
│   ├── main.py               ← App factory + lifespan
│   ├── core/
│   │   ├── config.py         ← All settings (pydantic-settings, reads .env)
│   │   └── logging.py        ← Structured stdout logging
│   ├── models/
│   │   └── schemas.py        ← Pydantic v2 request/response models
│   ├── routers/
│   │   ├── analyze.py        ← POST /analyze
│   │   └── health.py         ← GET /health, GET /clauses
│   └── services/
│       └── scorer.py         ← RobertaScorer + LRFallbackScorer + ScoringService
├── tests/
│   └── test_api.py           ← 15 pytest tests
├── models/
│   └── roberta-finetuned/    ← Drop pytorch_model.bin + config.json here
├── .env.example
├── requirements.txt
└── README.md
```
