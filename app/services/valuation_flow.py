from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timezone

# Import your actual math functions, LLM client, and schemas
from app.services.valuation_math import compute_price_estimate, compute_confidence, check_lowball
from app.services.llm_client import generate_valuation_narrative
from app.schemas.valuation import ValuationResponse

# Import your retrieval function from Phase 2
from app.core.retrive import retrieve_comps 

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
            "date": comp_obj.transaction_timestamp,
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
    
    # Ensure the item_id is injected correctly if the LLM missed it
    final_response.item_id = req_item.get("item_id") 

    return final_response