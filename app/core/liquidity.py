from datetime import datetime, timezone

def compute_liquidity(pool_size, most_recent_timestamp):
    # Guard clause: if there are no comps, it's instantly Low liquidity.
    if not most_recent_timestamp or most_recent_timestamp == 0:
        return "Low"
        
    now = datetime.now(timezone.utc)
    comp_time = datetime.fromtimestamp(most_recent_timestamp, tz=timezone.utc)
    age = (now - comp_time).days

    if pool_size >= 5 and age <= 30:
        return "High"
    elif pool_size >= 2 and age <= 90:
        return "Medium"
    else:
        return "Low"