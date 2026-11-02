import time
from datetime import timedelta

import pandas as pd

from src.database import queries

t0 = time.time()
rng = queries.fire_date_range()
min_day = pd.to_datetime(rng.loc[0, "min_day"]).date()
max_day = pd.to_datetime(rng.loc[0, "max_day"]).date()
start = max(min_day, max_day - timedelta(days=90))
print(f"date range: {min_day} to {max_day}")

classes = list(queries.fire_confidence_values()["confidence"])
print("confidence values:", classes)

t = time.time()
daily = queries.fire_daily_counts(start, max_day, classes)
print(f"daily counts: {len(daily)} rows, {time.time() - t:.1f}s")

t = time.time()
points = queries.fire_points(start, max_day, classes)
print(f"map points: {len(points)} rows, {time.time() - t:.1f}s")

print(f"TOTAL: {time.time() - t0:.1f}s")