<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://placehold.co/120x120/0f172a/3b82f6?text=PC&font=montserrat">
    <img src="https://placehold.co/120x120/3b82f6/ffffff?text=PC&font=montserrat" width="120" alt="Price Comparator Logo">
  </picture>
</p>

<h1 align="center">Online Price Comparator</h1>

<p align="center">
  <b>Compare product prices across India's top e-commerce stores in real-time</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white" alt="Python 3.12+">
  <img src="https://img.shields.io/badge/Flask-2.3%2B-000000?logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/MongoDB-Atlas-47A248?logo=mongodb&logoColor=white" alt="MongoDB Atlas">
  <img src="https://img.shields.io/badge/Perplexity_API-sonar--pro-1E90FF?logo=perplexity&logoColor=white" alt="Perplexity API">
  <img src="https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B?logo=streamlit&logoColor=white" alt="Streamlit">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Active-10b981?logo=checkmarx&logoColor=white" alt="Status: Active">
  <img src="https://img.shields.io/badge/License-MIT-3b82f6" alt="License: MIT">
</p>

---

## ✨ Features

| Feature | Description |
|---|---|
| **🔐 User Authentication** | Register & login with bcrypt-hashed passwords, persistent Flask sessions (7 days) |
| **🔍 Live Price Search** | Fetch real-time prices from Perplexity AI's `sonar-pro` model |
| **🏪 5 Indian Stores** | Amazon.in, Flipkart, Croma, Reliance Digital, TataCliq |
| **📊 Visual Dashboard** | Card-based UI with availability badges, INR prices, and "View Deal" links |
| **👤 Profile Management** | Inline editing of phone number linked to your account |
| **📱 Responsive Design** | Modern UI with Poppins font, Remixicon icons, mobile-friendly layout |
| **🔄 Dual UI** | Flask web app (primary) + Streamlit backup (alternative) |

---

## 🏗 Architecture

```
┌──────────────────────────────────────────────────────────┐
│                      User's Browser                       │
└──────────────────┬───────────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────────┐
│                    Flask App (flask_app.py)               │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐  │
│  │  Login   │  │ Register │  │Dashboard │  │ Profile │  │
│  │ /login   │  │/register │  │/dashboard│  │ /profile│  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬────┘  │
│       └──────────────┼─────────────┼──────────────┘       │
│                      │             │                      │
│               ┌──────▼─────────────▼──────┐               │
│               │  Flask Sessions (auth)    │               │
│               └───────────────────────────┘               │
└──────────────────┬────────────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────────┐
│            streamlit_version_backup.py (Core Logic)       │
│                                                          │
│  ┌─────────────────┐       ┌──────────────────────────┐  │
│  │  Auth Helpers    │       │  Perplexity Integration  │  │
│  │  (bcrypt/MongoDB)│       │  fetch_prices_from_      │  │
│  │                 │       │  perplexity(query)        │  │
│  └────────┬────────┘       └───────────┬──────────────┘  │
│           │                            │                 │
│           ▼                            ▼                 │
│  ┌──────────────────────────────────────────────────┐    │
│  │              Perplexity AI API                    │    │
│  │         (sonar-pro model, web search)             │    │
│  └───────────────────────┬──────────────────────────┘    │
│                          │                               │
│                          ▼                               │
│  ┌──────────────────────────────────────────────────┐    │
│  │                MongoDB Atlas                       │    │
│  │  ┌──────────────────────────────────────────────┐ │    │
│  │  │              users Collection                  │ │    │
│  │  │  { email, password(hashed), phone, createdAt } │ │    │
│  │  └──────────────────────────────────────────────┘ │    │
│  └──────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
```

### Data Flow: Price Search

```
User searches "iPhone 15"
         │
         ▼
  Flask POST /dashboard
         │
         ▼
  fetch_prices_from_perplexity("iPhone 15")
         │
         ▼
  Perplexity API → sonar-pro model
  [searches Amazon, Flipkart, Croma, etc.]
         │
         ▼
  Returns structured JSON:
  { product_title, stores: [{store, price, link, ...}] }
         │
         ▼
  Parsed & mapped to TARGET_STORES
         │
         ▼
  Rendered as store cards in dashboard.html
```

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.12+ · Flask 2.3 · Jinja2 Templating |
| **Database** | MongoDB Atlas (cloud, via PyMongo) |
| **AI / Search** | Perplexity AI API (`sonar-pro`) |
| **Auth** | bcrypt · Flask Sessions (7-day lifetime) |
| **Frontend** | HTML5 · CSS3 (custom properties) · Poppins · Remixicon |
| **Alt. UI** | Streamlit 1.28+ |
| **HTTP** | `requests` library |

---

## 📁 Project Structure

```
price_comparator/
├── flask_app.py                   # 🚀 Main Flask application (routes, server)
├── streamlit_version_backup.py    # 🔄 Streamlit backup (core business logic)
├── .env                           # 🔒 Environment variables (MONGO_URI, PPLX_KEY)
├── .gitignore                     # Python, venv, .env, OS files
│
├── static/
│   └── style.css                  # 🎨 Complete CSS design system (354 lines)
│
├── templates/
│   ├── auth_base.html             # Base template for auth pages
│   ├── base.html                  # Base template for dashboard (sidebar + navbar)
│   ├── layout.html                # Simpler alternative layout
│   ├── login.html                 # Split-screen login page
│   ├── register.html              # Split-screen registration page
│   ├── dashboard.html             # Price comparison dashboard
│   └── profile.html               # Profile editing page
│
└── __pycache__/                   # Python bytecode (generated)
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- MongoDB Atlas account (or local MongoDB)
- Perplexity API key ([get one here](https://www.perplexity.ai/settings/api))

### 1. Clone & Setup

```bash
git clone https://github.com/yourusername/price_comparator.git
cd price_comparator
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install flask bcrypt requests python-dotenv pymongo
```

*For the Streamlit alternative:*
```bash
pip install streamlit
```

### 3. Configure Environment

Create a `.env` file in the project root:

```env
MONGO_URI=mongodb+srv://<user>:<password>@cluster.mongodb.net/?retryWrites=true&w=majority
MONGO_DB_NAME=price_comparator
PPLX_KEY=pplx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 4. Run the App

```bash
# Flask version (primary) — http://localhost:5000
python3 flask_app.py

# Streamlit version (alternative) — http://localhost:8501
streamlit run streamlit_version_backup.py
```

---

## 🖥 Pages & Screens

| Page | Route | Description |
|---|---|---|
| **Login** | `/login` | Split-screen login with email & password |
| **Register** | `/register` | Account creation with password confirmation |
| **Dashboard** | `/dashboard` | Product search + store price comparison cards |
| **Profile** | `/profile` | View/edit phone number for your account |

### UI Highlights

```
┌────────────────────────────────────────────────────┐
│  ┌──────────┐  ┌─────────────────────────────────┐ │
│  │          │  │  [user@email.com    ▾]           │ │
│  │  🏠      │  │                                  │ │
│  │  Dashboard│  │  Price Comparison Dashboard      │ │
│  │          │  │                                  │ │
│  │          │  │  ┌──────────────────────────────┐ │ │
│  │          │  │  │ 🔍 iPhone 15   [Compare]    │ │ │
│  │          │  │  └──────────────────────────────┘ │ │
│  │          │  │                                  │ │
│  │          │  │  ┌────────┐ ┌────────┐ ┌────────┐ │ │
│  │          │  │  │ Amazon │ │Flipkart│ │ Croma  │ │ │
│  │          │  │  │ ₹72,999│ │ ₹70,999│ │ N/A    │ │ │
│  │          │  │  │[Deal]  │ │[Deal]  │ │        │ │ │
│  │          │  │  └────────┘ └────────┘ └────────┘ │ │
│  │          │  │  ┌────────┐ ┌────────┐            │ │
│  │          │  │  │Reliance│ │TataCliq│            │ │
│  │          │  │  │ ₹73,999│ │ ₹71,499│            │ │
│  │          │  │  │[Deal]  │ │[Deal]  │            │ │
│  │          │  │  └────────┘ └────────┘            │ │
│  └──────────┘  └─────────────────────────────────┘ │
└────────────────────────────────────────────────────┘
```

---

## 🔑 API Reference

### Perplexity Integration

The app uses Perplexity AI's `sonar-pro` model with a **system prompt** designed to return structured JSON:

```python
SYSTEM_PROMPT = """
You are an expert Procurement Agent...
Return ONLY valid JSON with format:
{
  "product_title": "Product Name",
  "stores": [
    {"store": "Amazon", "available": true, "price": 10000, "link": "...", "notes": ""},
    ...
  ]
}
"""
```

**Endpoint:** `POST https://api.perplexity.ai/chat/completions`  
**Auth:** Bearer token via `PPLX_KEY` environment variable  
**Timeout:** 60 seconds  
**Temperature:** 0.1 (deterministic outputs)

---

## 🗄 Database Schema

**Collection:** `users` (MongoDB)

```json
{
  "email": "user@example.com",
  "password": "$2b$12$...",           // bcrypt hash
  "phone": "+91-9876543210",           // optional
  "created_at": "2026-06-03T10:30:00Z"
}
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing`)
5. Open a Pull Request

---

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.

---

<p align="center">
  <b>Compare smarter. Save faster.</b>
</p>
