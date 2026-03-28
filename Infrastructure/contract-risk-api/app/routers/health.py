"""GET /health  and  GET /clauses"""
from __future__ import annotations
from fastapi import APIRouter, Depends
from app.models.schemas import HealthResponse, ClausesResponse, ClauseInfo
from app.services.scorer import ScoringService, get_scoring_service, CLAUSE_TYPES
from app.core.config import settings

health_router  = APIRouter(tags=["Operations"])
clauses_router = APIRouter(prefix="/clauses", tags=["Clauses"])

_DESCRIPTIONS: dict[str, str] = {
    "Uncapped Liability":               "Clauses where liability is explicitly not limited.",
    "Cap On Liability":                 "Maximum liability cap provisions.",
    "Ip Ownership Assignment":          "Assigns IP ownership to a party.",
    "Joint Ip Ownership":               "Shared IP ownership between parties.",
    "Change Of Control":                "Provisions triggered by acquisition or ownership change.",
    "Liquidated Damages":               "Pre-specified damages for breach.",
    "Anti-Assignment":                  "Restrictions on assigning the contract.",
    "Source Code Escrow":               "Requires depositing source code with a third party.",
    "Non-Compete":                      "Restricts competitive activity post-termination.",
    "Audit Rights":                     "Rights to audit the other party's records.",
    "Covenant Not To Sue":              "Agreement not to bring legal action.",
    "Most Favored Nation":              "Guarantees best available pricing or terms.",
    "Irrevocable Or Perpetual License": "License grants that cannot be revoked.",
    "Unlimited/All-You-Can-Eat-License":"Unlimited usage license grants.",
    "Termination For Convenience":      "Right to terminate without cause.",
    "Exclusivity":                      "Exclusive dealings provisions.",
    "Rofr/Rofo/Rofn":                   "Right of first refusal / offer / negotiation.",
    "Revenue/Profit Sharing":           "Revenue or profit sharing arrangements.",
    "Competitive Restriction Exception":"Exceptions to competitive restriction clauses.",
    "Minimum Commitment":               "Minimum purchase or volume commitments.",
    "Volume Restriction":               "Restrictions on usage or purchase volume.",
    "Price Restrictions":               "Restrictions on pricing adjustments.",
    "Non-Disparagement":                "Prohibition on disparaging the other party.",
    "No-Solicit Of Employees":          "Restriction on soliciting the other party's employees.",
    "No-Solicit Of Customers":          "Restriction on soliciting the other party's customers.",
    "Warranty Duration":                "Duration of warranty periods.",
    "Insurance":                        "Required insurance coverage provisions.",
    "Post-Termination Services":        "Obligations after termination.",
    "Third Party Beneficiary":          "Rights granted to third parties.",
    "Affiliate License-Licensee":       "License rights extended to licensee affiliates.",
    "Affiliate License-Licensor":       "License rights extended to licensor affiliates.",
    "Non-Transferable License":         "Licenses that cannot be transferred.",
    "License Grant":                    "Core license grant provisions.",
    "Renewal Term":                     "Contract renewal terms.",
    "Notice Period To Terminate Renewal":"Notice required to prevent auto-renewal.",
    "Expiration Date":                  "Contract expiration date.",
    "Effective Date":                   "Date the contract takes effect.",
    "Agreement Date":                   "Date the contract was signed.",
    "Governing Law":                    "Jurisdiction and governing law.",
    "Parties":                          "Parties to the agreement.",
    "Document Name":                    "Name or title of the contract.",
}


@health_router.get("/health", response_model=HealthResponse, summary="Liveness check")
async def health(svc: ScoringService = Depends(get_scoring_service)) -> HealthResponse:
    return HealthResponse(
        status="ok",
        model_loaded=True,
        model_type="roberta-qa" if svc.is_neural else "lr-tfidf-fallback",
        version=settings.version,
    )


@clauses_router.get(
    "",
    response_model=ClausesResponse,
    summary="List all 41 supported clause types",
)
async def list_clauses() -> ClausesResponse:
    items = sorted(
        [
            ClauseInfo(
                name=ct,
                risk_weight=settings.risk_weights.get(ct, 3),
                description=_DESCRIPTIONS.get(ct, ""),
            )
            for ct in CLAUSE_TYPES
        ],
        key=lambda x: -x.risk_weight,
    )
    return ClausesResponse(clauses=items, total=len(items))
