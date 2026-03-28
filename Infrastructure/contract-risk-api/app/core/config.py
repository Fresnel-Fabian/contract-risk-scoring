"""
All application settings.
Reads from environment variables or .env file via python-dotenv.
Falls back to defaults if pydantic-settings is unavailable.
"""
from __future__ import annotations
import os
from pathlib import Path


# ── Risk weights defined at module level ──────────────────────────────────────
DEFAULT_RISK_WEIGHTS: dict[str, int] = {
    "Uncapped Liability": 10,
    "Cap On Liability": 9,
    "Ip Ownership Assignment": 9,
    "Joint Ip Ownership": 8,
    "Change Of Control": 8,
    "Liquidated Damages": 7,
    "Anti-Assignment": 7,
    "Source Code Escrow": 7,
    "Non-Compete": 6,
    "Audit Rights": 6,
    "Covenant Not To Sue": 6,
    "Most Favored Nation": 6,
    "Irrevocable Or Perpetual License": 6,
    "Unlimited/All-You-Can-Eat-License": 6,
    "Termination For Convenience": 5,
    "Exclusivity": 5,
    "Competitive Restriction Exception": 5,
    "Rofr/Rofo/Rofn": 5,
    "Revenue/Profit Sharing": 5,
    "Minimum Commitment": 4,
    "Volume Restriction": 4,
    "Price Restrictions": 4,
    "Non-Disparagement": 3,
    "No-Solicit Of Employees": 3,
    "No-Solicit Of Customers": 3,
    "Warranty Duration": 3,
    "Insurance": 3,
    "Post-Termination Services": 3,
    "Third Party Beneficiary": 3,
    "Affiliate License-Licensee": 3,
    "Affiliate License-Licensor": 3,
    "Non-Transferable License": 3,
    "License Grant": 2,
    "Renewal Term": 2,
    "Notice Period To Terminate Renewal": 2,
    "Expiration Date": 2,
    "Effective Date": 2,
    "Agreement Date": 1,
    "Governing Law": 1,
    "Parties": 1,
    "Document Name": 1,
}


def _load_dotenv() -> None:
    """Load .env file if present, using python-dotenv if available."""
    env_path = Path(".env")
    if not env_path.exists():
        return
    try:
        from dotenv import load_dotenv
        load_dotenv(env_path)
    except ImportError:
        # Manual parse if python-dotenv not installed
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, val = line.partition("=")
                    os.environ.setdefault(key.strip(), val.strip())


_load_dotenv()


class _Settings:
    """
    Settings backed by environment variables.
    Supports pydantic-settings when installed, plain env vars otherwise.
    Compatible with both approaches so FastAPI and tests work identically.
    """

    def _get(self, key: str, default: str) -> str:
        return os.environ.get(key.upper(), default)

    def _getbool(self, key: str, default: bool) -> bool:
        v = os.environ.get(key.upper(), str(default)).lower()
        return v in ("1", "true", "yes")

    def _getint(self, key: str, default: int) -> int:
        try:
            return int(os.environ.get(key.upper(), str(default)))
        except ValueError:
            return default

    def _getfloat(self, key: str, default: float) -> float:
        try:
            return float(os.environ.get(key.upper(), str(default)))
        except ValueError:
            return default

    # ── Server ────────────────────────────────────────────────────────────────
    @property
    def app_name(self) -> str:
        return self._get("APP_NAME", "Contract Risk Scoring Engine")

    @property
    def version(self) -> str:
        return self._get("VERSION", "1.0.0")

    @property
    def debug(self) -> bool:
        return self._getbool("DEBUG", False)

    @property
    def host(self) -> str:
        return self._get("HOST", "0.0.0.0")

    @property
    def port(self) -> int:
        return self._getint("PORT", 8080)

    # ── CORS ──────────────────────────────────────────────────────────────────
    @property
    def allowed_origins(self) -> str:
        return self._get("ALLOWED_ORIGINS",
                         "http://localhost:3000,http://localhost:3001")

    @property
    def origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    # ── Model ─────────────────────────────────────────────────────────────────
    @property
    def model_dir(self) -> str:
        return self._get("MODEL_DIR", "models/roberta-finetuned")

    @property
    def confidence_threshold(self) -> float:
        return self._getfloat("CONFIDENCE_THRESHOLD", 0.10)

    @property
    def max_seq_length(self) -> int:
        return self._getint("MAX_SEQ_LENGTH", 384)

    @property
    def stride(self) -> int:
        return self._getint("STRIDE", 128)

    # ── LR fallback ───────────────────────────────────────────────────────────
    @property
    def tfidf_max_features(self) -> int:
        return self._getint("TFIDF_MAX_FEATURES", 10_000)

    @property
    def tfidf_ngram_max(self) -> int:
        return self._getint("TFIDF_NGRAM_MAX", 2)

    @property
    def lr_C(self) -> float:
        return self._getfloat("LR_C", 5.0)

    @property
    def lr_seed(self) -> int:
        return self._getint("LR_SEED", 42)

    # ── Triage thresholds ─────────────────────────────────────────────────────
    @property
    def triage_urgent_threshold(self) -> int:
        return self._getint("TRIAGE_URGENT_THRESHOLD", 65)

    @property
    def triage_flag_threshold(self) -> int:
        return self._getint("TRIAGE_FLAG_THRESHOLD", 30)

    # ── Risk weights ──────────────────────────────────────────────────────────
    @property
    def risk_weights(self) -> dict[str, int]:
        return DEFAULT_RISK_WEIGHTS


settings = _Settings()
