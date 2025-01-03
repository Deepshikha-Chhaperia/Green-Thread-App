import sqlite3

def update_database_schema():
    conn = sqlite3.connect('greenthreads.db')
    c = conn.cursor()

    # Update designs table
    c.execute("PRAGMA table_info(designs)")
    existing_columns = set(col[1] for col in c.fetchall())

    required_columns = ['id', 'user_id', 'style', 'materials', 'clothing_type', 'production_method', 'custom_design', 'tryon_image', 'timestamp', 'recycling_instructions', 'carbon_footprint', 
                                          'zero_waste_pattern', 'eco_dyes', 'durability_improvements', 'eco_packaging', 'sustainability_score','water_saved','co2_reduced', 'waste_reduced', 'energy_saved',
                                          'water_usage', 'co2_emissions', 'waste_generated', 'energy_consumption', 'packaging','production_location','shipping_method','base_color','qr_code_id','care_instructions']

    for column in required_columns:
        if column not in existing_columns:
            try:
                c.execute(f"ALTER TABLE designs ADD COLUMN {column} TEXT")
                print(f"Added {column} column to designs table")
            except sqlite3.OperationalError as e:
                print(f"Error adding {column} column: {e}")

    # Create recycling_instructions table
    c.execute('''CREATE TABLE IF NOT EXISTS recycling_instructions
                 (id INTEGER PRIMARY KEY,
                  qr_url TEXT UNIQUE,
                  instructions TEXT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    print("Created recycling_instructions table")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    update_database_schema()