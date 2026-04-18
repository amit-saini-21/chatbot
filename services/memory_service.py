# services/memory_service.py

import re

from models import role_model as role_db


def should_save_memory(user_message):
    text = (user_message or "").lower()
    save_phrases = [
        "save this",
        "remember this",
        "save it",
        "remember it",
        "note this",
        "store this",
        "keep this in mind",
        "Save kar lena",
        "yaad rakhna",
        "puch lena",
        "yaad kar lena",
    ]
    return any(phrase in text for phrase in save_phrases)


def _extract_name_fact(text):
    match = re.search(r"\bmy name is\s+([a-zA-Z][a-zA-Z\s]{1,40})", text, re.IGNORECASE)
    if match:
        return f"User name is {match.group(1).strip().title()}"
    return None


def _extract_age_fact(text):
    match = re.search(r"\b(?:i am|i'm|my age is)\s+(\d{1,3})\b", text, re.IGNORECASE)
    if not match:
        return None
    age = int(match.group(1))
    if 1 <= age <= 120:
        return f"User age is {age}"
    return None


def _extract_preference_fact(text):
    preference_patterns = [
        r"\bi like\s+(.+)",
        r"\bi love\s+(.+)",
        r"\bi hate\s+(.+)",
        r"\bmy favorite\s+(.+)",
    ]
    for pattern in preference_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = match.group(1).strip().rstrip(".!?")
            if value:
                return f"Preference: {value[:120]}"
    return None


def extract_memories(user_message, save_requested=False):
    text = (user_message or "").strip()
    if not text:
        return []

    facts = []
    for extractor in (_extract_name_fact, _extract_age_fact, _extract_preference_fact):
        fact = extractor(text)
        if fact:
            facts.append(fact)

    if save_requested:
        explicit_fact = f"User asked to remember: {text[:180]}"
        facts.append(explicit_fact)

    unique = []
    seen = set()
    for fact in facts:
        key = fact.lower().strip()
        if key and key not in seen:
            seen.add(key)
            unique.append(fact)
    return unique


def _profile_facts(user):
    if not user:
        return []
    profile = user.get("profile", {}) or {}

    facts = []
    name = (profile.get("name") or "").strip()
    age = profile.get("age")
    tags = profile.get("tags") or []

    if name:
        facts.append(f"User name is {name}")
    if isinstance(age, int) and 1 <= age <= 120:
        facts.append(f"User age is {age}")
    if isinstance(tags, list) and tags:
        clean_tags = [str(tag).strip() for tag in tags if str(tag).strip()]
        if clean_tags:
            facts.append("User tags: " + ", ".join(clean_tags[:10]))

    return facts


def get_relevant_memory(role):
    memory = role.get("memory", []) if role else []
    return memory[-20:]


def build_memory_context(role, user):
    context = _profile_facts(user) + get_relevant_memory(role)

    unique = []
    seen = set()
    for item in context:
        key = str(item).lower().strip()
        if key and key not in seen:
            seen.add(key)
            unique.append(str(item))
    return unique[-25:]


def update_memory(role_id, new_memories):
    if not new_memories:
        return

    if isinstance(new_memories, str):
        new_memories = [new_memories]

    role = role_db.get_role(role_id)
    if not role:
        return

    existing = role.get("memory", []) or []
    merged = existing + [m for m in new_memories if m]

    unique = []
    seen = set()
    for item in merged:
        normalized = str(item).strip()
        key = normalized.lower()
        if normalized and key not in seen:
            seen.add(key)
            unique.append(normalized)

    role_db.update_memory(role_id, unique[-50:])


def summarize_chat(messages):
    if not messages:
        return None

    last_user_msgs = [m["text"] for m in messages if m.get("sender") == "user" and m.get("text")]
    if not last_user_msgs:
        return None

    summary = "User talked about: " + ", ".join(last_user_msgs[-2:])
    return summary