# Contract Risk Scoring Engine — Makefile
# Usage: make <target>
#
# Prerequisites: conda or pip, Node.js >= 18

.PHONY: env install-backend install-frontend data \
        train-bert run-backend run-frontend test \
        run-all clean help

# ── Environment ───────────────────────────────────────────────────────────────
env:
	@echo "Creating conda environment 'contract-risk'..."
	conda env create -f environment.yml
	@echo ""
	@echo "Activate with: conda activate contract-risk"

# ── Install ───────────────────────────────────────────────────────────────────
install-backend:
	cd contract-risk-api && pip install -r requirements.txt

install-frontend:
	cd contract-risk-ui && npm install

install: install-backend install-frontend

# ── Data ──────────────────────────────────────────────────────────────────────
data:
	@echo "Checking for CUAD data..."
	@if [ ! -f data/raw/train_separate_questions.json ]; then \
		echo "data.zip not found. Download options:"; \
		echo "  Option 1: Place data.zip in project root, then run: unzip data.zip -d data/raw/"; \
		echo "  Option 2: wget https://huggingface.co/datasets/theatticusproject/cuad-qa/resolve/main/CUADv1.json -P data/raw/"; \
	else \
		echo "CUAD data found."; \
	fi

# ── Training (runs in Colab — this is a reminder target) ─────────────────────
train-bert:
	@echo "BERT fine-tuning runs in Google Colab (T4 GPU required)."
	@echo "Open: notebooks/06_BERT_model.ipynb"
	@echo "Runtime → Change runtime type → T4 GPU → Run all"
	@echo ""
	@echo "After training, download pytorch_model.bin from Google Drive and place at:"
	@echo "  models/roberta-finetuned/pytorch_model.bin"

# ── Backend ───────────────────────────────────────────────────────────────────
run-backend:
	cd contract-risk-api && uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

run-backend-prod:
	cd contract-risk-api && uvicorn app.main:app --host 0.0.0.0 --port 8080 --workers 2

# ── Frontend ──────────────────────────────────────────────────────────────────
run-frontend:
	cd contract-risk-ui && npm run dev

run-frontend-real:
	cd contract-risk-ui && USE_MOCK=false BACKEND_URL=http://localhost:8080 npm run dev

# ── Full stack ────────────────────────────────────────────────────────────────
# Run backend + frontend together (requires tmux or two terminals)
run-all:
	@echo "Starting backend on :8080 and frontend on :3000"
	@echo "Open http://localhost:3000 after both are ready"
	@echo ""
	@echo "Terminal 1: make run-backend"
	@echo "Terminal 2: make run-frontend-real"

# ── Tests ─────────────────────────────────────────────────────────────────────
test:
	cd contract-risk-api && pytest tests/ -v

test-verbose:
	cd contract-risk-api && pytest tests/ -v --tb=short

# ── Classical notebooks (no GPU) ──────────────────────────────────────────────
run-notebooks:
	jupyter notebook notebooks/

# ── Clean ─────────────────────────────────────────────────────────────────────
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .next -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "Cleaned build artifacts."

# ── Help ──────────────────────────────────────────────────────────────────────
help:
	@echo ""
	@echo "Contract Risk Scoring Engine"
	@echo "============================"
	@echo ""
	@echo "Setup:"
	@echo "  make env              Create conda environment"
	@echo "  make install          Install backend + frontend dependencies"
	@echo "  make data             Check for / download CUAD data"
	@echo ""
	@echo "Development:"
	@echo "  make run-backend      FastAPI backend on :8080 (mock or real model)"
	@echo "  make run-frontend     Next.js frontend on :3000 (mock mode)"
	@echo "  make run-frontend-real  Next.js connected to backend"
	@echo "  make test             Run 15 pytest tests (no GPU required)"
	@echo ""
	@echo "Training:"
	@echo "  make train-bert       Instructions for Colab BERT fine-tuning"
	@echo ""
	@echo "Docs: http://localhost:8080/docs (after make run-backend)"
