import os
import json
import time
import re
from datetime import datetime

import bcrypt
import requests
import streamlit as st
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# ----------------------------- ENV -----------------------------
load_dotenv()

PPLX_KEY = os.getenv("PPLX_KEY")  # Perplexity API key
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME") or "price_comparator"


@st.cache_resource
def get_mongo_client():
    """Create and cache MongoDB client."""
    load_dotenv()
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        return None
    try:
        client = MongoClient(mongo_uri)
        client.admin.command("ping")
        return client
    except PyMongoError:
        return None


def get_user_collection():
    client = get_mongo_client()
    if client is None:
        return None
    db = client[MONGO_DB_NAME]
    return db["users"]


# ----------------------------- AUTH -----------------------------
def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())


def verify_password(password: str, hashed: bytes) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed)
    except Exception:
        return False


def register_user(email: str, password: str):
    users = get_user_collection()
    if users is None:
        return False, "Database error."

    if users.find_one({"email": email.lower()}):
        return False, "Email already registered."

    doc = {
        "email": email.lower(),
        "password": hash_password(password),
        "created_at": datetime.now(),
    }

    try:
        users.insert_one(doc)
        return True, "Registration successful. Login now."
    except Exception as e:
        return False, str(e)


def authenticate_user(email: str, password: str):
    users = get_user_collection()
    if users is None:
        return False, "Database error."

    user = users.find_one({"email": email.lower()})
    if not user:
        return False, "User not found."

    if verify_password(password, user.get("password", b"")):
        return True, "Login successful."
    return False, "Incorrect password."


# ----------------------------- STORES / HELPERS -----------------------------
TARGET_STORES = {
    "Flipkart": ["flipkart"],
    "Amazon": ["amazon", "amazon.in"],
    "Croma": ["croma"],
    "Reliance Digital": ["reliance digital", "reliancedigital"],
    "TataCliq": ["tatacliq", "tata cliq"],
}


def normalize(text: str) -> str:
    return (text or "").strip().lower()


def default_store_dict():
    return {
        store: {
            "available": False,
            "price": None,
            "details": "Not available",
            "link": None,
        }
        for store in TARGET_STORES.keys()
    }


# ----------------------------- PERPLEXITY INTEGRATION -----------------------------
def extract_json_from_text(text: str):
    """Extract JSON object from a plain / fenced code block string."""
    text = text.strip()

    # If there is a fenced code block ```json ... ```
    if "```" in text:
        start = text.find("```")
        end = text.rfind("```")
        if start != -1 and end != -1 and end > start:
            snippet = text[start + 3 : end].strip()
            if snippet.lower().startswith("json"):
                snippet = snippet[4:].strip()
            text = snippet

    return json.loads(text)


def fetch_prices_from_perplexity(query: str):
    """
    Call Perplexity API without domain restrictions to avoid anti-bot blocking.
    """
    if not PPLX_KEY:
        return None, "PPLX_KEY not set in .env"

    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {PPLX_KEY}",
        "Content-Type": "application/json",
    }

    # 1. SYSTEM PROMPT: Strict JSON instructions
    system_prompt = (
        "You are an expert Procurement Agent. Your task is to find the current sale price of a product.\n"
        "STORES: Amazon.in, Flipkart, Croma, Reliance Digital, TataCliq.\n"
        "RULES:\n"
        "1. Search the open web for the current price on these specific stores.\n"
        "2. If a store is out of stock or price is not found, set 'available': false.\n"
        "3. IGNORE reviews and blogs. Look for price listings.\n"
        "4. Return ONLY valid JSON. No conversational text.\n\n"
        "JSON SCHEMA:\n"
        "{\n"
        '  "product_title": "Product Name",\n'
        '  "stores": [\n'
        '    {"store": "Amazon", "available": true, "price": 10000, "link": "...", "notes": ""},\n'
        '    {"store": "Flipkart", "available": true, "price": 10000, "link": "...", "notes": ""}\n'
        '    ... (and so on)\n'
        '  ]\n'
        "}"
    )

    body = {
        "model": "sonar-pro", 
        "messages": [
            {"role": "system", "content": system_prompt},
            # 2. USER MESSAGE: Clear instruction
            {"role": "user", "content": f"Find the current price of '{query}' on Amazon, Flipkart, Croma, Reliance Digital, and TataCliq. Return JSON only."}
        ],
        "max_tokens": 1000,
        "temperature": 0.1,
        # 3. CRITICAL FIX: REMOVED 'search_domain_filter' 
        # We let it search the whole web so it doesn't get blocked.
    }

    try:
        resp = requests.post(url, headers=headers, json=body, timeout=60)
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return None, f"Error calling Perplexity API: {e}"

    # 4. SAFETY CATCH: Extract JSON if the AI adds text
    try:
        # If content has ```json markers, extract them
        if "```" in content:
            content = content.split("```json")[-1].split("```")[0].strip()
        elif "{" in content:
             # Find the first { and last }
            start = content.find("{")
            end = content.rfind("}") + 1
            content = content[start:end]
            
        parsed = json.loads(content)
    except Exception as e:
        # PRINT THE RAW ERROR for debugging
        print(f"RAW API RESPONSE ERROR: {content}")
        return None, f"Failed to parse JSON. The API returned text instead of data. Try again."

    # --- PARSING LOGIC (Standard) ---
    result = default_store_dict()
    product_title = (parsed.get("product_title") or query).strip()

    for row in parsed.get("stores", []):
        name = normalize(row.get("store"))
        match_store = None
        for k, aliases in TARGET_STORES.items():
            if k.lower() == name or any(a in name for a in aliases):
                match_store = k
                break
        if not match_store:
            continue

        available = bool(row.get("available", False))
        price = row.get("price")
        # clean price if it's a string like "₹12,000"
        if isinstance(price, str):
            price = ''.join(filter(str.isdigit, price))
            price = int(price) if price else None

        result[match_store] = {
            "available": available and price is not None,
            "price": price,
            "details": row.get("notes", ""),
            "link": row.get("link"),
        }

    return {"product_title": product_title, "stores": result}, None


# ----------------------------- UI: LOGIN / REGISTER -----------------------------
def login_register_ui():
    st.title("Online Price Comparator")

    if st.session_state.get("user_email"):
        st.success(f"Logged in as {st.session_state['user_email']}")
        if st.button("Logout"):
            st.session_state["user_email"] = None
            st.rerun()
        return

    login_tab, register_tab = st.tabs(["Login", "Register"])

    with login_tab:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            ok, msg = authenticate_user(email, password)
            if ok:
                st.success(msg)
                st.session_state["user_email"] = email
                time.sleep(0.2)
                st.rerun()
            else:
                st.error(msg)

    with register_tab:
        email = st.text_input("Email", key="reg_email")
        pw1 = st.text_input("Password", type="password", key="reg_pw1")
        pw2 = st.text_input("Confirm Password", type="password", key="reg_pw2")
        if st.button("Create Account"):
            if pw1 != pw2:
                st.error("Passwords do not match.")
            elif len(pw1) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                ok, msg = register_user(email, pw1)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)


# ----------------------------- UI: DASHBOARD -----------------------------
def dashboard_ui():
    st.header("Price Comparison Dashboard")

    if not st.session_state.get("user_email"):
        st.warning("Login required.")
        return

    with st.form("search_form"):
        query = st.text_input("Search product", placeholder="Ex: Samsung Galaxy S24 128GB")
        submit = st.form_submit_button("Compare Prices")

    if not submit:
        return

    with st.spinner("Fetching live prices using Perplexity..."):
        data, err = fetch_prices_from_perplexity(query)

    if err:
        st.error(err)
        return

    product_title = data.get("product_title") or query
    store_data = data["stores"]

    st.success(f"Matched Product: {product_title}")

    cols = st.columns(len(TARGET_STORES))
    for idx, (store, info) in enumerate(store_data.items()):
        with cols[idx]:
            st.markdown(f"### {store}")
            if not info["available"]:
                st.warning("❌ Not Available")
                if info.get("details"):
                    st.caption(info["details"])
            else:
                price = info["price"]
                st.markdown(
                    f"<p style='font-size:26px;font-weight:700;color:#0a8a24'>₹{price}</p>",
                    unsafe_allow_html=True,
                )
                if info.get("details"):
                    st.caption(info["details"])
                if info.get("link"):
                    st.markdown(f"[🔗 View Deal]({info['link']})", unsafe_allow_html=True)


# ----------------------------- MAIN -----------------------------
def main():
    st.set_page_config(page_title="Online Price Comparator", layout="wide")
    login_register_ui()
    st.markdown("---")
    dashboard_ui()


if __name__ == "__main__":
    main()
