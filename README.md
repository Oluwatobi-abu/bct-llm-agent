# 🤖 DSN x BCT LLM Agent Challenge — Hackathon 3.0

> 🧠 *Designing agents that understand how people behave, what they want, and what they'll choose next.*

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3_70b-orange)
![License](https://img.shields.io/badge/License-MIT-green)
![Live](https://img.shields.io/badge/Live-Render-brightgreen)

---

## 🌍 Overview
An LLM-powered agent system built for the **DSN x Bluechip Technologies Hackathon 3.0**.
This project tackles both tasks using real Amazon Reviews 2023 data, **Groq (Llama 3.3-70b)**,
and **FastAPI** — with 🇳🇬 Nigerian cultural context baked in at every layer for bonus points!

🔗 **Live Demo:** https://bct-llm-agent.onrender.com
📁 **GitHub:** https://github.com/Oluwatobi-abu/bct-llm-agent

---

## 🎯 Tasks

### 🅰️ Task A — User Modeling (Review Generator)
Given a user's review history and a new product, the agent **simulates** what that user
would write as a review — matching their tone, rating style, and adding natural
Nigerian expressions. Works for both **known users** (from dataset) and **unknown users**
(falls back to a default Nigerian shopper profile). 🇳🇬

### 🅱️ Task B — Smart Recommendation with NDCG Ranking
Given a user's review history, the agent **recommends 3 ranked products** — using a
two-stage pipeline: generate 10 candidates → score and re-rank by relevance → return
top 3 with NDCG@10 score. Handles **cold-start users** gracefully and supports
**multi-turn conversational refinement**. 😄

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| 🦙 Groq (Llama 3.3-70b) | LLM brain of the agent |
| ⚡ FastAPI | API framework |
| 🐍 Python 3.11 | Core language |
| 📦 Amazon Reviews 2023 | Dataset |
| 💬 Multi-turn Chat | Conversational memory across requests |
| 📊 NDCG@10 | Ranking quality metric |
| 🐳 Docker | Containerization via Render |
| 🌐 Render | Cloud deployment |

---

## 🚀 How To Run

### 1️⃣ Clone the repo
```bash
git clone https://github.com/Oluwatobi-abu/bct-llm-agent.git
cd bct-llm-agent
```

### 2️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Set up environment variables
Create a `.env` file in the root folder:
```
GROQ_API_KEY=your_groq_api_key_here
```
Get your free Groq API key at: https://console.groq.com

### 4️⃣ Download the dataset
```bash
python download_data.py
```

### 5️⃣ Run the API
```bash
uvicorn main:app --reload
```

### 6️⃣ Access the UI and API docs
- 🎨 Beautiful UI: `http://127.0.0.1:8000`
- 📡 API Docs: `http://127.0.0.1:8000/docs`

---

## 📡 API Endpoints

### 📝 POST `/generate-review`
Simulates a user review for a new product.
Works for **known users** (uses real review history) and **unknown users** (uses default Nigerian shopper profile).

**Input:**
```json
{
  "user_id": "AHZ6XMOLEWA67S3TX7IWEXXGWSOA",
  "product_name": "Ironing Board",
  "product_description": "Great legs for standing, soft clothing material texture to iron on."
}
```

**Output:**
```json
{
  "rating": 5.0,
  "title": "Good one",
  "text": "Having a good ironing board is always a blessing, no worries at all, my wife dey use am well well.",
  "user_id": "AHZ6XMOLEWA67S3TX7IWEXXGWSOA",
  "product_name": "Ironing Board"
}
```

**More real output samples across different products:**
- 🎶 Samsung Earbuds → *"Make my music sound sweet like jollof rice"*
- 🎂 Birthday Cake → *"No be small thing, my family enjoy am"*
- 🍳 Cooking Pot → *"I use am for my small catering business, e dey serve me well"*

---

### 🎯 POST `/recommend`
Recommends 3 ranked products based on user history with NDCG@10 scoring.
Handles **cold-start** (unknown/new users) gracefully with popular Nigerian picks.

**Input:**
```json
{
  "user_id": "Dotun",
  "category": "Car Wash Equipment"
}
```

**Output:**
```json
{
  "recommendations": [
    {
      "product_name": "Microfiber Car Wash Mitt",
      "reason": "Soft and gentle on your car's paint, easy to rinse and dry",
      "relevance_score": 0.9
    },
    {
      "product_name": "Car Wash Soap and Shampoo",
      "reason": "Gentle and effective, removes dirt without stripping wax",
      "relevance_score": 0.8
    },
    {
      "product_name": "Car Vacuum Cleaner",
      "reason": "Portable and powerful, perfect for cleaning your car's interior",
      "relevance_score": 0.7
    }
  ],
  "user_id": "Dotun",
  "cold_start": true,
  "ndcg_score": 1.0
}
```

**Works with absolutely any category — some tested examples:**
- 💈 Barbing Clippers → Wahl Senior, Andis T-Outliner, Oster Fast Feed
- 📺 Television → Samsung 4K, LG OLED, TCL Roku
- 🚗 Car Wash Equipment → Microfiber Mitt, Car Shampoo, Vacuum Cleaner
- 🍳 Kitchen Appliances → Binatone Blender, Philips, Kenwood

---

### 💬 POST `/recommend/chat`
Multi-turn conversational recommendations with full memory.
The AI remembers previous messages and refines recommendations based on follow-ups.

**Input (First message):**
```json
{
  "user_id": "Abel-Brighton",
  "message": "Recommend barbing clippers for me",
  "category": "Barbing Clippers",
  "history": []
}
```

**Input (Follow-up — AI remembers previous context):**
```json
{
  "user_id": "Abel-Brighton",
  "message": "Show me cheaper options abeg",
  "category": "Barbing Clippers",
  "history": [
    {"role": "user", "content": "Recommend barbing clippers for me"},
    {"role": "assistant", "content": "<previous response>"}
  ]
}
```

**Output:**
```json
{
  "message": "No worries my friend, make you no go break the bank!",
  "recommendations": [...],
  "follow_up": "How much are you looking to spend?",
  "ndcg_score": 0.9528,
  "cold_start": false,
  "history": [...]
}
```

---

## 🏆 Scoring Features

| Feature | Points | Status |
|---|---|---|
| Ranking Quality (NDCG@10) | 30 | ✅ Implemented — scores 0.95-1.0 |
| Cold-Start & Cross-Domain | 25 | ✅ Graceful fallback for unknown users |
| Contextual Relevance | 20 | ✅ Nigerian-friend persona throughout |
| Solution Paper | 15 | ✅ Full 9-section paper submitted |
| Code Reproducibility | 10 | ✅ Clean repo, documented README |
| Nigerian Localization | Bonus | ✅ Three-level integration |
| Multi-turn Conversation | Bonus | ✅ Full conversational memory |

---

## 🐳 Docker & Deployment

The project is fully containerized with Docker. The `Dockerfile` is included
in the repository and is used automatically by Render for cloud deployment.

### Run with Docker locally:
```bash
docker build -t bct-llm-agent .
docker run -p 8000:8000 --env-file .env bct-llm-agent
```

### Cloud Deployment (Render):
The app is deployed and live at:
👉 **https://bct-llm-agent.onrender.com**

Render automatically builds the Docker container on every push to `main`.
No manual deployment needed.

### Environment Variables Required:
| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Your free Groq API key from console.groq.com |

---

## 📁 Project Structure

```
bct-llm-agent/
├── main.py                       # FastAPI app — all endpoints
├── download_data.py              # Dataset downloader
├── task_a_agent.py               # Task A standalone script
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Container configuration
├── .dockerignore                 # Docker ignore rules
├── .gitignore                    # Git ignore rules
├── static/
│   └── index.html                # NaijAI frontend UI
└── data/
    └── gift_cards_reviews.jsonl  # Amazon Reviews 2023 dataset
```

---

## 👨🏾‍💻 Author
**Abubakar Oluwatobi**
- 🎓 Data Science Nigeria (DSN) Student
- 💼 GitHub: [Oluwatobi-abu](https://github.com/Oluwatobi-abu)
- 📧 abuoluwatobi9@gmail.com
- 🌍 Lagos, Nigeria 🇳🇬

---

> *"E good, i no regret am. E worth am, trust me."* — Our AI 😄🇳🇬
