from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List

# Import your pipeline
from app.services.valuation_flow import execute_valuation_pipeline
from app.schemas.valuation import ValuationResponse


from app.db.session import get_db 

app = FastAPI(title="TF2 Valuation API")


class ValuationRequest(BaseModel):
    # --- Hard filters (gate the candidate pool entirely) ---
    item_id: int = Field(..., description="The base asset defindex/item ID")
    is_australium: bool = Field(default=False, description="Is the item an Australium variant?")
    is_craftable: bool = Field(default=True, description="Is the item craftable?")
    quality_id: int = Field(default=6, description="TF2 Quality ID (e.g., 6 for Unique, 11 for Strange, 5 for Unusual)")

    unusual_effect_id: Optional[int] = Field(default=None, description="Unusual particle effect ID, if applicable")
    paint_id: Optional[int] = Field(default=None, description="Paint can color ID, if applicable")
    war_paint_id: Optional[int] = Field(default=None, description="War Paint / Decorated skin ID, if applicable")
    botkiller_tier_id: Optional[int] = Field(default=None, description="Botkiller tier ID, if applicable")
    wear_float: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Wear float 0.0-1.0, for War Paints")
    pattern_seed: Optional[int] = Field(default=None, description="War Paint pattern seed, if applicable")
    killstreak_tier_id: Optional[int] = Field(default=None, description="Killstreak tier ID (None/Basic/Specialized/Professional)")
    sheen_id: Optional[int] = Field(default=None, description="Killstreak sheen ID (Specialized+ only)")
    killstreaker_id: Optional[int] = Field(default=None, description="Killstreaker effect ID (Professional only)")
    grade_id: Optional[int] = Field(default=None, description="Collector's item grade ID, if applicable")
    holiday_restriction_id: Optional[int] = Field(default=None, description="Holiday restriction ID, if applicable")
    collection_id: Optional[int] = Field(default=None, description="Collection ID, if applicable")
    is_festivized: bool = Field(default=False, description="Is the item Festivized?")
    spells: List[int] = Field(default_factory=list, description="List of spell IDs on the item")
    strange_parts: List[int] = Field(default_factory=list, description="List of strange part IDs on the item")

    user_offer: Optional[float] = Field(default=None, description="Optional candidate price to evaluate for lowballing")

@app.get("/")
def read_root():
    return {"message": "TF2 Valuation API is running! 🚀 Go to /docs to test it."}

@app.post("/api/v1/valuation", response_model=ValuationResponse)
def get_item_valuation(
    request: ValuationRequest, 
    db: Session = Depends(get_db)
):
    try:
        # 1. Convert the Pydantic request to a flat dictionary
        req_item = request.model_dump()
        
        # 2. Extract user_offer out since your pipeline expects it as a separate argument
        user_offer = req_item.pop("user_offer", None)
        
        # 3. req_item now contains the 4 hard filters plus all soft-match
        #    attributes score_comp() uses for ranking within the pool.
        result = execute_valuation_pipeline(
            db_session=db, 
            req_item=req_item, 
            user_offer=user_offer
        )
        return result
        
    except ValueError as e:
        # Catch the "No comps found" edge case safely
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # Catch unexpected pipeline/LLM exceptions
        raise HTTPException(status_code=500, detail=str(e))