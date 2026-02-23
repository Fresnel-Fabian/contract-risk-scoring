"""
Full evaluation suite.
Outputs reports/evaluation_results.json + matplotlib plots.
Run via: make evaluate
"""
import json
import numpy as np
from pathlib import Path
from sklearn.metrics import (
    f1_score, roc_auc_score, classification_report,
    average_precision_score,
)


def evaluate_clause_classifier(y_true, y_pred, label_names: list) -> dict:
    """Micro + macro F1 for 41-way clause classification."""
    return {
        "f1_micro": f1_score(y_true, y_pred, average="micro"),
        "f1_macro": f1_score(y_true, y_pred, average="macro"),
        "per_class": classification_report(
            y_true, y_pred, target_names=label_names, output_dict=True
        ),
    }


def evaluate_risk_model(risk_scores: np.ndarray, risk_labels: np.ndarray) -> dict:
    """AUROC, AUPRC, and auto-clear rate."""
    normalized = risk_scores / 100.0
    auto_clear_mask = risk_scores < 30
    high_risk_mask  = risk_scores >= 70
    return {
        "auroc":           float(roc_auc_score(risk_labels, normalized)),
        "auprc":           float(average_precision_score(risk_labels, normalized)),
        "auto_clear_rate": float(auto_clear_mask.mean()),
        "high_risk_precision": (
            float(risk_labels[high_risk_mask].mean())
            if high_risk_mask.any() else None
        ),
        "n_contracts": int(len(risk_scores)),
        "n_auto_cleared": int(auto_clear_mask.sum()),
        "n_high_risk":    int(high_risk_mask.sum()),
    }


def save_results(results: dict, out_path: str = "reports/evaluation_results.json") -> None:
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {out_path}")
