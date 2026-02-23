"""Shared metric + scoring utilities used across training and evaluation."""
import numpy as np


def risk_score_to_label(
    score: float,
    auto_clear_threshold: float = 30.0,
    high_risk_threshold: float = 70.0,
) -> str:
    """Convert continuous risk score to a human-readable triage label."""
    if score < auto_clear_threshold:
        return "LOW — Auto-clear recommended"
    elif score < high_risk_threshold:
        return "MEDIUM — Flag for expedited review"
    else:
        return "HIGH — Requires immediate legal review"


def precision_at_k(scores: np.ndarray, labels: np.ndarray, k: int) -> float:
    """Precision of the top-k highest-risk contracts."""
    top_k_idx = np.argsort(scores)[-k:]
    return float(labels[top_k_idx].mean())


def attorney_hours_saved(
    n_contracts: int,
    auto_clear_rate: float,
    hours_per_review: float = 2.5,
) -> float:
    """Estimate attorney hours saved vs. reviewing every contract."""
    return n_contracts * auto_clear_rate * hours_per_review
