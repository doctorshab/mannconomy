from typing import List, Dict, Any, Tuple
from datetime import datetime, timezone
import math

# --- 1. PRICE ESTIMATION (Weighted Percentiles) ---

def _weighted_percentile(data: List[Tuple[float, float]], percentile: float) -> float:
    """
    Helper to calculate a weighted percentile. 
    data is a list of tuples: (price_in_ref, soft_match_score)
    """
    if not data:
        return 0.0
        
    # Sort by price ascending
    data.sort(key=lambda x: x[0])
    total_weight = sum(weight for _, weight in data)
    
    if total_weight == 0:
        # Fallback if all weights are 0 (shouldn't happen with valid Phase 2 output)
        return data[len(data)//2][0]

    target = total_weight * percentile
    cumulative_weight = 0.0
    
    for price, weight in data:
        cumulative_weight += weight
        if cumulative_weight >= target:
            return float(round(price, 2))
            
    return float(round(data[-1][0], 2))

def compute_price_estimate(comps: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Calculates the point estimate (weighted median) and range (weighted P25/P75).
    Expects comps to have 'price_in_ref' and 'soft_match_score'.
    """
    data = [(comp['price_in_ref'], comp['soft_match_score']) for comp in comps]
    
    point = _weighted_percentile(data, 0.50) # 50th percentile = median
    low = _weighted_percentile(data, 0.25)   # 25th percentile
    high = _weighted_percentile(data, 0.75)  # 75th percentile
    
    return {
        "point": point,
        "low": low,
        "high": high
    }


# --- 2. CONFIDENCE SCORING ---
# app/services/valuation_math.py

# --- 2. CONFIDENCE SCORING ---

def compute_confidence(comps: List[Dict[str, Any]], point_estimate: float, low: float, high: float) -> Dict[str, Any]:
    """
    Computes confidence tier and score based on sample size, recency, dispersion, and match quality.
    """
    comp_count = len(comps)
    
    if comp_count <= 2:
        return {"tier": "Low", "score": 0.30, "comp_count": comp_count}

    # 1. Sample Size (diminishing returns after ~10 comps)
    target_sample_size = 10.0
    score_size = min(comp_count / target_sample_size, 1.0)
    
    # 2. Match Quality (average soft score)
    score_match = sum(comp['soft_match_score'] for comp in comps) / comp_count
    
    # 3. Price Dispersion (tighter spread = higher confidence)
    # Zero guard: if point_estimate is 0, we can't calculate relative spread safely
    if point_estimate <= 0:
        score_dispersion = 0.0
    else:
        spread_ratio = (high - low) / point_estimate
        score_dispersion = max(0.0, 1.0 - spread_ratio)
    
    # 4. Recency (decay over 90 days)
    now = datetime.now(timezone.utc)
    avg_age_days = sum((now - comp['date']).days for comp in comps) / comp_count
    score_recency = max(0.0, 1.0 - (avg_age_days / 90.0))

    # Combine weights
    combined_score = (
        (score_size * 0.25) + 
        (score_match * 0.25) + 
        (score_dispersion * 0.25) + 
        (score_recency * 0.25)
    )
    
    combined_score = round(combined_score, 2)

    # Determine Tier
    if combined_score >= 0.75:
        tier = "High"
    elif combined_score >= 0.40:
        tier = "Medium"
    else:
        tier = "Low"

    return {
        "tier": tier,
        "score": combined_score,
        "comp_count": comp_count
    }


# --- 3. LOWBALL DETECTION ---

def check_lowball(point_estimate: float, candidate_price: float) -> Dict[str, Any]:
    """
    Determines if an offer is a lowball using a tiered threshold based on item value.
    Guards against zero values safely.
    """
    # Guard against 0 or negative base price point estimates to prevent division by zero
    if point_estimate <= 0:
        return {
            "requested": True,
            "candidate_price": candidate_price,
            "discount_percentage": 0.0,
            "is_lowball": True,
            "explanation": "Item has an invalid or zero market valuation base, making offer assessment impossible."
        }

    discount_percentage = ((point_estimate - candidate_price) / point_estimate) * 100.0
    discount_percentage = round(discount_percentage, 2)
    
    # Tiered thresholds
    if point_estimate < 10.0:
        threshold = 20.0  
    elif point_estimate <= 50.0:
        threshold = 15.0
    elif point_estimate <= 200.0:
        threshold = 10.0
    else:
        threshold = 5.0   
        
    is_lowball = discount_percentage >= threshold
    
    return {
        "requested": True,
        "candidate_price": candidate_price,
        "discount_percentage": discount_percentage,
        "is_lowball": is_lowball
    }