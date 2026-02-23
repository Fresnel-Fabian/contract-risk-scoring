"""Unit tests for metric utilities."""
import numpy as np
import pytest
from src.utils.metrics import risk_score_to_label, precision_at_k, attorney_hours_saved


def test_risk_labels():
    assert "LOW" in risk_score_to_label(20)
    assert "MEDIUM" in risk_score_to_label(50)
    assert "HIGH" in risk_score_to_label(80)


def test_risk_label_boundaries():
    assert "LOW" in risk_score_to_label(29.9)
    assert "MEDIUM" in risk_score_to_label(30.0)
    assert "MEDIUM" in risk_score_to_label(69.9)
    assert "HIGH" in risk_score_to_label(70.0)


def test_precision_at_k():
    scores = np.array([0.1, 0.9, 0.8, 0.2, 0.7])
    labels = np.array([0,   1,   1,   0,   1  ])
    assert precision_at_k(scores, labels, k=3) == 1.0   # top 3 are all positive


def test_attorney_hours_saved():
    hours = attorney_hours_saved(n_contracts=100, auto_clear_rate=0.4, hours_per_review=2.5)
    assert hours == 100.0
