"""Unified LLM backend — supports Demo, OpenAI API, and Ollama modes."""
import json
import logging
import os
from src.config import MODE, OPENAI_API_KEY, LLM_MODEL, OLLAMA_MODEL, OLLAMA_BASE_URL, MAX_RETRIES

logger = logging.getLogger(__name__)


def get_mode():
    """Get current mode from env (can be changed at runtime via Streamlit)."""
    return os.getenv("LEARNFORGE_MODE", MODE)


def call_llm(messages: list, temperature: float = 0.7, max_tokens: int = 2000,
             json_mode: bool = True, model: str | None = None) -> dict | str:
    """
    Unified LLM call. Routes to demo/api/ollama based on current mode.
    Returns parsed dict if json_mode, else raw string.
    """
    mode = get_mode()

    if mode == "demo":
        return _demo_response(messages, json_mode)
    elif mode == "ollama":
        return _ollama_call(messages, temperature, max_tokens, json_mode, model)
    else:
        return _openai_call(messages, temperature, max_tokens, json_mode, model)


def _openai_call(messages, temperature, max_tokens, json_mode, model):
    """Call OpenAI API."""
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
    model = model or LLM_MODEL

    for attempt in range(MAX_RETRIES + 1):
        try:
            kwargs = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}

            response = client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content

            if json_mode:
                return json.loads(content)
            return content
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parse error (attempt {attempt + 1}): {e}")
            if attempt == MAX_RETRIES:
                return {"_error": f"JSON parse failure: {e}"}
        except Exception as e:
            logger.warning(f"API error (attempt {attempt + 1}): {e}")
            if attempt == MAX_RETRIES:
                return {"_error": f"API failure: {e}"}
    return {"_error": "Unexpected retry loop exit"}


def _ollama_call(messages, temperature, max_tokens, json_mode, model):
    """Call local Ollama server."""
    import requests
    model = model or OLLAMA_MODEL

    # Convert to Ollama format
    prompt_parts = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "system":
            prompt_parts.append(f"System: {content}")
        elif role == "user":
            prompt_parts.append(f"User: {content}")
        else:
            prompt_parts.append(f"Assistant: {content}")

    if json_mode:
        prompt_parts.append("\nRespond with valid JSON only. No markdown, no explanation outside JSON.")

    prompt = "\n\n".join(prompt_parts)

    try:
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": temperature, "num_predict": max_tokens},
            },
            timeout=120,
        )
        resp.raise_for_status()
        content = resp.json().get("response", "")

        if json_mode:
            # Try to extract JSON
            content = content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            start = content.find("{")
            end = content.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(content[start:end])
            return {"_error": f"Could not parse JSON from Ollama response"}
        return content
    except Exception as e:
        logger.error(f"Ollama error: {e}")
        return {"_error": f"Ollama error: {e}"}


def _demo_response(messages, json_mode):
    """Return a placeholder indicating demo mode — actual demo data loaded from files."""
    return {"_demo": True, "_message": "Demo mode — using pre-generated content"}
