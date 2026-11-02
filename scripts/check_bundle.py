from src.database import queries

meta = queries.load_meta_bundle()
print("keys:", sorted(meta.keys()))
for k, v in meta.items():
    print(k, "->", list(v.columns), len(v), "rows")