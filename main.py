from fastapi import FastAPI
from pydantic import BaseModel
import json
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="BCT Hackathon - LLM Review & Recommendation Agent")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


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