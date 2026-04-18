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
        "save kar lena",
        "yaad rakhna",
        "puch lena",
        "yaad kar lena",
    ]
    return any(phrase in text for phrase in save_phrases)


def _normalize_items(items):
    if items is None:
        return []
    if isinstance(items, str):
        items = [items]

    cleaned = []
    seen = set()
    for item in items:
        text = str(item).strip()
        key = text.lower()
        if text and key not in seen:
            seen.add(key)
            cleaned.append(text)
    return cleaned


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
        facts.append(f"User asked to remember: {text[:180]}")

    return _normalize_items(facts)


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


def get_relevant_memory(role, limit=20):
    memory = role.get("memory", []) if role else []
    return list(memory)[-limit:]


def build_memory_context(role, user, short_term_messages=None, short_term_limit=5):
    context = _profile_facts(user) + get_relevant_memory(role)

    if short_term_messages:
        recent_messages = short_term_messages[-short_term_limit:]
        chat_snippets = []
        for message in recent_messages:
            sender = message.get("sender", "user")
            text = (message.get("text") or "").strip()
            if text:
                chat_snippets.append(f"{sender}: {text}")
        if chat_snippets:
            context.extend(chat_snippets)

    return _normalize_items(context)[-25:]


def update_memory(role_id, new_memories, user_id=None):
    normalized = _normalize_items(new_memories)
    if not normalized:
        return False

    role = role_db.get_role(role_id, user_id=user_id)
    if not role:
        return False

    existing = _normalize_items(role.get("memory", []))
    merged = _normalize_items(existing + normalized)
    return role_db.update_memory(role_id, merged[-50:], user_id=user_id)


def summarize_chat(messages):
    if not messages:
        return None

    last_user_msgs = [m.get("text") for m in messages if m.get("sender") == "user" and m.get("text")]
    if not last_user_msgs:
        return None

    return "User talked about: " + ", ".join(last_user_msgs[-2:])