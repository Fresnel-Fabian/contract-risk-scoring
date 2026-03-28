"""
Contract Risk Scoring Service
==============================
Two-tier design:
  Primary  — RobertaForQuestionAnswering fine-tuned on CUAD
             (loaded when models/roberta-finetuned/ exists + torch installed)
  Fallback — LR + TF-IDF, trains on synthetic data in ~5 s, no GPU needed

Direct class imports (not Auto*) avoid the ernie_m registry scan that
breaks on Colab / Python 3.12.
"""
from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Optional

import numpy as np

from app.models.schemas import AnalyzeResponse, DetectedClause
from app.core.config import settings

logger = logging.getLogger("contract_risk.scorer")

# ── 41 CUAD clause types ──────────────────────────────────────────────────────
CLAUSE_TYPES: list[str] = [
    "Affiliate License-Licensee", "Affiliate License-Licensor",
    "Agreement Date", "Anti-Assignment", "Audit Rights",
    "Cap On Liability", "Change Of Control",
    "Competitive Restriction Exception", "Covenant Not To Sue",
    "Document Name", "Effective Date", "Exclusivity",
    "Expiration Date", "Governing Law", "Insurance",
    "Ip Ownership Assignment", "Irrevocable Or Perpetual License",
    "Joint Ip Ownership", "License Grant", "Liquidated Damages",
    "Minimum Commitment", "Most Favored Nation",
    "No-Solicit Of Customers", "No-Solicit Of Employees",
    "Non-Compete", "Non-Disparagement", "Non-Transferable License",
    "Notice Period To Terminate Renewal", "Parties",
    "Post-Termination Services", "Price Restrictions",
    "Renewal Term", "Revenue/Profit Sharing", "Rofr/Rofo/Rofn",
    "Source Code Escrow", "Termination For Convenience",
    "Third Party Beneficiary", "Uncapped Liability",
    "Unlimited/All-You-Can-Eat-License", "Volume Restriction",
    "Warranty Duration",
]

CLAUSE_QUESTIONS: dict[str, str] = {
    ct: f'Highlight the parts (if any) of this contract related to "{ct}".'
    for ct in CLAUSE_TYPES
}


# ── helpers ───────────────────────────────────────────────────────────────────

def _compute_risk_score(detected: list[DetectedClause]) -> int:
    if not detected:
        return 0
    w = np.array([d.risk_weight for d in detected], dtype=float)
    c = np.array([d.confidence  for d in detected], dtype=float)
    base  = float(np.dot(w / w.sum(), c)) * 80
    boost = sum(d.confidence * d.risk_weight for d in detected
                if d.risk_weight >= 7)
    return min(100, int(base + boost * 3))


def _triage(score: int) -> tuple[str, str]:
    if score >= settings.triage_urgent_threshold:
        return ("URGENT REVIEW",
                "High-risk clauses detected. Requires immediate legal review before signing.")
    if score >= settings.triage_flag_threshold:
        return ("FLAG FOR REVIEW",
                "Moderate risk present. Schedule legal review within standard SLA.")
    return ("AUTO-CLEAR",
            "Low-risk contract. No immediate legal review required.")


# ══════════════════════════════════════════════════════════════════════════════
# PRIMARY — RoBERTa extractive QA
# ══════════════════════════════════════════════════════════════════════════════

class RobertaScorer:
    """
    Runs all 41 clause questions against the contract using span extraction.

    Key design decisions:
    - Uses RobertaForQuestionAnswering directly (not AutoModelForQuestionAnswering)
      to avoid the ernie_m module scan that breaks on Python 3.12.
    - Uses sequence_ids() to identify context tokens, not the (0,0) heuristic,
      so answers at character position 0 are not incorrectly skipped.
    - Sliding window (stride) handles contracts longer than max_seq_length.
    """

    def __init__(self, model_dir: str):
        import torch
        from transformers import RobertaForQuestionAnswering, RobertaTokenizerFast

        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info("Loading RoBERTa from %s on %s", model_dir, self._device)

        self._tok   = RobertaTokenizerFast.from_pretrained(model_dir)
        self._model = (
            RobertaForQuestionAnswering.from_pretrained(model_dir)
            .to(self._device)
            .eval()
        )

        # Read best_threshold from saved config if present
        cfg_path = Path(model_dir) / "config.json"
        self._default_threshold = settings.confidence_threshold
        if cfg_path.exists():
            try:
                with open(cfg_path) as f:
                    saved = json.load(f)
                self._default_threshold = float(
                    saved.get("best_threshold", self._default_threshold)
                )
            except Exception:
                pass

        n = sum(p.numel() for p in self._model.parameters())
        logger.info("RoBERTa ready — %dM params, threshold=%.2f",
                    n // 1_000_000, self._default_threshold)

    @property
    def model_name(self) -> str:
        return "roberta-base fine-tuned on CUAD"

    @property
    def default_threshold(self) -> float:
        return self._default_threshold

    @property
    def is_neural(self) -> bool:
        return True

    def score(self, text: str, threshold: float) -> list[DetectedClause]:
        import torch
        import torch.nn.functional as F

        detected: list[DetectedClause] = []

        for clause, question in CLAUSE_QUESTIONS.items():
            # Tokenize with sliding window for long contracts.
            # return_offsets_mapping gives character positions for each token.
            enc = self._tok(
                question,
                text,
                max_length=settings.max_seq_length,
                truncation="only_second",
                stride=settings.stride,
                return_overflowing_tokens=True,
                return_offsets_mapping=True,
                padding="max_length",
                return_tensors="pt",
            )

            # Save offset_mapping and sample_map before moving to GPU.
            # offset_mapping stays on CPU as a Python list of (start, end) tuples.
            offset_mapping = enc.pop("offset_mapping")       # (n_windows, seq_len, 2)
            sample_map     = enc.pop("overflow_to_sample_mapping", None)

            # sequence_ids per window — identifies question (0), context (1),
            # and special tokens (None). Used to mask non-context positions.
            seq_ids_per_window = [
                enc.sequence_ids(i) for i in range(len(enc["input_ids"]))
            ]

            enc = {k: v.to(self._device) for k, v in enc.items()}

            with torch.no_grad():
                out = self._model(**enc)

            best_conf, best_text = 0.0, ""

            for i in range(len(out.start_logits)):
                sl = out.start_logits[i]   # (seq_len,)
                el = out.end_logits[i]     # (seq_len,)
                seq_ids = seq_ids_per_window[i]
                offsets = offset_mapping[i]   # (seq_len, 2) tensor

                # Build a mask: True only for context tokens (sequence_id == 1)
                context_mask = [sid == 1 for sid in seq_ids]

                # Find best start in context
                best_s_score, best_s_idx = float("-inf"), 0
                for j, is_ctx in enumerate(context_mask):
                    if is_ctx and sl[j].item() > best_s_score:
                        best_s_score = sl[j].item()
                        best_s_idx = j

                # Find best end in context at or after start
                best_e_score, best_e_idx = float("-inf"), 0
                for j, is_ctx in enumerate(context_mask):
                    if is_ctx and j >= best_s_idx and el[j].item() > best_e_score:
                        best_e_score = el[j].item()
                        best_e_idx = j

                if best_s_idx > best_e_idx:
                    continue

                # Confidence = product of softmax probabilities at the chosen positions
                conf = (
                    F.softmax(sl, dim=-1)[best_s_idx]
                    * F.softmax(el, dim=-1)[best_e_idx]
                ).item()

                if conf > best_conf:
                    cs = offsets[best_s_idx][0].item()
                    ce = offsets[best_e_idx][1].item()
                    # Skip if span is empty (shouldn't happen but guard)
                    if ce <= cs:
                        continue
                    best_conf = conf
                    best_text = text[cs:ce].strip()

            if best_conf >= threshold and best_text:
                detected.append(DetectedClause(
                    clause=clause,
                    text=best_text,
                    confidence=round(best_conf, 4),
                    risk_weight=settings.risk_weights.get(clause, 3),
                ))

        return detected


# ══════════════════════════════════════════════════════════════════════════════
# FALLBACK — LR + TF-IDF
# ══════════════════════════════════════════════════════════════════════════════

_LEGAL_VOCAB: list[str] = [
    "agreement", "party", "parties", "vendor", "licensee", "licensor",
    "term", "termination", "renewal", "notice", "obligation", "liability",
    "damages", "intellectual", "property", "ownership", "license", "grant",
    "exclusive", "confidential", "disclosure", "warranty", "indemnification",
    "governing", "law", "payment", "fee", "revenue", "profit", "assignment",
    "transfer", "subsidiary", "affiliate", "control", "change", "merger",
    "source", "code", "escrow", "audit", "insurance", "non-compete",
    "employee", "customer", "period", "effective", "expiration", "shall",
    "may", "must", "cap", "uncapped", "limitation", "unlimited", "maximum",
    "exceed", "covenant", "sue", "third", "beneficiary", "irrevocable",
    "perpetual", "solicit", "liquidated", "volume", "price", "minimum",
    "commitment", "rofo", "rofr", "rofn", "duration",
]

_POSITIVE_RATES: dict[str, float] = {
    "Document Name": 0.92, "Parties": 0.95, "Agreement Date": 0.85,
    "Effective Date": 0.72, "Expiration Date": 0.58, "Renewal Term": 0.44,
    "Notice Period To Terminate Renewal": 0.38, "Governing Law": 0.89,
    "Most Favored Nation": 0.08, "Non-Compete": 0.31, "Exclusivity": 0.22,
    "No-Solicit Of Customers": 0.18, "No-Solicit Of Employees": 0.21,
    "Non-Disparagement": 0.14, "Cap On Liability": 0.52,
    "Liquidated Damages": 0.12, "Termination For Convenience": 0.39,
    "Anti-Assignment": 0.61, "Revenue/Profit Sharing": 0.19,
    "Price Restrictions": 0.24, "Minimum Commitment": 0.17,
    "Volume Restriction": 0.11, "Ip Ownership Assignment": 0.43,
    "Joint Ip Ownership": 0.07, "License Grant": 0.55,
    "Non-Transferable License": 0.29, "Affiliate License-Licensor": 0.13,
    "Affiliate License-Licensee": 0.11,
    "Unlimited/All-You-Can-Eat-License": 0.06,
    "Irrevocable Or Perpetual License": 0.16, "Source Code Escrow": 0.05,
    "Post-Termination Services": 0.28, "Audit Rights": 0.34,
    "Uncapped Liability": 0.09, "Warranty Duration": 0.31,
    "Insurance": 0.26, "Covenant Not To Sue": 0.08,
    "Third Party Beneficiary": 0.12, "Change Of Control": 0.33,
    "Rofr/Rofo/Rofn": 0.09, "Competitive Restriction Exception": 0.15,
}


class LRFallbackScorer:
    """
    LR + TF-IDF bigram fallback.
    Trains on 510 synthetic contracts at startup (~5 s, no GPU).
    Returns probability per clause; threshold=0.20 (val-tuned W3 ablation B2).
    """

    def __init__(self):
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.multiclass import OneVsRestClassifier
        from sklearn.preprocessing import MultiLabelBinarizer

        logger.info("Training LR fallback on synthetic data …")
        t0 = time.perf_counter()

        rng = np.random.default_rng(settings.lr_seed)
        texts: list[str] = []
        labels: list[list[str]] = []

        for _ in range(510):
            n = int(np.clip(rng.lognormal(7.5, 0.4), 800, 3000))
            present = [c for c in CLAUSE_TYPES
                       if rng.random() < _POSITIVE_RATES.get(c, 0.2)]
            # Draw words from vocabulary
            words: list[str] = rng.choice(
                np.array(_LEGAL_VOCAB), size=n, replace=True
            ).tolist()
            # Inject clause-specific keywords for signal
            for clause in present:
                kw = clause.lower().split()[0]
                n_inject = max(2, n // 80)
                inject_idx = rng.choice(n, size=n_inject, replace=False)
                for idx in inject_idx:
                    words[int(idx)] = kw   # explicit int() avoids numpy int64 issues
            texts.append(" ".join(words))
            labels.append(present)

        self._mlb = MultiLabelBinarizer(classes=CLAUSE_TYPES)
        Y = self._mlb.fit_transform(labels)

        self._vec = TfidfVectorizer(
            max_features=settings.tfidf_max_features,
            ngram_range=(1, settings.tfidf_ngram_max),
            sublinear_tf=True,
            min_df=2,
        )
        X = self._vec.fit_transform(texts)

        self._clf = OneVsRestClassifier(
            LogisticRegression(
                C=settings.lr_C,
                max_iter=300,
                class_weight="balanced",
                random_state=settings.lr_seed,
            ),
            n_jobs=-1,
        )
        self._clf.fit(X, Y)
        logger.info("LR fallback ready in %.1fs", time.perf_counter() - t0)

    @property
    def model_name(self) -> str:
        return "LR (balanced bigram TF-IDF) — fallback, no GPU needed"

    @property
    def default_threshold(self) -> float:
        # 0.20 is the val-tuned threshold from Week 3 ablation B2 (+0.139 macro-F1)
        return 0.20

    @property
    def is_neural(self) -> bool:
        return False

    def score(self, text: str, threshold: float) -> list[DetectedClause]:
        X = self._vec.transform([text])
        # estimators_ is a list of binary classifiers, one per clause type.
        # predict_proba returns shape (1, 2); index [0, 1] = P(positive class).
        probas = np.array([
            est.predict_proba(X)[0, 1]
            for est in self._clf.estimators_
        ])
        return [
            DetectedClause(
                clause=clause,
                text=(
                    f"[Detected with {probas[i]:.0%} confidence — "
                    "upgrade to RoBERTa for exact text extraction]"
                ),
                confidence=round(float(probas[i]), 4),
                risk_weight=settings.risk_weights.get(clause, 3),
            )
            for i, clause in enumerate(CLAUSE_TYPES)
            if probas[i] >= threshold
        ]


# ══════════════════════════════════════════════════════════════════════════════
# SERVICE FACADE
# ══════════════════════════════════════════════════════════════════════════════

class ScoringService:
    """
    Single entry point for scoring.
    Instantiated once during app lifespan; injected via FastAPI Depends.
    Auto-selects RoBERTa when model directory exists, LR otherwise.
    """

    def __init__(self):
        self._scorer: RobertaScorer | LRFallbackScorer = self._load()

    def _load(self) -> RobertaScorer | LRFallbackScorer:
        model_dir = settings.model_dir
        if model_dir and Path(model_dir).exists():
            try:
                import torch          # noqa: F401
                import transformers   # noqa: F401
                return RobertaScorer(model_dir)
            except Exception as exc:
                logger.warning("RoBERTa load failed (%s) — using LR fallback", exc)
        else:
            logger.info("'%s' not found — using LR fallback", model_dir)
        return LRFallbackScorer()

    @property
    def model_name(self) -> str:
        return self._scorer.model_name

    @property
    def is_neural(self) -> bool:
        return self._scorer.is_neural

    def analyze(self, text: str, threshold: Optional[float] = None) -> AnalyzeResponse:
        t0  = time.perf_counter()
        thr = threshold if threshold is not None else self._scorer.default_threshold

        detected = self._scorer.score(text, thr)
        detected.sort(key=lambda d: d.risk_weight * d.confidence, reverse=True)

        score        = _compute_risk_score(detected)
        triage, desc = _triage(score)
        elapsed_ms   = round((time.perf_counter() - t0) * 1000)

        logger.info(
            "analyze: %d words → score=%d %s clauses=%d (%dms)",
            len(text.split()), score, triage, len(detected), elapsed_ms,
        )

        return AnalyzeResponse(
            score=score,
            triage=triage,
            triage_description=desc,
            clauses=detected,
            word_count=len(text.split()),
            n_clauses_detected=len(detected),
            model=self.model_name,
            threshold=thr,
        )


# ── Module-level singleton ────────────────────────────────────────────────────
_service: Optional[ScoringService] = None


def get_scoring_service() -> ScoringService:
    """FastAPI Depends — returns the singleton."""
    if _service is None:
        raise RuntimeError("ScoringService not initialised. Check app lifespan.")
    return _service


def init_scoring_service() -> ScoringService:
    """Called once in app lifespan startup."""
    global _service
    _service = ScoringService()
    return _service
