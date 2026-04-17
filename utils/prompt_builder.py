def build_prompt(role, messages, user_input, memory):
    role_config = role.get("config", {}) if role else {}
    role_type = role.get("role_type", "assistant") if role else "assistant"
    tone = role_config.get("tone", "friendly")
    style = role_config.get("style", "casual")

    system = f"""
You are a {role_type}.

Personality Rules:
- Tone: {tone}
- Style: {style}

Behavior Guidelines:
- Stay consistent with your role at all times
- Do not break character
- Keep responses natural and engaging
- Avoid any explicit, abusive, or unsafe content
- If user asks inappropriate things, politely redirect

"""

    memory_text = ""
    if memory:
        memory_text = "Known Facts About User:\n" + "\n".join(
            [f"- {m}" for m in memory]
        )

    chat_history = "\n".join(
        [f"{m.get('sender', 'user')}: {m.get('text', '')}" for m in (messages or [])]
    )

    prompt = f"""
{system}

{memory_text}

Recent Conversation:
{chat_history}

User: {user_input}

Respond appropriately:
"""

    return prompt