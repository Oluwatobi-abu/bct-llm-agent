from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List
import json
import os
import re
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
    return FileResponse("static/index.html")


# ── Task A: Generate a review ─────────────────────────────────
@app.post("/generate-review")
def generate_review(req: ReviewRequest):
    past_reviews = load_user_reviews(req.user_id)

    if not past_reviews:
        past_reviews = [{
            "asin": "B00DEFAULT",
            "rating": 4.5,
            "title": "Good product",
            "text": "This product is good value for money, I recommend it."
        }]

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


# ── Task B: Recommend products with NDCG ranking ──────────────
@app.post("/recommend")
def recommend(req: RecommendRequest):
    past_reviews = load_user_reviews(req.user_id)

    # ── Cold-start handling ────────────────────────────────────
    if not past_reviews:
        cold_prompt = f"""You are a smart Nigerian shopping assistant on Amazon.

This is a NEW user with no purchase history yet.

Recommend 3 popular and highly rated products in the "{req.category}" category
that would appeal to most Nigerian Amazon shoppers.
Think about what Nigerian users generally value: good value for money,
reliability, and products that make great gifts.

Respond ONLY in this JSON format, no markdown, no backticks:
{{
  "recommendations": [
    {{
      "product_name": "<name>",
      "reason": "<why most Nigerian shoppers would love it>",
      "relevance_score": <float between 0.0 and 1.0>
    }},
    {{
      "product_name": "<name>",
      "reason": "<why most Nigerian shoppers would love it>",
      "relevance_score": <float between 0.0 and 1.0>
    }},
    {{
      "product_name": "<name>",
      "reason": "<why most Nigerian shoppers would love it>",
      "relevance_score": <float between 0.0 and 1.0>
    }}
  ],
  "cold_start": true,
  "ndcg_score": 0.0,
  "user_id": "{req.user_id}"
}}"""
        result = call_groq(cold_prompt)
        result["user_id"] = req.user_id
        result["cold_start"] = True
        return result

    # ── Build user profile ─────────────────────────────────────
    history_text = ""
    avg_rating = sum(r["rating"] for r in past_reviews) / len(past_reviews)
    high_rated = [r for r in past_reviews if r["rating"] >= 4.0]

    for r in past_reviews:
        history_text += f"""
- Product: {r['asin']}
  Rating: {r['rating']} stars
  Review: {r['text']}
"""

    # ── Step 1: Generate 10 candidates ────────────────────────
    candidate_prompt = f"""You are a smart Nigerian shopping assistant on Amazon.

USER PROFILE:
- Average rating given: {avg_rating:.1f} stars
- Number of reviews: {len(past_reviews)}
- High-rated products: {len(high_rated)} out of {len(past_reviews)}

PAST REVIEWS:
{history_text}

Generate 10 different product candidates in the "{req.category}" category
that this user might enjoy based on their history.
Assign each a relevance_score (0.0 to 1.0) based on how well it matches
this user's demonstrated preferences. Higher score = better match.

Respond ONLY in this JSON format, no markdown, no backticks:
{{
  "candidates": [
    {{"product_name": "<name>", "relevance_score": <0.0-1.0>}},
    {{"product_name": "<name>", "relevance_score": <0.0-1.0>}},
    {{"product_name": "<name>", "relevance_score": <0.0-1.0>}},
    {{"product_name": "<name>", "relevance_score": <0.0-1.0>}},
    {{"product_name": "<name>", "relevance_score": <0.0-1.0>}},
    {{"product_name": "<name>", "relevance_score": <0.0-1.0>}},
    {{"product_name": "<name>", "relevance_score": <0.0-1.0>}},
    {{"product_name": "<name>", "relevance_score": <0.0-1.0>}},
    {{"product_name": "<name>", "relevance_score": <0.0-1.0>}},
    {{"product_name": "<name>", "relevance_score": <0.0-1.0>}}
  ]
}}"""

    candidates_result = call_groq(candidate_prompt)
    candidates = candidates_result["candidates"]

    # ── Step 2: Sort by relevance score (NDCG ranking) ────────
    candidates_sorted = sorted(
        candidates,
        key=lambda x: x["relevance_score"],
        reverse=True
    )

    # ── Step 3: Calculate NDCG@10 score ───────────────────────
    import math

    def dcg(scores):
        return sum(
            (2 ** s - 1) / math.log2(i + 2)
            for i, s in enumerate(scores)
        )

    actual_scores = [c["relevance_score"] for c in candidates_sorted]
    ideal_scores = sorted(actual_scores, reverse=True)

    dcg_score = dcg(actual_scores)
    idcg_score = dcg(ideal_scores)
    ndcg = round(dcg_score / idcg_score, 4) if idcg_score > 0 else 0.0

    # ── Step 4: Get top 3 with Nigerian-style reasons ─────────
    top3 = candidates_sorted[:3]
    top3_text = "\n".join(
        [f"{i+1}. {c['product_name']} (score: {c['relevance_score']})"
         for i, c in enumerate(top3)]
    )

    reason_prompt = f"""You are a smart Nigerian shopping assistant on Amazon.

Based on this user's history:
{history_text}

These are the TOP 3 recommended products (already ranked best to worst):
{top3_text}

For each product, write a short warm reason why this specific user would love it.
Sound like a friendly Nigerian friend giving advice naturally.
Use Nigerian expressions where they fit (e.g. "e good", "my guy", "e worth am", "abi").

Respond ONLY in this JSON format, no markdown, no backticks:
{{
  "recommendations": [
    {{
      "product_name": "<exact name from list>",
      "reason": "<Nigerian-style reason>",
      "relevance_score": <score from above>
    }},
    {{
      "product_name": "<exact name from list>",
      "reason": "<Nigerian-style reason>",
      "relevance_score": <score from above>
    }},
    {{
      "product_name": "<exact name from list>",
      "reason": "<Nigerian-style reason>",
      "relevance_score": <score from above>
    }}
  ]
}}"""

    final_result = call_groq(reason_prompt)
    final_result["user_id"] = req.user_id
    final_result["cold_start"] = False
    final_result["ndcg_score"] = ndcg

    return final_result

# ── Multi-turn conversation model ─────────────────────────────
class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    user_id: str
    message: str
    category: str = "Gift Cards"
    history: List[ChatMessage] = []


# ── Task B: Multi-turn conversational recommendation ──────────
@app.post("/recommend/chat")
def recommend_chat(req: ChatRequest):
    past_reviews = load_user_reviews(req.user_id)

    # Build user profile text
    if past_reviews:
        avg_rating = sum(r["rating"] for r in past_reviews) / len(past_reviews)
        history_text = ""
        for r in past_reviews:
            history_text += f"""
- Product: {r['asin']}
  Rating: {r['rating']} stars
  Review: {r['text']}
"""
        user_context = f"""USER REVIEW HISTORY:
Average rating given: {avg_rating:.1f} stars
Reviews:
{history_text}"""
    else:
        user_context = "NEW USER — no review history available. Use popular Nigerian preferences."

    # Build conversation history for LLM
    conversation = []

    # System message
    system_msg = f"""You are NaijAI, a smart Nigerian shopping assistant on Amazon.
You remember everything discussed in this conversation.
You give personalized product recommendations based on the user's history.
Always sound like a friendly, knowledgeable Nigerian friend.
Use natural Nigerian expressions where they fit naturally.

{user_context}

When recommending products, always return your response in this JSON format:
{{
  "message": "<your friendly Nigerian response>",
  "recommendations": [
    {{"product_name": "<name>", "reason": "<reason>", "relevance_score": <0.0-1.0>}},
    {{"product_name": "<name>", "reason": "<reason>", "relevance_score": <0.0-1.0>}},
    {{"product_name": "<name>", "reason": "<reason>", "relevance_score": <0.0-1.0>}}
  ],
  "follow_up": "<one question to refine recommendations further>"
}}
If the user is just chatting or asking a question without needing recommendations,
return:
{{
  "message": "<your friendly response>",
  "recommendations": [],
  "follow_up": "<relevant follow-up question>"
}}
Always respond with valid JSON only. No markdown, no backticks."""

    # Add past conversation history
    for msg in req.history:
        conversation.append({
            "role": msg.role,
            "content": msg.content
        })

    # Add current user message
    conversation.append({
        "role": "user",
        "content": req.message
    })

    # Call Groq with full conversation
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_msg},
            *conversation
        ],
        temperature=0.7,
        max_tokens=800
    )

    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    # Find JSON object in response even if LLM adds extra text
    json_match = re.search(r'\{.*\}', raw, re.DOTALL)
    if json_match:
        raw = json_match.group(0)

    if not raw:
        return {
            "message": "E don happen o! Something went wrong, abeg try again my guy.",
            "recommendations": [],
            "follow_up": "What category of products are you interested in?",
            "ndcg_score": 0.0,
            "user_id": req.user_id,
            "history": []
        }

    result = json.loads(raw)

    # Add NDCG score if recommendations exist
    if result.get("recommendations"):
        import math
        scores = [r["relevance_score"] for r in result["recommendations"]]
        sorted_scores = sorted(scores, reverse=True)

        def dcg(s):
            return sum((2**v - 1) / math.log2(i + 2) for i, v in enumerate(s))

        ndcg = round(dcg(scores) / dcg(sorted_scores), 4) if dcg(sorted_scores) > 0 else 0.0
        result["ndcg_score"] = ndcg
    else:
        result["ndcg_score"] = 0.0

    # Append assistant response to history
    updated_history = list(req.history) + [
        ChatMessage(role="user", content=req.message),
        ChatMessage(role="assistant", content=raw)
    ]

    result["user_id"] = req.user_id
    result["history"] = [{"role": m.role, "content": m.content} for m in updated_history]

    return result