import base64
import os
import time
from typing import Optional, Tuple
import dotenv
import requests

dotenv.load_dotenv()


# HF_MODEL_URL = os.getenv(
#     "HF_IMAGE_MODEL_URL",
#     "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1",
# )
# HF_MODEL_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
#HF_MODEL_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
HF_MODEL_URL = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3.1-8B-Instruct"

HF_TIMEOUT_SECONDS = int(os.getenv("HF_TIMEOUT_SECONDS", "80"))
HF_MAX_RETRIES = int(os.getenv("HF_MAX_RETRIES", "3"))

_SESSION = requests.Session()


def _build_headers() -> dict:
    token = os.getenv("HF_TOKEN", "").strip()
    if not token:
        return {}
    #print(token)
    return {"Authorization": f"Bearer {token}"}


def _extract_provider_error(response: requests.Response) -> str:
    content_type = (response.headers.get("content-type") or "").lower()
    if "application/json" in content_type:
        try:
            payload = response.json()
            if isinstance(payload, dict):
                if payload.get("error"):
                    return str(payload.get("error"))
        except Exception:
            pass

    return f"Image provider returned status {response.status_code}."


def generate_image_base64(prompt: str, timeout: int = HF_TIMEOUT_SECONDS) -> Tuple[Optional[str], Optional[str]]:
    headers = _build_headers()
    #print(headers)
    if not headers:
        return None, "Missing HuggingFace token."

    payload = {
        "inputs": prompt,
        "options": {
            "wait_for_model": True,
            "use_cache": False,
        },
    }

    attempt = 0
    while attempt < max(1, HF_MAX_RETRIES):
        attempt += 1
        try:
            response = _SESSION.post(
                HF_MODEL_URL,
                headers=headers,
                json=payload,
                timeout=timeout,
            )
        except requests.RequestException:
            if attempt >= HF_MAX_RETRIES:
                return None, "Image provider request failed."
            time.sleep(min(2 ** (attempt - 1), 4))
            continue

        if response.status_code == 200:
            image_bytes = response.content
            if not image_bytes:
                return None, "Image provider returned empty payload."

            image_b64 = base64.b64encode(image_bytes).decode("utf-8")
            return image_b64, None

        # Retry on temporary backend/load issues.
        if response.status_code in {429, 500, 502, 503, 504} and attempt < HF_MAX_RETRIES:
            time.sleep(min(2 ** (attempt - 1), 4))
            continue

        return None, _extract_provider_error(response)

    return None, "Image provider request failed after retries."
