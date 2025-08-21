import requests

APIKEY = None
ENDPOINT = None
_LAST_RESPONSE = None  # lưu kết quả gần nhất

def apikey(key: str) -> str:
    """Thiết lập API key"""
    global APIKEY
    APIKEY = key.strip()
    return APIKEY

def model(url: str) -> str:
    """Thiết lập endpoint đầy đủ từ Gemini (URL phải bắt đầu bằng http/https)"""
    global ENDPOINT
    if not (url.startswith("http://") or url.startswith("https://")):
        raise ValueError("Hãy dán URL đầy đủ từ Gemini.")
    ENDPOINT = url.strip()
    return ENDPOINT

def hoi(text: str):
    """Gửi câu hỏi lên API, lưu lại response"""
    global _LAST_RESPONSE
    if not ENDPOINT:
        raise ValueError("Hãy gọi model() trước khi dùng hoi().")

    url = ENDPOINT
    if APIKEY and "key=" not in url:
        if "?" in url:
            url += f"&key={APIKEY}"
        else:
            url += f"?key={APIKEY}"

    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"role": "user", "parts": [{"text": text}]}]}

    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    _LAST_RESPONSE = resp.json()

def traloi() -> str:
    """Lấy câu trả lời từ lần hoi() gần nhất"""
    if not _LAST_RESPONSE:
        raise ValueError("Chưa có câu hỏi nào. Hãy dùng hoi('...') trước.")
    try:
        return _LAST_RESPONSE["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        return str(_LAST_RESPONSE)