# Contract Risk Scoring Engine

**Fresnel Fabian | MPS Applied Machine Intelligence | Northeastern Roux Institute | 2026**

AI-powered contract triage: fine-tuned `bert-base-uncased` on 510 real SEC EDGAR contracts (CUAD) to extract exact clause text for 41 high-risk clause types and output a 0–100 risk score with three-tier triage (AUTO-CLEAR / FLAG FOR REVIEW / URGENT REVIEW).

---

## Quick Start (5 minutes, no GPU)

```bash
# 1. Clone
git clone https://github.com/Fresnel-Fabian/contract-risk-scoring
cd contract-risk-scoring

# 2. Backend (LR fallback — no model weights needed)
cd contract-risk-api
pip install -r requirements.txt
uvicorn app.main:app --port 8080

# 3. Frontend (in a new terminal)
cd contract-risk-ui
npm install
npm run dev   # mock mode — no backend needed
# or: USE_MOCK=false BACKEND_URL=http://localhost:8080 npm run dev

# Open http://localhost:3000
# API docs: http://localhost:8080/docs
```

The backend auto-detects whether a trained model is available. Without `pytorch_model.bin` it falls back to LR+TF-IDF trained on synthetic data at startup (~5 s).

---

## Full Reproducibility

### Prerequisites

| Tool | Version | Install |
|---|---|---|
| Python | 3.12 | `conda install python=3.12` |
| Node.js | ≥ 18 | https://nodejs.org |
| conda | any | https://docs.conda.io |
| Google Colab | T4 GPU | https://colab.research.google.com |

### Step 1 — Environment

```bash
# Conda (recommended — handles CUDA-aware torch)
conda env create -f environment.yml
conda activate contract-risk

# Or pip-only (no CUDA torch)
pip install -r requirements-notebooks.txt
pip install -r contract-risk-api/requirements.txt
```

### Step 2 — Data

Place `data.zip` (provided via course) in the project root and unzip:

```bash
unzip data.zip -d data/raw/
# Creates:
#   data/raw/train_separate_questions.json  (408 contracts, 22,450 QA pairs)
#   data/raw/test.json                      (102 contracts, 4,182 QA pairs)
#   data/raw/CUADv1.json                    (full CUAD corpus)
```

Or download directly from HuggingFace (CC BY 4.0):

```bash
wget https://huggingface.co/datasets/theatticusproject/cuad-qa/resolve/main/CUADv1.json \
  -P data/raw/
```

### Step 3 — Classical Models (Weeks 2–4, no GPU)

```bash
jupyter notebook notebooks/
# Run in order:
#   03_eda_baseline.ipynb       → EDA + LR baseline (Macro-F1 = 0.6358)
#   04_classical_model.ipynb    → RF + 4 ablations + threshold tuning
#   05_neural_crosscheck.ipynb  → MLP cross-check
```

All classical notebooks run locally with scikit-learn. No GPU required. Expected runtime: < 5 min each.

### Step 4 — BERT Fine-Tuning (Week 6, Colab T4)

> **Important:** BERT training requires a GPU. Run in Google Colab.

1. Go to [colab.research.google.com](https://colab.research.google.com)
2. Open `notebooks/06_BERT_model.ipynb`
3. `Runtime → Change runtime type → T4 GPU`
4. Upload `data.zip` when prompted (Cell 2)
5. Run all cells (~90 min on T4, ~25 min on A100)
6. Model saves to Google Drive at `/content/drive/MyDrive/contract_risk_cuad/model/`

**Colab version pins (applied in Cell 1):**
```bash
pip install 'transformers==4.46.3' datasets==2.21.0 accelerate
```

> Do **not** use `transformers==4.40.0` (Colab default) — breaks on Python 3.12 via ernie_m registry scan.
> Do **not** use `datasets>=3.0.0` — removed CUAD loader script support.

### Step 5 — Connect Trained Model to Backend

After training, download `pytorch_model.bin` from Google Drive and place it here:

```
models/roberta-finetuned/
├── pytorch_model.bin     ← from Google Drive
└── config.json           ← create this file:
```

```json
{
  "model_type": "bert",
  "best_threshold": 0.10
}
```

Then restart the backend:
```bash
cd contract-risk-api
pip install torch transformers
uvicorn app.main:app --port 8080
# /health will now report: "model_type": "roberta-qa"
```

### Step 6 — Run Tests

```bash
cd contract-risk-api
pip install pytest httpx pytest-asyncio
pytest tests/ -v
# 15 tests, all pass with LR fallback (no GPU needed)
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/analyze` | Score a contract → risk scorecard |
| `GET` | `/health` | Model status (roberta-qa or lr-tfidf-fallback) |
| `GET` | `/clauses` | All 41 clause types with risk weights |
| `GET` | `/docs` | Swagger UI |

**POST /analyze example:**
```bash
curl -X POST http://localhost:8080/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Vendor liability shall not be limited under any circumstances..."}'
```

---

## Project Structure

```
contract-risk-scoring/
├── notebooks/
│   ├── 03_eda_baseline.ipynb         ← EDA + LR baseline
│   ├── 04_classical_model.ipynb      ← RF + ablations
│   ├── 05_neural_crosscheck.ipynb    ← MLP cross-check
│   └── 06_BERT_model.ipynb           ← BERT fine-tuning (Colab)
├── contract-risk-api/                ← FastAPI backend
│   ├── app/
│   │   ├── main.py                   ← App factory + lifespan
│   │   ├── core/config.py            ← All settings (reads .env)
│   │   ├── models/schemas.py         ← Pydantic v2 schemas
│   │   ├── routers/analyze.py        ← POST /analyze
│   │   ├── routers/health.py         ← GET /health, /clauses
│   │   └── services/scorer.py        ← BERT + LR fallback
│   ├── tests/test_api.py             ← 15 pytest tests
│   └── requirements.txt
├── contract-risk-ui/                 ← Next.js frontend
│   ├── app/
│   │   ├── page.tsx                  ← Contract input page
│   │   ├── analyze/page.tsx          ← Risk scorecard page
│   │   └── api/analyze/route.ts      ← API proxy route
│   ├── components/
│   │   ├── RiskGauge.tsx             ← Animated SVG ring gauge
│   │   └── ClauseCard.tsx            ← Expandable clause card
│   └── lib/types.ts                  ← Types + mock data
├── models/
│   └── roberta-finetuned/            ← Place pytorch_model.bin here
├── data/
│   └── raw/                          ← READ-ONLY — CUAD data.zip contents
├── environment.yml                   ← Conda environment (full stack)
├── requirements-notebooks.txt        ← Pip-only (notebooks + Colab)
├── Makefile                          ← One-command targets
└── README.md
```

---

## Model Ladder Summary

| Week | Model | Data | Macro-F1 | Key finding |
|---|---|---|---|---|
| W2 | LR balanced bigram | Simulated | 0.6358 | Bigrams +0.024 over unigrams; macro-F1 exposes what micro hides |
| W3 | RF 100-tree balanced | Simulated | 0.5145 | Good AUROC (0.8525) but probability miscalibration collapses macro-F1 |
| W3★ | RF + threshold=0.20 | Simulated | **0.6533** | Threshold tuning alone: +0.139 macro-F1. Largest single gain |
| W3 | LR C=5.0 | Simulated | 0.6406 | Best AUROC (0.8781). Less regularization lifts rare-clause weights |
| W4 | MLP-A 1×128 | Simulated | 0.5119 | −0.124 vs LR. Non-linearity on TF-IDF features does not help |
| W6 | bert-base-uncased | Real CUAD | AUPR (see notebook) | Extractive QA — resolves negation polarity. Reports AUPR, not F1 |

> W2–W4 metrics are Macro-F1 on simulated data. W6 uses AUPR on real CUAD. These are not directly comparable.

---

## Data License

CUAD (Contract Understanding Atticus Dataset) is licensed under **CC BY 4.0**.  
Source: Hendrycks et al., "CUAD: An Expert-Annotated NLP Dataset for Legal Contract Review" (2021).  
HuggingFace: [theatticusproject/cuad-qa](https://huggingface.co/datasets/theatticusproject/cuad-qa)

---

## Disclaimer

This system is a triage aid for attorney review. It does not provide legal advice, assess enforceability, or recommend negotiation positions. All contracts still require attorney review before execution.
