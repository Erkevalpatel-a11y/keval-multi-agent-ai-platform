import base64
import httpx
from app.config import settings

class AIProviderError(Exception):
    pass

class AIProvider:
    async def chat(self, messages: list[dict], image_data_url: str | None = None) -> str:
        if not settings.ai_base_url or not settings.ai_model or not settings.ai_api_key:
            raise AIProviderError(
                "No AI provider is configured. Set AI_BASE_URL, AI_MODEL and AI_API_KEY in backend/.env."
            )

        payload_messages = messages
        if image_data_url:
            payload_messages = [dict(m) for m in messages]
            payload_messages[-1] = {
                "role": "user",
                "content": [
                    {"type": "text", "text": messages[-1]["content"]},
                    {"type": "image_url", "image_url": {"url": image_data_url}},
                ],
            }

        url = settings.ai_base_url.rstrip("/") + "/chat/completions"
        headers = {"Authorization": f"Bearer {settings.ai_api_key}"}
        payload = {"model": settings.ai_model, "messages": payload_messages, "temperature": 0.2}

        async with httpx.AsyncClient(timeout=90) as client:
            r = await client.post(url, json=payload, headers=headers)
        if r.status_code >= 400:
            raise AIProviderError(f"AI provider returned HTTP {r.status_code}.")
        data = r.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            raise AIProviderError("AI provider returned an unexpected response format.")
