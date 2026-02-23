"""
Preprocessing pipeline: clause segmentation, tokenization, label encoding.
Operates on raw/ -> writes to processed/. Never modifies raw/.
"""
import random
import numpy as np


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)


def stratified_split(
    contracts: list,
    train: float = 0.70,
    val: float = 0.15,
    seed: int = 42,
    stratify_key: str = "contract_type",
) -> tuple:
    """
    Stratified split by contract_type so all types appear in every fold.
    Returns (train_contracts, val_contracts, test_contracts).
    """
    from sklearn.model_selection import train_test_split
    labels = [c[stratify_key] for c in contracts]
    test_size = round(1 - train - val, 10)
    train_val, test = train_test_split(
        contracts, test_size=test_size, stratify=labels, random_state=seed
    )
    labels_tv = [c[stratify_key] for c in train_val]
    val_size = round(val / (train + val), 10)
    train_data, val_data = train_test_split(
        train_val, test_size=val_size, stratify=labels_tv, random_state=seed
    )
    return train_data, val_data, test


def segment_clauses(text: str) -> list:
    """
    Split contract text into clause spans.
    Returns list of {text, start_char, end_char}.
    Full implementation uses spaCy sentence segmentation +
    rule-based clause boundary detection (section headers, numbered lists).
    """
    raise NotImplementedError("Implement clause segmentation in Stage 1")
