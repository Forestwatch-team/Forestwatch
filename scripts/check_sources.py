from src.database import db

with db.get_connection() as conn:
    with conn.cursor() as cur:
        cur.execute("""SELECT satellite, instrument, version, COUNT(*)
                       FROM fire_alerts GROUP BY 1, 2, 3 ORDER BY 4 DESC""")
        for row in cur.fetchall():
            print(row)
        cur.execute("""SELECT acq_date, COUNT(*) FROM fire_alerts
                       GROUP BY 1 ORDER BY 1""")
        for row in cur.fetchall():
            print(row)
        cur.execute("""SELECT COUNT(*) - COUNT(DISTINCT (latitude, longitude, acq_date, acq_time))
                       FROM fire_alerts""")
        print("possible duplicates:", cur.fetchone()[0])