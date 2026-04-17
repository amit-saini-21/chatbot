import re
from dataclasses import dataclass


@dataclass(frozen=True)
class SafetyFilterResult:
    is_safe: bool
    category: str
    reason: str


_BLOCKED_PATTERNS = {
    "sexual_explicit": [
        re.compile(r"\b(nude|naked|sex|sexual|porn|nsfw|erotic|explicit|fetish|lingerie)\b", re.IGNORECASE),
        re.compile(r"\b(topless|bikini\s+model|bedroom\s+scene)\b", re.IGNORECASE),
        re.compile(r"\b(nanga|nangi|ashleel|ganda\s+content|adult\s+photo|sexy)\b", re.IGNORECASE),
        re.compile(r"(नंगा|नंगी|अश्लील|सेक्सी|पोर्न|न्यूड)", re.IGNORECASE),
        re.compile(r"(ਨੰਗਾ|ਨੰਗੀ|ਅਸ਼ਲੀਲ|ਸੈਕਸੀ|ਪੋਰਨ)", re.IGNORECASE),
        re.compile(r"(નગ્ન|અશ્લીલ|સેક્સી|પોર્ન)", re.IGNORECASE),
    ],
    "minor_related": [
        re.compile(r"\b(child|kid|teen|underage|schoolgirl|schoolboy)\b", re.IGNORECASE),
        re.compile(r"\b(minor|bacchi|baccha|under\s*18|teen\s+girl|teen\s+boy)\b", re.IGNORECASE),
        re.compile(r"(नाबालिग|बच्चा|बच्ची|कम उम्र)", re.IGNORECASE),
        re.compile(r"(ਨਾਬਾਲਗ|ਬੱਚਾ|ਬੱਚੀ|ਘੱਟ ਉਮਰ)", re.IGNORECASE),
        re.compile(r"(નાબાલિક|બાળક|બાળકી|ઓછી ઉંમર)", re.IGNORECASE),
    ],
    "graphic_violence": [
        re.compile(r"\b(gore|bloody|beheading|dismember|torture|graphic\s+violence)\b", re.IGNORECASE),
        re.compile(r"\b(khoon|katna|hinsak|maar\s*do|murder\s+scene)\b", re.IGNORECASE),
        re.compile(r"(खून|काटना|हिंसक|हत्या|यातना)", re.IGNORECASE),
        re.compile(r"(ਖੂਨ|ਕੱਟਣਾ|ਹਿੰਸਕ|ਹੱਤਿਆ|ਤਸ਼ੱਦਦ)", re.IGNORECASE),
        re.compile(r"(લોહી|કાપવું|હિંસક|હત્યા|યાતના)", re.IGNORECASE),
    ],
    "self_harm": [
        re.compile(r"\b(suicide|self harm|kill myself|cutting)\b", re.IGNORECASE),
        re.compile(r"\b(aatmahatya|khud\s*ko\s*marna|self\s*injury)\b", re.IGNORECASE),
        re.compile(r"(आत्महत्या|खुद को मारना|स्वयं को नुकसान)", re.IGNORECASE),
        re.compile(r"(ਆਤਮਹੱਤਿਆ|ਆਪਣੇ ਆਪ ਨੂੰ ਮਾਰਨਾ|ਆਪਣੇ ਆਪ ਨੂੰ ਨੁਕਸਾਨ)", re.IGNORECASE),
        re.compile(r"(આત્મહત્યા|પોતાને મારી નાખવું|પોતાને નુકસાન)", re.IGNORECASE),
    ],
    "hate_or_extremism": [
        re.compile(r"\b(nazi|terrorist propaganda|hate symbol)\b", re.IGNORECASE),
        re.compile(r"\b(atankwadi\s+propaganda|nafrat\s+symbol)\b", re.IGNORECASE),
        re.compile(r"(आतंकवादी प्रचार|नफरत प्रतीक)", re.IGNORECASE),
        re.compile(r"(ਅੱਤਵਾਦੀ ਪ੍ਰਚਾਰ|ਨਫਰਤ ਚਿੰਨ੍ਹ)", re.IGNORECASE),
        re.compile(r"(આતંકવાદી પ્રચાર|નફરત ચિહ્ન)", re.IGNORECASE),
    ],
}


def evaluate_image_safety(user_message: str) -> SafetyFilterResult:
    text = (user_message or "").strip()
    if not text:
        return SafetyFilterResult(True, "none", "Prompt is empty.")

    for category, patterns in _BLOCKED_PATTERNS.items():
        for pattern in patterns:
            if pattern.search(text):
                return SafetyFilterResult(
                    is_safe=False,
                    category=category,
                    reason="Request includes disallowed unsafe content.",
                )

    return SafetyFilterResult(True, "none", "Prompt passed safety checks.")


def safe_fallback_message() -> str:
    return (
        "I cannot help with unsafe image content. "
        "If you want, I can create a safe alternative image prompt instead."
    )
