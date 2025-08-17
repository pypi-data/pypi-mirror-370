import json
import requests
from typing import Optional

from ._config import (
    API_KEY,
    DEFAULT_MODEL,
    OPENROUTER_URL,
    HTTP_REFERER,
    X_TITLE,
    SYSTEM_PROMPT,
)

# История НЕ храним (по ТЗ «минимально просто»),
# но оставляем задел на будущее, если захочешь включить:
_HISTORY = []  # не используется сейчас


def _headers():
    if not API_KEY or API_KEY.startswith("REPLACE_WITH_"):
        raise RuntimeError("В _config.py не задан API_KEY.")
    h = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    if HTTP_REFERER:
        h["HTTP-Referer"] = HTTP_REFERER
    if X_TITLE:
        h["X-Title"] = X_TITLE
    return h


def q(
    prompt: str,
    model: Optional[str] = None,
    echo: bool = True,
    max_tokens: int = 1500,
) -> str:
    """
    Отправляет запрос в OpenRouter с константным системным промптом и возвращает текст ответа.

    mistralai/mistral-7b-instruct:free

    :param prompt: пользовательский запрос
    :param model: id модели (если None — DEFAULT_MODEL из _config.py)
    :param echo: печатать ли ответ в stdout
    :param max_tokens: ограничение на длину ответа (помогает избежать 402 при нулевом балансе)
    :return: текст ответа модели
    """
    messages = []
    if SYSTEM_PROMPT:
        messages.append({"role": "system", "content": SYSTEM_PROMPT})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model or DEFAULT_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        # Возвращать usage, чтобы видеть реальные токены
        "usage": {"include": True},
        # Если история будет нужна, можно включить авто-урезание:
        # "transforms": ["middle-out"],
    }

    resp = requests.post(OPENROUTER_URL, headers=_headers(), data=json.dumps(payload), timeout=120)

    # Попробуем распарсить JSON в любом случае
    try:
        data = resp.json()
    except Exception:
        resp.raise_for_status()
        raise

    if resp.status_code >= 400:
        # Достаём читаемое сообщение об ошибке
        msg = None
        if isinstance(data, dict):
            msg = (data.get("error") or {}).get("message") or data.get("message")
        raise RuntimeError(f"OpenRouter error {resp.status_code}: {msg or data}")

    try:
        text = data["choices"][0]["message"]["content"]
    except Exception:
        raise RuntimeError(f"Unexpected response format: {data}")

    if echo:
        print(text)
    return None
