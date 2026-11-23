"""Authentication and User Management Module.
Supports local user persistence, secure salted hashing, pre-seeded judge/farmer demo accounts,
and Streamlit session state management.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import streamlit as st

AUTH_FILE = Path(__file__).resolve().parent.parent / "data" / "users.json"
SALT = "krishi_netra_salt_2026"


def _hash_pw(password: str) -> str:
    return hashlib.sha256((SALT + password).encode("utf-8")).hexdigest()


DEFAULT_USERS: dict[str, dict[str, Any]] = {
    "judge@krishinetra.ai": {
        "name": "Competition Judge",
        "email": "judge@krishinetra.ai",
        "pw_hash": _hash_pw("judge123"),
        "role": "Exhibition / Technical Judge",
        "role_badge": "Judge / Evaluator",
        "location": "New Delhi",
        "icon": "👨‍⚖️",
    },
    "farmer@krishinetra.ai": {
        "name": "Ramesh Patel",
        "email": "farmer@krishinetra.ai",
        "pw_hash": _hash_pw("farmer123"),
        "role": "Farmer / Progressive Grower",
        "role_badge": "Farmer / कृषक",
        "location": "Karnal, Haryana",
        "icon": "🌾",
    },
    "kvk@krishinetra.ai": {
        "name": "Dr. Ananya Sharma",
        "email": "kvk@krishinetra.ai",
        "pw_hash": _hash_pw("kvk123"),
        "role": "KVK Agronomist / Plant Pathologist",
        "role_badge": "KVK Officer / कृषि वैज्ञानिक",
        "location": "ICAR-IARI, New Delhi",
        "icon": "🔬",
    },
}


def load_users() -> dict[str, dict[str, Any]]:
    if not AUTH_FILE.exists():
        save_users(DEFAULT_USERS)
        return DEFAULT_USERS
    try:
        with open(AUTH_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Ensure defaults always exist
            for k, v in DEFAULT_USERS.items():
                if k not in data:
                    data[k] = v
            return data
    except Exception:
        return DEFAULT_USERS


def save_users(users: dict[str, dict[str, Any]]) -> None:
    try:
        AUTH_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(AUTH_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def get_current_user() -> dict[str, Any] | None:
    return st.session_state.get("user")


def is_logged_in() -> bool:
    return get_current_user() is not None


def login(identifier: str, password: str) -> tuple[bool, str, dict[str, Any] | None]:
    identifier = identifier.strip().lower()
    users = load_users()
    if identifier not in users:
        return False, "User not found. Please check your email or Sign Up.", None
    user = users[identifier]
    if user["pw_hash"] != _hash_pw(password):
        return False, "Incorrect password. Please try again.", None
    st.session_state["user"] = user
    return True, f"Welcome back, {user['name']}!", user


def signup(
    name: str,
    email: str,
    password: str,
    role: str,
    location: str,
) -> tuple[bool, str, dict[str, Any] | None]:
    name = name.strip()
    email = email.strip().lower()
    location = location.strip()
    if not name or not email or not password:
        return False, "Please fill in all required fields (Name, Email, Password).", None
    if len(password) < 4:
        return False, "Password must be at least 4 characters long.", None
    users = load_users()
    if email in users:
        return False, "An account with this email already exists. Please Sign In.", None

    icon = "👨‍🌾" if "Farmer" in role else ("🔬" if "KVK" in role else "👤")
    new_user = {
        "name": name,
        "email": email,
        "pw_hash": _hash_pw(password),
        "role": role,
        "role_badge": role,
        "location": location or "India",
        "icon": icon,
    }
    users[email] = new_user
    save_users(users)
    st.session_state["user"] = new_user
    return True, f"Account created successfully! Welcome to Krishi Netra, {name}.", new_user


def quick_login(role_key: str) -> tuple[bool, str, dict[str, Any] | None]:
    """1-Click instant login for judges, farmers, or agronomists."""
    key_map = {
        "judge": "judge@krishinetra.ai",
        "farmer": "farmer@krishinetra.ai",
        "kvk": "kvk@krishinetra.ai",
    }
    email = key_map.get(role_key, "judge@krishinetra.ai")
    users = load_users()
    user = users.get(email, DEFAULT_USERS[email])
    st.session_state["user"] = user
    return True, f"Signed in as {user['name']} ({user['role_badge']})!", user


def logout() -> None:
    if "user" in st.session_state:
        del st.session_state["user"]
