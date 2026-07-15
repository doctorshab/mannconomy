from app.db.session import SessionLocal
from app.db.models import Item
session = SessionLocal()
try:
    results = session.query(Item).filter(Item.defindex == 900001).all()
    query = session.query(PriceComp).filter(PriceComp.item_id == 10,PriceComp.quality_id == requested.quality_id).options(joinedload(PriceComp.quality),selectinload(PriceComp.spells)).all()
    if not results:
        print("No items found with that defindex.")
    else:
        for item in results:
            print(f"Found Item: {item.base_name} | Class: {item.item_class} | Defindex: {item.defindex}")
finally:        
    # 5. CLOSE THE SESSION
    # We always do this in a 'finally' block so it closes even if the query crashes
    session.close()