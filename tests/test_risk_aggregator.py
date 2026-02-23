"""Unit tests for the attention risk aggregator."""
import torch
from src.models.risk_aggregator import AttentionRiskAggregator


def test_output_shape():
    model = AttentionRiskAggregator(embed_dim=64, hidden_dim=32, num_heads=4)
    embeddings = torch.randn(4, 10, 64)
    scores, attn = model(embeddings)
    assert scores.shape == (4,)


def test_scores_in_range():
    model = AttentionRiskAggregator(embed_dim=64, hidden_dim=32, num_heads=4)
    embeddings = torch.randn(8, 15, 64)
    scores, _ = model(embeddings)
    assert (scores >= 0).all() and (scores <= 100).all()
