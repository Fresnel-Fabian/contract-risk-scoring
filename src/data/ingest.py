"""
Data ingestion: CUAD + EDGAR + CourtListener.
All paths resolved from config.yaml — never hardcoded.
"""
import yaml
from pathlib import Path


def load_config(config_path: str = "configs/config.yaml") -> dict:
    with open(config_path) as f:
        return yaml.safe_load(f)


def download_cuad(config: dict) -> None:
    """Download CUAD v1 from HuggingFace datasets."""
    from datasets import load_dataset
    out = Path(config["paths"]["raw_data"]) / "cuad"
    out.mkdir(parents=True, exist_ok=True)
    dataset = load_dataset("cuad", cache_dir=str(out))
    print(f"CUAD downloaded: {len(dataset['train'])} train, {len(dataset['test'])} test samples")


def download_edgar(config: dict, max_contracts: int = None) -> None:
    """
    Download material contracts (EX-10) from SEC EDGAR API.
    Reproducible: same parameters always return same filing set.
    """
    max_contracts = max_contracts or config["data"]["max_contracts_edgar"]
    out = Path(config["paths"]["raw_data"]) / "edgar"
    out.mkdir(parents=True, exist_ok=True)
    print(f"[EDGAR] Querying {config['data']['edgar_filing_types']} — max {max_contracts} contracts")
    # Full implementation in scripts/download_edgar.py


if __name__ == "__main__":
    cfg = load_config()
    download_cuad(cfg)
    download_edgar(cfg)
