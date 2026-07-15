from app.core.weights import WEIGHTS


def score_wear_float( req_float, comp_float, weight):
    if req_float is None and comp_float is None:
        return weight
    if req_float is None or comp_float is None:
        return 0
    result = weight * (1 - abs(req_float - comp_float))
    return result


def score_list_overlap(req_list,comp_list,weight):
    if len(req_list) ==0 and len(comp_list)==0:
        return weight
    elif len(req_list)==0:
        return 0

    req_set = set(req_list)
    comp_set = set(comp_list)
    same_attributes = req_set & comp_set
    score = (len(same_attributes) * weight) / len(req_set)
    return score


def score_comp(req_item, comp_item):
    total_score =0

    total_score+=score_wear_float(req_item.get("wear_float"),comp_item.wear_float,WEIGHTS["wear_float"])

    comp_spell_ids = [s.spell_id for s in comp_item.spells]
    req_spell_ids=req_item.get("spells",[])
    total_score+=score_list_overlap(req_spell_ids,comp_spell_ids,WEIGHTS["spells"])

    comp_strange_parts_ids=[s.strange_part_id for s in comp_item.strange_parts]
    req_strange_parts_ids=req_item.get("strange_parts",[])
    total_score+=score_list_overlap(req_strange_parts_ids,comp_strange_parts_ids,WEIGHTS["strange_parts"])

    if req_item.get("unusual_effect_id") == comp_item.unusual_effect_id:
        total_score += WEIGHTS["unusual_effect_id"]
        
    if req_item.get("paint_id") == comp_item.paint_id:
        total_score += WEIGHTS["paint_id"]
        
    if req_item.get("war_paint_id") == comp_item.war_paint_id:
        total_score += WEIGHTS["war_paint_id"]
        
    if req_item.get("botkiller_tier_id") == comp_item.botkiller_tier_id:
        total_score += WEIGHTS["botkiller_tier_id"]
        
    if req_item.get("pattern_seed") == comp_item.pattern_seed:
        total_score += WEIGHTS["pattern_seed"]
        
    if req_item.get("killstreak_tier_id") == comp_item.killstreak_tier_id:
        total_score += WEIGHTS["killstreak_tier_id"]
        
    if req_item.get("sheen_id") == comp_item.sheen_id:
        total_score += WEIGHTS["sheen_id"]  
        
    if req_item.get("killstreaker_id") == comp_item.killstreaker_id:
        total_score += WEIGHTS["killstreaker_id"]
        
    if req_item.get("grade_id") == comp_item.grade_id:
        total_score += WEIGHTS["grade_id"]
        
    if req_item.get("holiday_restriction_id") == comp_item.holiday_restriction_id:
        total_score += WEIGHTS["holiday_restriction_id"]
        
    if req_item.get("collection_id") == comp_item.collection_id:
        total_score += WEIGHTS["collection_id"]

    if req_item.get("is_festivized", False) == comp_item.is_festivized:
        total_score += WEIGHTS["is_festivized"]
    
    return total_score