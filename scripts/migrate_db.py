import sqlite3
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def migrate():
    db_path = config.DB_PATH
    if not os.path.exists(db_path):
        print("No database found to migrate.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check existing columns
    cursor.execute("PRAGMA table_info(traffic_results)")
    columns = [row[1] for row in cursor.fetchall()]
    
    new_cols = [
        ("avg_speed", "TEXT"),
        ("flow_rate", "INTEGER"),
        ("density", "REAL"),
        ("total_lane_changes", "INTEGER"),
        ("fps", "TEXT"),
        ("latency", "TEXT"),
        ("predicted_count", "INTEGER"),
        ("predicted_congestion", "TEXT")
    ]
    
    for col_name, col_type in new_cols:
        if col_name not in columns:
            print(f"Adding column {col_name}...")
            cursor.execute(f"ALTER TABLE traffic_results ADD COLUMN {col_name} {col_type}")
            
    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
