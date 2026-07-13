import mysql.connector

# 1. The Comprehensive Data Lists
PAINTS = [
    "A Color Similar to Slate", "A Deep Commitment to Purple", "A Distinctive Lack of Hue",
    "A Mann's Mint", "After Eight", "Aged Moustache Grey", "An Air of Debonair",
    "An Extraordinary Abundance of Tinge", "Australium Gold", "Balaclavas Are Forever",
    "Color No. 216-190-216", "Cream Spirit", "Dark Salmon Injustice", "Indubitably Green",
    "Mann Co. Orange", "Mocha Drop", "Muskelmannbraun", "Noble Hatter's Violet",
    "Operator's Overalls", "Peculiarly Drab Tincture", "Pink as Hell", "Radigan Conagher Brown",
    "Team Spirit", "The Bitter Taste of Defeat and Lime", "The Color of a Gentlemann's Business Pant",
    "The Value of Teamwork", "Waterlogged Lab Coat", "Ye Olde Rustic Colour", "Zepheniah's Greed"
]

COLLECTIONS = [
    "The Concealed Killer Collection", "The Craftsman Collection", "The Teufort Collection",
    "The Pyroland Collection", "The Warbird Collection", "The Gentlemann's Collection",
    "The Harvest Collection", "The Macabre Web Collection", "The Gargoyle Collection",
    "The Mayflower Collection", "The Jungle Jackpot Collection", "The Infernal Reward Collection",
    "The Decorated Tanker Collection", "The Contract Campaigner Collection", "The Saxton Select Collection",
    "The Scream Fortress IX Collection", "The Jungle Inferno Collection", "The Winter 2017 Collection",
    "The Scream Fortress X Collection", "The Winter 2019 Collection", "The Scream Fortress XII Collection",
    "The Winter 2020 Collection"
]

# A robust list covering standard, high-tier, and blood-money war paints
WAR_PAINTS = [
    "Macabre Web", "Nutcracker", "Autumn", "Bovine Blazemaker", "Night Owl", "Civic Duty",
    "Miami Element", "Jazzy", "Hazard Warning", "Coffin Nail", "High Roller's", "Warhawk",
    "Blitzkrieg", "Corsair", "Airwolf", "Bomber Soul", "Uranium", "Roar", "Backwoods Boomstick",
    "Iron Wood", "Plaid Potshotter", "Shot in the Dark", "Alien Tech", "Dragon Slayer",
    "Park Pigmented", "Sax Wax", "Yeti Coated", "Crocodile Munitions", "Macaw Masked",
    "Piñata", "Star Crossed", "Clover Camo'd", "Kill Covered", "Fire Glazed", "Blood Swept",
    "Night Terror", "Woodsy Widowmaker", "Woodland Warrior", "Wrapped Reviver", "Forest Fire"
]

def seed_database():
    try:
        # 2. Connect to the Database
        # Update your password here if you set one for your 'divya' user
        conn = mysql.connector.connect(
            host="localhost",
            user="divya", 
            password="",  
            database="mannconomy_db"
        )
        cursor = conn.cursor()

        # 3. Seed Paints
        print("Seeding Paints...")
        for paint in PAINTS:
            # IGNORE prevents the script from crashing if the row already exists
            cursor.execute("INSERT IGNORE INTO paints (name) VALUES (%s)", (paint,))
        
        # 4. Seed Collections
        print("Seeding Collections...")
        for collection in COLLECTIONS:
            cursor.execute("INSERT IGNORE INTO collections (name) VALUES (%s)", (collection,))

        # 5. Seed War Paints
        print("Seeding War Paints...")
        for war_paint in WAR_PAINTS:
            cursor.execute("INSERT IGNORE INTO war_paints (name) VALUES (%s)", (war_paint,))

        # Commit all the changes to the database
        conn.commit()
        print("Success! All paints, collections, and war paints have been seeded.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    seed_database()