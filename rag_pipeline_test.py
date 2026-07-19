import json
import time
from datetime import datetime, timezone, timedelta

# Adjust these imports based on your actual project structure!
from app.db.session import SessionLocal
from app.db.models import Item, Quality, PriceComp
# Assuming you put score_comp and compute_liquidity in these files:
from app.core.score import score_comp
from app.core.liquidity import compute_liquidity
from sqlalchemy.exc import IntegrityError

def seed_test_data(db):
    print("--- Seeding Database ---")
    
    # 1. Create a dummy item (Bulletproof method)
    item = db.query(Item).filter_by(base_name="Rocket Launcher").first()
    if not item:
        try:
            item = Item(base_name="Rocket Launcher", item_class="weapon", defindex=18)
            db.add(item)
            db.commit()
            db.refresh(item)
            print(f"Created Item: {item.base_name} (ID: {item.id})")
        except IntegrityError:
            # If MySQL complains about duplicates, roll back the crash!
            db.rollback()
            # Just grab the very first item in the database, whatever it is named
            item = db.query(Item).first()
            print(f"Recovered conflicting existing Item: {item.base_name} (ID: {item.id})")
    else:
        print(f"Found existing Item: {item.base_name} (ID: {item.id})")

    # 2. Create a dummy quality (Bulletproof method)
    quality = db.query(Quality).filter_by(name="Strange").first()
    if not quality:
        try:
            quality = Quality(name="Strange")
            db.add(quality)
            db.commit()
            db.refresh(quality)
            print(f"Created Quality: {quality.name} (ID: {quality.id})")
        except IntegrityError:
            db.rollback()
            quality = db.query(Quality).first()
            print(f"Recovered conflicting existing Quality: {quality.name} (ID: {quality.id})")
    else:
        print(f"Found existing Quality: {quality.name} (ID: {quality.id})")

    # 3. Create Price Comps (Historical Sales)
    # Let's check if we already have comps for this item to avoid duplicates
    existing_comps = db.query(PriceComp).filter_by(item_id=item.id).count()
    if existing_comps == 0:
        now = datetime.now(timezone.utc)
        
        # Comp 1: Exact Match (Sold today)
        comp1 = PriceComp(
            item_id=item.id,
            quality_id=quality.id,
            is_australium=False,
            is_craftable=True,
            killstreak_tier_id=2, # Specialized
            wear_float=0.15,      # Field-Tested
            price_keys=2.0,
            price_metal=0.0,
            transaction_timestamp=int(now.timestamp()),
            listing_type="sell",
            source="backpack.tf", # Fixed: Added required source column
            external_id="test_comp_1"
        )
        
        # Comp 2: Partial Match (Wrong killstreak, slightly different float. Sold 10 days ago)
        comp2 = PriceComp(
            item_id=item.id,
            quality_id=quality.id,
            is_australium=False,
            is_craftable=True,
            killstreak_tier_id=1, # Standard Killstreak (Will lose points)
            wear_float=0.40,      # Well-Worn (Will lose points)
            price_keys=1.5,
            price_metal=0.0,
            transaction_timestamp=int((now - timedelta(days=10)).timestamp()),
            listing_type="sell",
            source="backpack.tf", # Fixed: Added required source column
            external_id="test_comp_2"
        )

        db.add_all([comp1, comp2])
        db.commit()
        print("Inserted 2 mock historical sales (PriceComps).")
    else:
        print("Mock PriceComps already exist, skipping seed.")
        
    # Return the actual DB IDs so our test uses the right ones!
    return item.id, quality.id


def test_retrieve_comps(req_item, db):
    print("\n--- Running Retrieval Pipeline ---")
    
    # 1. The Hard Filter (Phase 2, Steps 1 & 2)
    candidate_pool = db.query(PriceComp).filter(
        PriceComp.item_id == req_item["item_id"],
        PriceComp.quality_id == req_item["quality_id"],
        PriceComp.is_australium == req_item.get("is_australium", False),
        PriceComp.is_craftable == req_item.get("is_craftable", True)
    ).all()

    if not candidate_pool:
        return {"status": "failed", "message": "No comps found."}

    # 2. The Scoring Loop (Phase 2, Steps 3, 4, 5)
    scored_comps = []
    most_recent_timestamp = 0
    
    for comp_item in candidate_pool:
        # Call the function you built!
        item_score = score_comp(req_item, comp_item)
        
        # We store the comp ID and the score (converting ORM to dict for easy viewing)
        scored_comps.append({
            "comp_id": comp_item.id,
            "score": item_score,
            "price_keys": float(comp_item.price_keys) if comp_item.price_keys else 0.0
        })
        
        most_recent_timestamp = max(most_recent_timestamp, comp_item.transaction_timestamp)
    
    # Sort and truncate
    scored_comps.sort(key=lambda x: x["score"], reverse=True)
    scored_comps = scored_comps[:8]
    
    # 3. Calculate Liquidity (Phase 2, Step 6)
    pool_size = len(candidate_pool)
    liquidity = compute_liquidity(pool_size, most_recent_timestamp)

    return {
        "status": "success",
        "candidate_pool_size": pool_size,
        "liquidity_score": liquidity,
        "retrieved_comps": scored_comps
    }


if __name__ == "__main__":
    db = SessionLocal()
    
    try:
        # Seed the DB and get the ACTUAL database IDs
        actual_item_id, actual_quality_id = seed_test_data(db)
        
        # Create a mock frontend request for a Strange Specialized Killstreak Rocket Launcher (Field-Tested)
        requested_item = {
            "item_id": actual_item_id,
            "quality_id": actual_quality_id,
            "is_australium": False,
            "is_craftable": True,
            "killstreak_tier_id": 2, 
            "wear_float": 0.15,
            "spells": [],
            "strange_parts": []
        }
        
        print(f"\nSearching for: {requested_item}")
        
        # Run the pipeline
        result = test_retrieve_comps(requested_item, db)
        
        print("\n--- Pipeline Result ---")
        print(json.dumps(result, indent=4))
        
    finally:
        db.close()