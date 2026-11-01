import time

from src.database import queries

for name in ["table_counts", "fire_date_range", "fire_confidence_values", "loss_countries", "quality_summary"]:
    t = time.time()
    try:
        df = getattr(queries, name)()
        print(f"{name}: OK, {len(df)} rows, {time.time() - t:.1f}s")
    except Exception as e:
        print(f"{name}: FAILED after {time.time() - t:.1f}s -> {type(e).__name__}: {e}")