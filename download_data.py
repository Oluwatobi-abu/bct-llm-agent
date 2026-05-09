import requests
import os

os.makedirs("data", exist_ok=True)

print("Downloading Amazon Gift Cards reviews...")

# Direct parquet file from Hugging Face
url = "https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023/resolve/main/raw/review_categories/Gift_Cards.jsonl"

headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get(url, headers=headers, stream=True)

if response.status_code == 200:
    with open("data/gift_cards_reviews.jsonl", "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print("Download complete!")
else:
    print(f"Failed with status code: {response.status_code}")
    print("Trying backup method...")

    # Backup - create sample data to keep moving
    import json
    sample_reviews = [
        {"user_id": "U001", "asin": "B001E4KFG0", "rating": 5.0, "text": "Great gift card, easy to use and recipient loved it!", "title": "Perfect gift"},
        {"user_id": "U001", "asin": "B002L3XLBO", "rating": 4.0, "text": "Good value, delivered instantly to email.", "title": "Good product"},
        {"user_id": "U002", "asin": "B001E4KFG0", "rating": 3.0, "text": "Okay gift card but took long to arrive.", "title": "Average"},
        {"user_id": "U002", "asin": "B003AVKOP2", "rating": 5.0, "text": "Excellent! Bought for my friend and she was happy.", "title": "Loved it"},
        {"user_id": "U003", "asin": "B002L3XLBO", "rating": 2.0, "text": "Did not work at first, had to call support.", "title": "Frustrating"},
        {"user_id": "U003", "asin": "B003AVKOP2", "rating": 4.0, "text": "Nice gift option, will buy again.", "title": "Good"},
    ]
    with open("data/gift_cards_reviews.jsonl", "w") as f:
        for review in sample_reviews:
            f.write(json.dumps(review) + "\n")
    print("Created sample data to keep building!")