import json
import pandas as pd

reviews = []
with open("data/gift_cards_reviews.jsonl", "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if i >= 100:  # just look at first 100 rows
            break
        reviews.append(json.loads(line.strip()))

df = pd.DataFrame(reviews)

print("=== SHAPE ===")
print(f"{len(df)} rows, {len(df.columns)} columns")

print("\n=== COLUMNS ===")
print(df.columns.tolist())

print("\n=== SAMPLE REVIEW ===")
print(json.dumps(reviews[0], indent=2))

print("\n=== RATINGS DISTRIBUTION ===")
print(df['rating'].value_counts().sort_index())