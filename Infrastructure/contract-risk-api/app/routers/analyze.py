"""POST /analyze — score a contract."""
from __future__ import annotations
import logging
from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import AnalyzeRequest, AnalyzeResponse
from app.services.scorer import ScoringService, get_scoring_service

logger = logging.getLogger("contract_risk.router")
router = APIRouter(prefix="/analyze", tags=["Analysis"])


@router.post(
    "",
    response_model=AnalyzeResponse,
    summary="Analyze a contract",
    description=(
        "Runs all 41 CUAD clause questions against the contract text. "
        "Returns risk score 0–100, triage recommendation, and extracted "
        "text for every detected clause sorted by business impact."
    ),
    responses={
        422: {"description": "Validation error — text too short or missing"},
        503: {"description": "Model not available"},
    },
)
async def analyze(
    body: AnalyzeRequest,
    service: ScoringService = Depends(get_scoring_service),
) -> AnalyzeResponse:
    try:
        return service.analyze(body.text, threshold=body.threshold)
    except Exception as exc:
        logger.exception("Scoring error: %s", exc)
        raise HTTPException(status_code=503, detail=str(exc))
