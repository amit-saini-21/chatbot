import re
from dataclasses import dataclass


@dataclass(frozen=True)
class IntentResult:
    is_image_request: bool
    intent_type: str
    confidence: float
    wants_diagram: bool


# Weighted signals keep this extendable and stronger than plain keyword checks.
_INTENT_PATTERNS = {
    "request_phrase": [
        re.compile(r"\b(can you|could you|please|show me|send me|make me|create|generate|draw)\b", re.IGNORECASE),
        re.compile(r"\b(i want|i need)\b", re.IGNORECASE),
        re.compile(r"\b(banao|banado|banayiye|dikhao|dikha do|bhejo|mujhe chahiye)\b", re.IGNORECASE),
        re.compile(r"\b(banavo|batavo|moklo|mane joie)\b", re.IGNORECASE),
        re.compile(r"\b(bnao|dikhao|bhejo|chaahida)\b", re.IGNORECASE),
        re.compile(r"(दिखाओ|बनाओ|भेजो|मुझे चाहिए|बना दो)", re.IGNORECASE),
        re.compile(r"(ਬਣਾ|ਬਣਾਓ|ਦਿਖਾ|ਭੇਜ|ਚਾਹੀਦਾ)", re.IGNORECASE),
        re.compile(r"(બનાવો|બતાવો|મોકલો|મને જોઈએ)", re.IGNORECASE),
    ],
    "visual_object": [
        re.compile(r"\b(image|picture|pic|photo|wallpaper|portrait|selfie|render|illustration|artwork)\b", re.IGNORECASE),
        re.compile(r"\b(tasveer|photo|image|pic|selfie|chitra|diagram)\b", re.IGNORECASE),
        re.compile(r"(तस्वीर|फोटो|इमेज|चित्र|सेल्फी|डायग्राम)", re.IGNORECASE),
        re.compile(r"(ਤਸਵੀਰ|ਫੋਟੋ|ਚਿੱਤਰ|ਸੈਲਫੀ|ਡਾਇਗ੍ਰਾਮ)", re.IGNORECASE),
        re.compile(r"(ફોટો|છબી|ચિત્ર|સેલ્ફી|ડાયાગ્રામ)", re.IGNORECASE),
    ],
    "creation_action": [
        re.compile(r"\b(generate|create|draw|design|render|illustrate|show)\b", re.IGNORECASE),
        re.compile(r"\b(banao|banavo|draw|render|dikhao|dikhavo|illustrate)\b", re.IGNORECASE),
        re.compile(r"(बनाओ|खींचो|दिखाओ|तैयार करो)", re.IGNORECASE),
        re.compile(r"(ਬਣਾਓ|ਖਿੱਚੋ|ਦਿਖਾਓ|ਤਿਆਰ ਕਰੋ)", re.IGNORECASE),
        re.compile(r"(બનાવો|દોરો|બતાવો|તૈયાર કરો)", re.IGNORECASE),
    ],
}

_DIAGRAM_PATTERNS = [
    re.compile(r"\b(diagram|flowchart|flow chart|chart|process map|mind map|architecture|pipeline|schema|block diagram)\b", re.IGNORECASE),
    re.compile(r"\b(explain with|show)\s+(a\s+)?(diagram|chart|flow)\b", re.IGNORECASE),
    re.compile(r"\b(flow|chart|diagram|process)\s+(banao|banavo|dikhao)\b", re.IGNORECASE),
    re.compile(r"(डायग्राम|फ्लोचार्ट|चार्ट|प्रोसेस मैप|ब्लॉक डायग्राम)", re.IGNORECASE),
    re.compile(r"(ਡਾਇਗ੍ਰਾਮ|ਫਲੋਚਾਰਟ|ਚਾਰਟ|ਪ੍ਰੋਸੈਸ ਮੈਪ|ਬਲਾਕ ਡਾਇਗ੍ਰਾਮ)", re.IGNORECASE),
    re.compile(r"(ડાયાગ્રામ|ફ્લોચાર્ટ|ચાર્ટ|પ્રોસેસ મેપ|બ્લોક ડાયાગ્રામ)", re.IGNORECASE),
]

_EDUCATION_PATTERNS = [
    re.compile(r"\b(teach|lesson|class|study|explain|educational|learning|tutorial|concept|chapter)\b", re.IGNORECASE),
    re.compile(r"\b(samjhao|samjhaao|padhai|lesson|adhyayan|concept)\b", re.IGNORECASE),
    re.compile(r"(पढ़ाई|समझाओ|पाठ|अध्याय|शिक्षा|सीखना)", re.IGNORECASE),
    re.compile(r"(ਪੜ੍ਹਾਈ|ਸਮਝਾਓ|ਪਾਠ|ਸਿੱਖਿਆ|ਸਿੱਖਣਾ)", re.IGNORECASE),
    re.compile(r"(અભ્યાસ|સમજાવો|પાઠ|શિક્ષણ|શીખવું)", re.IGNORECASE),
]

_FALSE_POSITIVE_PATTERNS = [
    re.compile(r"\bimagine\b", re.IGNORECASE),
    re.compile(r"\bimage processing\b", re.IGNORECASE),
    re.compile(r"\bprofile image url\b", re.IGNORECASE),
]


def _score_intent(message: str) -> float:
    score = 0.0

    for pattern in _INTENT_PATTERNS["request_phrase"]:
        if pattern.search(message):
            score += 0.35
            break

    for pattern in _INTENT_PATTERNS["visual_object"]:
        if pattern.search(message):
            score += 0.40
            break

    for pattern in _INTENT_PATTERNS["creation_action"]:
        if pattern.search(message):
            score += 0.25
            break

    # Direct imperative structure gives extra confidence.
    if re.match(r"^\s*(generate|create|draw|show)\b", message, flags=re.IGNORECASE):
        score += 0.20

    if re.match(r"^\s*(बनाओ|दिखाओ|बना दो|ਬਣਾਓ|ਦਿਖਾਓ|બનાવો|બતાવો)\b", message, flags=re.IGNORECASE):
        score += 0.20

    if any(pattern.search(message) for pattern in _FALSE_POSITIVE_PATTERNS):
        score -= 0.45

    return max(0.0, min(score, 1.0))


def detect_image_intent(user_message: str) -> IntentResult:
    text = (user_message or "").strip()
    if not text:
        return IntentResult(False, "text", 0.0, False)

    confidence = _score_intent(text)
    wants_diagram = any(pattern.search(text) for pattern in _DIAGRAM_PATTERNS)
    educational_context = any(pattern.search(text) for pattern in _EDUCATION_PATTERNS)

    if wants_diagram and educational_context:
        return IntentResult(True, "diagram", max(confidence, 0.65), True)

    if wants_diagram:
        return IntentResult(True, "diagram", max(confidence, 0.55), True)

    is_image_request = confidence >= 0.55
    intent_type = "image" if is_image_request else "text"

    return IntentResult(is_image_request, intent_type, confidence, False)
