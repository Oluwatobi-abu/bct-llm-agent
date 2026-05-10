from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import json
import os
import requests
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="BCT Hackathon - LLM Review & Recommendation Agent")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/ui")
def ui():
    return FileResponse("static/index.html")


# ── Auto-download data on startup ─────────────────────────────
def ensure_data_exists():
    if not os.path.exists("data/gift_cards_reviews.jsonl"):
        os.makedirs("data", exist_ok=True)
        print("Downloading dataset...")
        url = "https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023/resolve/main/raw/review_categories/Gift_Cards.jsonl"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, stream=True)
        if response.status_code == 200:
            with open("data/gift_cards_reviews.jsonl", "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print("Dataset downloaded!")
        else:
            print("Using backup sample data...")
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

# Run on startup
ensure_data_exists()
# ── Input shapes ──────────────────────────────────────────────

class ReviewRequest(BaseModel):
    user_id: str
    product_name: str
    product_description: str

class RecommendRequest(BaseModel):
    user_id: str
    category: str = "Gift Cards"


# ── Helpers ───────────────────────────────────────────────────
def load_user_reviews(user_id, max_reviews=10):
    reviews = []
    with open("data/gift_cards_reviews.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            review = json.loads(line.strip())
            if review["user_id"] == user_id:
                reviews.append(review)
            if len(reviews) >= max_reviews:
                break
    return reviews


def call_groq(prompt):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=500
    )
    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)


# ── Root ──────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"message": "BCT Hackathon Agent is running!"}


# ── Task A: Generate a review ─────────────────────────────────
@app.post("/generate-review")
def generate_review(req: ReviewRequest):
    past_reviews = load_user_reviews(req.user_id)

    if not past_reviews:
        return {"error": f"No reviews found for user {req.user_id}"}

    history_text = ""
    for r in past_reviews:
        history_text += f"""
- Product: {r['asin']}
  Rating: {r['rating']} stars
  Title: {r['title']}
  Review: {r['text']}
"""

    prompt = f"""You are simulating a real Amazon user based on their review history.

PAST REVIEWS BY THIS USER:
{history_text}

Now simulate what this SAME user would write for:
Product Name: {req.product_name}
Product Description: {req.product_description}

Match their tone, length, and rating style exactly.
Add natural Nigerian expressions where it fits naturally.

Respond ONLY in this JSON format, no markdown, no backticks:
{{
  "rating": <number from 1.0 to 5.0>,
  "title": "<short review headline>",
  "text": "<full review text>"
}}"""

    result = call_groq(prompt)
    result["user_id"] = req.user_id
    result["product_name"] = req.product_name
    return result


# ── Task B: Recommend products ────────────────────────────────
@app.post("/recommend")
def recommend(req: RecommendRequest):
    past_reviews = load_user_reviews(req.user_id)

    if not past_reviews:
        return {"error": f"No reviews found for user {req.user_id}"}

    history_text = ""
    for r in past_reviews:
        history_text += f"""
- Product: {r['asin']}
  Rating: {r['rating']} stars
  Review: {r['text']}
"""

    prompt = f"""You are a smart Nigerian shopping assistant on Amazon.

This user's past reviews:
{history_text}

Based on their taste and behaviour, recommend 3 products in the "{req.category}" category.
Consider: what they liked, how generous they are with ratings, what they value.
Make recommendations sound like a friendly Nigerian friend advising them.

Respond ONLY in this JSON format, no markdown, no backticks:
{{
  "recommendations": [
    {{
      "product_name": "<name>",
      "reason": "<why this user would love it, in natural Nigerian tone>"
    }},
    {{
      "product_name": "<name>",
      "reason": "<why this user would love it>"
    }},
    {{
      "product_name": "<name>",
      "reason": "<why this user would love it>"
    }}
  ]
}}"""

    result = call_groq(prompt)
    result["user_id"] = req.user_id
    return result