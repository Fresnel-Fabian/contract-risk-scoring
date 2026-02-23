.PHONY: all data train evaluate demo clean test lint

# ── Reproduce everything end-to-end ────────────────────────────────────────
all: data train evaluate

# ── Data pipeline ──────────────────────────────────────────────────────────
data: data-cuad data-edgar data-court

data-cuad:
	python scripts/download_cuad.py

data-edgar:
	python scripts/download_edgar.py

data-court:
	python scripts/download_courtlistener.py

# ── Model training ─────────────────────────────────────────────────────────
train:
	python src/models/train_clause_classifier.py --config configs/config.yaml
	python src/models/train_risk_aggregator.py   --config configs/config.yaml

# ── Evaluation ─────────────────────────────────────────────────────────────
evaluate:
	python src/evaluation/evaluate.py --config configs/config.yaml

# ── Demo: score a single contract ─────────────────────────────────────────
demo:
	python src/demo.py --contract data/raw/sample_contract.pdf

# ── Download pretrained model weights ─────────────────────────────────────
download-model:
	python scripts/download_legalbert.py

# ── Tests ──────────────────────────────────────────────────────────────────
test:
	pytest tests/ -v --tb=short

lint:
	ruff check src/ tests/

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache
