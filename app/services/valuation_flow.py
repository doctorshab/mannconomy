from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timezone

# Import your actual math functions, LLM client, and schemas
from app.services.valuation_math import compute_price_estimate, compute_confidence, check_lowball
from app.services.llm_client import generate_valuation_narrative
from app.schemas.valuation import ValuationResponse

# Import your retrieval function from Phase 2
from app.core.retrive import retrieve_comps 
from app.schemas.valuation import ValuationResponse, PriceEstimate, Confidence, LowballCheck

def build_valuation_prompt(
    item_name: str, 
    price_estimate: dict,
    confidence: dict,
    comps: List[dict], 
    lowball_data: Optional[dict] = None
) -> str:
    """Builds the strict text prompt to feed to the LLM."""
    
    # Format the comps into a readable list for the prompt
    comps_text = "\n".join([
        f"- ID {comp['id']}: Sold for {comp['price_in_ref']} ref (Match Score: {comp['soft_match_score']}%)"
        for comp in comps
    ])

    prompt = f"""
    You are an expert Team Fortress 2 economy app backend. 
    Analyze the following data and generate a structured JSON valuation response.
    
    Item Requested: {item_name}
    
    Calculated Point Value: {price_estimate['point']} ref
    Calculated Low Bound: {price_estimate['low']} ref
    Calculated High Bound: {price_estimate['high']} ref
    
    Comps found in database:
    {comps_text}
    
    Confidence Info:
    Tier: {confidence['tier']}
    Score: {confidence['score']}
    """

    # If the user provided an offer, feed the deterministic lowball math to the LLM
    if lowball_data:
        prompt += f"\nUser is asking if an offer of {lowball_data['candidate_price']} ref is a good deal.\n"
        if lowball_data['is_lowball']:
            prompt += f"MATH SYSTEM FLAG: This IS a lowball (Discount: {lowball_data['discount_percentage']}%). Explain why they should reject it."
        else:
            prompt += f"MATH SYSTEM FLAG: This is NOT a lowball (Discount: {lowball_data['discount_percentage']}%). It is a fair offer."

    return prompt



def execute_valuation_pipeline(db_session: Session, req_item: dict, user_offer: Optional[float] = None) -> ValuationResponse:
    # STEP 1: Fetch real comps from your database!
    retrieval_result = retrieve_comps(db_session, req_item)
    
    if retrieval_result["status"] == "no_comps_found":
        raise ValueError(f"No comps found for item {req_item.get('item_id')}. Cannot value item.")

   
    KEY_PRICE_IN_REF = 70.0 

    formatted_comps = []
    for item in retrieval_result["retrieved_comps"]:
        comp_obj = item["comp"]
        
       
        keys = float(getattr(comp_obj, 'price_keys', 0.0) or 0.0)
        metal = float(getattr(comp_obj, 'price_metal', 0.0) or 0.0)
        
        total_price_in_ref = (keys * KEY_PRICE_IN_REF) + metal
        
        formatted_comps.append({
            "id": comp_obj.id,
            "price_in_ref": total_price_in_ref, 
            "date": datetime.fromtimestamp(comp_obj.transaction_timestamp, tz=timezone.utc),
            "soft_match_score": item["score"]
        })
    # -----------------------

    # STEP 2: Run the deterministic math step-by-step
    price_estimate = compute_price_estimate(formatted_comps)
    
    # ... (The rest of the function remains exactly the same!) ...
    
    confidence = compute_confidence(
        comps=formatted_comps,
        point_estimate=price_estimate["point"],
        low=price_estimate["low"],
        high=price_estimate["high"]
    )
    
    lowball_data = None
    if user_offer is not None:
        lowball_data = check_lowball(price_estimate["point"], user_offer)
    
    # STEP 3: Build the prompt using the calculated data
    item_name_placeholder = f"Item ID {req_item.get('item_id')}" 
    prompt = build_valuation_prompt(
        item_name=item_name_placeholder, 
        price_estimate=price_estimate, 
        confidence=confidence, 
        comps=formatted_comps, 
        lowball_data=lowball_data
    )
    
    # STEP 4: Get the strict JSON response from Gemini
    final_response = generate_valuation_narrative(prompt)
 
    warnings = list(final_response.warnings or [])
 
    # --- Echo check: did the LLM's copy of our numbers drift? (signal only) ---
    def _mismatch(a: float, b: float, rel_tol: float = 0.02, abs_tol: float = 0.05) -> bool:
        return abs(a - b) > max(abs_tol, rel_tol * max(abs(a), abs(b), 1e-9))
 
    if _mismatch(final_response.price_estimate.point, price_estimate["point"]):
        warnings.append("llm_price_echo_mismatch")
    if abs(final_response.confidence.score - confidence["score"]) > 0.05:
        warnings.append("llm_confidence_echo_mismatch")
    if lowball_data and final_response.lowball_check:
        if _mismatch(final_response.lowball_check.discount_percentage, lowball_data["discount_percentage"]):
            warnings.append("llm_lowball_echo_mismatch")
 
    # --- Authoritative overwrite: Python's numbers always win ---
    final_response.item_id = req_item.get("item_id")
    final_response.price_estimate = PriceEstimate(**price_estimate)
    final_response.confidence = Confidence(**confidence)
 
    # comps_used must be a real subset of what was actually retrieved
    valid_comp_ids = {c["id"] for c in formatted_comps}
    cited = [cid for cid in final_response.comps_used if cid in valid_comp_ids]
    if not cited:
        cited = [c["id"] for c in formatted_comps]
        warnings.append("llm_comps_used_invalid_fallback_to_full_pool")
    final_response.comps_used = cited
 
    if lowball_data is None:
        final_response.lowball_check = None
    else:
        # Keep the LLM's explanation text (narration is its job) but the
        # numbers come straight from check_lowball(), never from the model.
        explanation = (
            final_response.lowball_check.explanation
            if final_response.lowball_check and final_response.lowball_check.explanation
            else ("This offer falls below the fair-value threshold for this item's price band."
                  if lowball_data["is_lowball"] else
                  "This offer is within the fair-value range for this item's price band.")
        )
        final_response.lowball_check = LowballCheck(
            requested=True,
            candidate_price=lowball_data["candidate_price"],
            discount_percentage=lowball_data["discount_percentage"],
            is_lowball=lowball_data["is_lowball"],
            explanation=explanation,
        )
 
    final_response.warnings = warnings
 
    return final_response