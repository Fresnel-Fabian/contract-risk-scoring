"""Unit tests for preprocessing pipeline."""
from src.data.preprocess import stratified_split


def make_fake_contracts(n: int = 100) -> list:
    types = ["NDA", "MSA", "SOW", "Employment", "License"]
    return [{"id": i, "contract_type": types[i % len(types)], "text": f"Contract {i}"} for i in range(n)]


def test_split_sizes():
    contracts = make_fake_contracts(100)
    train, val, test = stratified_split(contracts)
    assert len(train) + len(val) + len(test) == 100


def test_no_type_missing():
    contracts = make_fake_contracts(100)
    train, val, test = stratified_split(contracts)
    all_types = {"NDA", "MSA", "SOW", "Employment", "License"}
    for split in [train, val, test]:
        assert {c["contract_type"] for c in split} == all_types


def test_seed_reproducibility():
    contracts = make_fake_contracts(100)
    train1, _, _ = stratified_split(contracts, seed=42)
    train2, _, _ = stratified_split(contracts, seed=42)
    assert [c["id"] for c in train1] == [c["id"] for c in train2]
