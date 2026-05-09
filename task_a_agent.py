import json
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# ── 1. Load reviews from our dataset ──────────────────────────
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


# ── 2. Get any user that has reviews ──────────────────────────
def get_sample_user():
    with open("data/gift_cards_reviews.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            review = json.loads(line.strip())
            return review["user_id"]


# ── 3. The AI review generator ────────────────────────────────
def generate_review(user_id, product_name, product_description):
    past_reviews = load_user_reviews(user_id)

    if not past_reviews:
        return {"error": f"No reviews found for user {user_id}"}

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

Now simulate what this SAME user would write as a review for this new product:
Product Name: {product_name}
Product Description: {product_description}

Study the user's pattern:
- How do they rate things? Are they generous or strict with stars?
- How long are their reviews?
- What tone do they use?
- Do they write formally or casually?

IMPORTANT: Add a Nigerian touch — use natural Nigerian expressions where it fits
(e.g., "e good", "i no regret am", "e worth am", "this one dey different")
but keep it realistic and natural, not forced.

Respond ONLY in this exact JSON format, nothing else, no markdown, no backticks:
{{
  "rating": <number from 1.0 to 5.0>,
  "title": "<short review headline>",
  "text": "<full review text>"
}}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=500
    )

    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    result = json.loads(raw)
    return result


# ── 4. Test it ─────────────────────────────────────────────────
if __name__ == "__main__":
    user_id = get_sample_user()
    print(f"Testing with user: {user_id}\n")

    past = load_user_reviews(user_id)
    print(f"This user has {len(past)} past review(s):")
    for r in past:
        print(f"  ⭐ {r['rating']} — {r['title']}: {r['text'][:60]}...")

    print("\n--- Generating simulated review for a new product ---\n")

    result = generate_review(
        user_id=user_id,
        product_name="Amazon eGift Card - Birthday Cake",
        product_description="A digital Amazon gift card delivered by email, "
                            "perfect for birthdays. Available in any amount."
    )

    print("🤖 AI Generated Review:")
    print(f"  ⭐ Rating : {result['rating']}")
    print(f"  📝 Title  : {result['title']}")
    print(f"  💬 Review : {result['text']}")