# 🤖 DSN x BCT LLM Agent Challenge — Hackathon 3.0

> 🧠 *Designing agents that understand how people behave, what they want, and what they'll choose next.*

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3_70b-orange)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🌍 Overview
An LLM-powered agent system built for the **DSN x Bluechip Technologies Hackathon 3.0**.
This project tackles both tasks using real Amazon Reviews data, **Groq (Llama 3.3-70b)**,
and **FastAPI** — with 🇳🇬 Nigerian cultural context baked in for bonus points!

---

## 🎯 Tasks

### 🅰️ Task A — User Modeling (Review Generator)
Given a user's review history and a new product, the agent **simulates** what that user
would write as a review — matching their tone, rating style, and adding natural
Nigerian expressions. 🇳🇬

### 🅱️ Task B — Smart Recommendation
Given a user's review history, the agent **recommends 3 products** they would love —
reasoning like a smart Nigerian friend who knows their taste. 😄

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| 🦙 Groq (Llama 3.3-70b) | LLM brain of the agent |
| ⚡ FastAPI | API framework |
| 🐍 Python 3.11 | Core language |
| 📦 Amazon Reviews 2023 | Dataset |
| 🐳 Docker | Containerization |

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

### 4️⃣ Download the dataset
```bash
python download_data.py
```

### 5️⃣ Run the API
```bash
uvicorn main:app --reload
```

### 6️⃣ Test the endpoints
Visit: `http://127.0.0.1:8000/docs` 🌐

---

## 📡 API Endpoints

### 📝 POST `/generate-review`
Simulates a user review for a new product.

**Input:**
```json
{
  "user_id": "AHZ6XMOLEWA67S3TX7IWEXXGWSOA",
  "product_name": "Amazon eGift Card - Birthday Cake",
  "product_description": "A digital gift card delivered by email, perfect for birthdays."
}
```

**Output:**
```json
{
  "rating": 5.0,
  "title": "E good gift",
  "text": "Having Amazon money is always a good thing, e worth am, trust me.",
  "user_id": "AHZ6XMOLEWA67S3TX7IWEXXGWSOA",
  "product_name": "Amazon eGift Card - Birthday Cake"
}
```

---

### 🎯 POST `/recommend`
Recommends 3 products based on user history.

**Input:**
```json
{
  "user_id": "AHZ6XMOLEWA67S3TX7IWEXXGWSOA",
  "category": "Gift Cards"
}
```

**Output:**
```json
{
  "recommendations": [
    {
      "product_name": "Amazon Gift Card",
      "reason": "My guy, you know what's always good, you feel me? 😄"
    }
  ],
  "user_id": "AHZ6XMOLEWA67S3TX7IWEXXGWSOA"
}
```

---

## 🐳 Docker

```bash
docker build -t bct-llm-agent .
docker run -p 8000:8000 --env-file .env bct-llm-agent
```

---

## 👨🏾‍💻 Author
**Abubakar Oluwatobi**
- 🎓 Data Science Nigeria (DSN) Student
- 💼 GitHub: [Oluwatobi-abu](https://github.com/Oluwatobi-abu)
- 🌍 Lagos, Nigeria 🇳🇬

---

> *"E good, i no regret am. E worth am, trust me."* — Our AI 😄
