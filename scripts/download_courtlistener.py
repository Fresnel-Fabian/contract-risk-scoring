"""download_courtlistener -- called via: make data"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.data.ingest import load_config

if __name__ == "__main__":
    cfg = load_config()
    print("[download_courtlistener] Starting download...")
    # TODO: Implement download logic
    print("[download_courtlistener] Done.")
