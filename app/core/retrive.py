from sqlalchemy.orm import Session
from datetime import datetime
from app.db.models import PriceComp
from app.core.score import score_comp
from sqlalchemy.orm import joinedload, selectinload
from datetime import datetime, timezone
from app.core.liquidity import compute_liquidity


def retrieve_comps(db_session, req_item):
    # 1. The Hard Filter (Identity Pillars)
    query = db_session.query(PriceComp).filter(
        PriceComp.item_id == req_item["item_id"],
        PriceComp.is_australium == req_item["is_australium"],
        PriceComp.is_craftable == req_item["is_craftable"],
        PriceComp.quality_id == req_item["quality_id"],
    )
    
    # 2. Eager Loading (One relationship per call!)
    query = query.options(
        # joinedload for Many-to-One relationships (Standard SQL JOINs)
        joinedload(PriceComp.unusual_effect),
        joinedload(PriceComp.paint),
        joinedload(PriceComp.war_paint),
        joinedload(PriceComp.botkiller_tier),
        joinedload(PriceComp.killstreak_tier),
        joinedload(PriceComp.sheen),
        joinedload(PriceComp.killstreaker),
        joinedload(PriceComp.grade),
        joinedload(PriceComp.collection),
        joinedload(PriceComp.holiday_restriction),
        
        # selectinload for Many-to-Many relationships (Smart batch queries)
        selectinload(PriceComp.spells),
        selectinload(PriceComp.strange_parts)
    )
    
    # 3. Execute the query
    candidate_pool = query.all()
    if not candidate_pool :
        return {
            "status": "no_comps_found",
            "retrieved_comps": [],
            "liquidity_score": 0,
            "candidate_pool_size": 0
        }
    

    scored_comps =[]
    most_recent_timestamp=0
    pool_size=len(candidate_pool)


    for comp_item in candidate_pool:
        item_score=score_comp(req_item, comp_item)
        scored_comps.append({"comp":comp_item,"score":item_score})
        most_recent_timestamp=max(most_recent_timestamp,comp_item.transaction_timestamp)
    
    scored_comps.sort(key=lambda x: x["score"], reverse=True)
    scored_comps=scored_comps[:8]
    
    liquidity = compute_liquidity(pool_size, most_recent_timestamp)

    # The final return
    return {
        "status": "success",
        "retrieved_comps": scored_comps, # Your top 8 list
        "liquidity_score": liquidity,
        "candidate_pool_size": pool_size
    }