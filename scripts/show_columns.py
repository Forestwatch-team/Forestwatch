from src.database import db

with db.get_connection() as conn:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name IN ('fire_alerts', 'forest_loss', 'validation_logs')
            ORDER BY table_name, ordinal_position
        """)
        for table, col, typ in cur.fetchall():
            print(f"{table:16} {col:25} {typ}")