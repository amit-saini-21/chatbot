from typing import Dict


def build_default_appearance(role: Dict) -> str:
    role_type = (role or {}).get("role_type", "assistant")
    config = (role or {}).get("config", {})
    tone = config.get("tone", "friendly")
    style = config.get("style", "casual")

    role_appearance = {
        "friend": "mid-20s person, warm smile, natural everyday outfit, clean background",
        "girlfriend": "young adult woman, soft natural makeup, expressive eyes, stylish casual outfit",
        "boyfriend": "young adult man, clean haircut, confident posture, smart casual outfit",
        "teacher": "educational visual design style, clean diagram palette, whiteboard-inspired composition",
        "assistant": "minimal neutral digital illustration style",
    }

    base = role_appearance.get(role_type, role_appearance["assistant"])
    return f"{base}, {tone} tone, {style} visual style"


def build_image_prompt(user_message: str, role: Dict, appearance: str, intent_type: str) -> str:
    role_type = (role or {}).get("role_type", "assistant")
    config = (role or {}).get("config", {})
    tone = config.get("tone", "friendly")
    style = config.get("style", "casual")

    safety_constraints = (
        "safe content only, no nudity, no sexual content, no explicit content, "
        "no graphic violence, no hate symbols"
    )

    if role_type == "teacher" or intent_type == "diagram":
        return (
            "Create a clean educational diagram. "
            f"Topic: {user_message}. "
            "Use labels, arrows, and structured sections with high readability. "
            f"Visual style: {appearance}. "
            f"Tone: {tone}. Style: {style}. "
            "flat vector infographic, high clarity, high contrast, clean spacing, legible typography, white background. "
            "No human characters or faces, no portrait rendering. "
            f"{safety_constraints}."
        )

    return (
        f"Natural portrait scene based on: {user_message}. "
        f"Character appearance: {appearance}. "
        "same person, consistent face, consistent identity across sessions. "
        f"Role behavior style: {role_type}, tone {tone}, style {style}. "
        "photorealistic, candid expression, natural pose, subtle emotion, realistic skin texture, "
        "soft cinematic lighting, shallow depth of field, sharp focus on eyes, high detail, premium quality. "
        f"{safety_constraints}."
    )
