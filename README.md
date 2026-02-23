# Contract Risk Scoring Engine

> **ML system that reads contract PDFs and outputs a ranked risk scorecard in under 60 seconds — telling legal ops which contracts need human review and why.**

## Problem

Legal review costs $300–$800/hr. Most vendor, partnership, and SaaS contracts are signed without any review. A single missed auto-renewal or IP-assignment clause can cost $200K+. This system auto-clears low-risk contracts and surfaces specific risky clauses with plain-English explanations for the rest.

## Quickstart

```bash
git clone https://github.com/fresnel-fabian/contract-risk-scoring
cd contract-risk-scoring
pip install -r requirements.txt
make data          # Download CUAD + EDGAR contracts
make train         # Fine-tune LegalBERT + train risk model
make evaluate      # Run full eval suite, outputs to reports/
make demo          # Score a sample contract
```

## Architecture

```
Contract PDF
    │
    ▼
[Stage 1] Clause Segmentation + Classification
          LegalBERT fine-tuned on CUAD (41 clause types)
    │
    ▼
[Stage 2] Clause-Level Risk Embedding
          Semantic similarity to known-risky clause corpus
    │
    ▼
[Stage 3] Contract-Level Risk Aggregation
          Attention-based aggregation over clause embeddings
    │
    ▼
[Stage 4] Explainability Layer
          SHAP over clause embeddings → ranked risk report
    │
    ▼
Risk Scorecard (0–100) + Flagged Clauses + Plain-English Explanations
```

## Project Structure

```
contract-risk-scoring/
├── data/
│   ├── raw/            # Original datasets — never modified
│   ├── processed/      # Cleaned, tokenized, feature-engineered
│   └── external/       # CourtListener proxy labels
├── notebooks/          # EDA and exploration (numbered, sequential)
├── src/                # All production-quality source code
│   ├── data/           # Ingestion + preprocessing pipelines
│   ├── models/         # Model definitions + training logic
│   ├── evaluation/     # Metrics, eval loops, reporting
│   └── utils/          # Shared helpers
├── configs/            # All hyperparams + paths in one place
├── tests/              # Unit + integration tests
├── reports/            # Generated PDFs, charts, weekly submissions
└── scripts/            # One-off utility scripts
```

## Data Sources

| Dataset | Source | Access | Size |
|---|---|---|---|
| CUAD v1 | HuggingFace `datasets/cuad` | Public | 510 contracts, 13K+ labels |
| EDGAR Contracts | SEC EDGAR API | Public | ~100K material contracts |
| CourtListener | REST API | Public | Proxy risk labels |
| LegalBERT | HuggingFace `nlpaueb/legal-bert-base-uncased` | Public | Pretrained weights |

## Success Metrics

| Metric | Target |
|---|---|
| Clause extraction F1 | ≥ 0.80 |
| Contract-level risk AUROC | ≥ 0.82 |
| Auto-clear rate (low-risk contracts) | ≥ 40% |
| Attorney-hours saved per 100 contracts | ≥ 60 hrs |

## Reproducibility

All randomness is seeded via `configs/config.yaml`. Running `make all` from a clean environment produces identical results. See `configs/config.yaml` for all hyperparameters.

## Weekly Reports

- [x] Week 1 — Project Charter + Dataset Contract (`reports/week1_charter.pdf`)

## Author

Fresnel Fabian — MPS Applied Machine Intelligence, Northeastern University Roux Institute
