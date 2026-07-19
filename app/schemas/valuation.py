from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class PriceEstimate(BaseModel):
    point: float = Field(..., description="Deterministically computed point estimate in ref")
    low: float = Field(..., description="Lower bound of the estimate range")
    high: float = Field(..., description="Upper bound of the estimate range")
    currency: Literal["ref"] = Field(default="ref", description="Canonical currency unit")

class Confidence(BaseModel):
    tier: Literal["High", "Medium", "Low"] = Field(..., description="Deterministic confidence tier")
    score: float = Field(..., ge=0.0, le=1.0, description="0-1 normalized confidence score")
    comp_count: int = Field(..., description="Total number of comps in the math pool")

class LowballCheck(BaseModel):
    requested: bool = Field(default=True)
    candidate_price: float
    discount_percentage: float
    is_lowball: bool
    explanation: str = Field(..., description="Short explanation grounded in the provided comps")

class ValuationResponse(BaseModel):
    item_id: int
    price_estimate: PriceEstimate
    confidence: Confidence
    comps_used: List[int] = Field(..., description="Subset of comp IDs actually shown to and citable by the LLM")
    narrative: str = Field(..., description="Explanation citing specific comps by id, price, and date")
    lowball_check: Optional[LowballCheck] = Field(default=None, description="Omitted when no candidate price is given")
    warnings: List[str] = Field(default_factory=list, description="Warnings like 'low_comp_count' or 'narrative_unavailable'")