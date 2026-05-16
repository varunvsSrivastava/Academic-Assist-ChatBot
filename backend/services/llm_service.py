import re
import threading
import time
from openai import OpenAI
from backend.app.config import config

client = OpenAI(api_key=config.OPENAI_API_KEY) if config.OPENAI_API_KEY else None


_LAST_OPENAI_CALL_TS = 0.0
_OPENAI_CALL_LOCK = threading.Lock()


def _wait_for_call_window() -> None:
    global _LAST_OPENAI_CALL_TS

    min_interval = max(config.LLM_MIN_CALL_INTERVAL_SECONDS, 0.0)
    if min_interval == 0:
        return

    with _OPENAI_CALL_LOCK:
        now = time.monotonic()
        elapsed = now - _LAST_OPENAI_CALL_TS
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        _LAST_OPENAI_CALL_TS = time.monotonic()


def _safe_chat_completion(messages, temperature):
    last_exc = None
    max_retries = max(config.LLM_MAX_RETRIES, 0)

    for attempt in range(max_retries + 1):
        try:
            _wait_for_call_window()
            return client.chat.completions.create(
                model=config.MODEL_NAME,
                messages=messages,
                temperature=temperature,
            )
        except Exception as exc:
            last_exc = exc
            text = str(exc).lower()

            # No retry for invalid key/model/quota errors.
            fatal_markers = {
                "insufficient_quota",
                "invalid_api_key",
                "model_not_found",
                "does not exist",
            }
            if any(marker in text for marker in fatal_markers):
                raise

            is_rate_limit = ("rate_limit_exceeded" in text) or ("requests per min" in text)
            if not is_rate_limit or attempt >= max_retries:
                raise

            backoff = config.LLM_RETRY_BASE_SECONDS * (2 ** attempt)
            time.sleep(backoff)

    if last_exc is not None:
        raise last_exc


def _friendly_openai_error(exc: Exception) -> str:
    """
    Convert low-level OpenAI exceptions into actionable user-facing guidance.
    """
    raw = str(exc)
    text = raw.lower()

    if "insufficient_quota" in text or "exceeded your current quota" in text:
        return (
            "OpenAI request failed: insufficient quota (429). "
            "Add billing/credits in your OpenAI project, then retry."
        )

    if "invalid_api_key" in text or "incorrect api key" in text:
        return (
            "OpenAI request failed: invalid API key. "
            "Update OPENAI_API_KEY in your .env and restart the app."
        )

    if "model_not_found" in text or "does not exist" in text:
        return (
            "OpenAI request failed: model access issue. "
            "Verify MODEL_NAME and project model permissions."
        )

    if "rate_limit_exceeded" in text or "requests per min" in text:
        return (
            "OpenAI request failed: rate limit reached. "
            "Retry shortly or reduce request frequency."
        )

    return (
        "LLM request failed. Check API key, model access, and quota. "
        f"Details: {type(exc).__name__}"
    )


def llm_generate(query: str, context: str) -> str:
    if client is None:
        return "OPENAI_API_KEY is not set. Add it to your environment or .env to enable generated answers."

    prompt = f"""
    You are an academic assistant.
    Answer clearly and concisely using the provided context when available.

    Question:
    {query}

    Context:
    {context}
    """

    try:
        response = _safe_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=config.TEMPERATURE,
        )
        return response.choices[0].message.content or ""
    except Exception as exc:
        return _friendly_openai_error(exc)


def llm_quick_score(query: str) -> float:
    if client is None:
        return 1.0

    prompt = f"""
    Score the complexity of this academic question from 0.0 to 1.0.
    Return ONLY in this format: Score: <number>

    Question:
    {query}
    """

    try:
        response = _safe_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        text = response.choices[0].message.content or ""
        return parse_score(text)
    except Exception:
        return 1.0


def llm_improve(answer: str, feedback: str) -> str:
    if client is None:
        return answer

    prompt = f"""
    Improve the following answer using the feedback.
    Return only the improved answer text.

    Original Answer:
    {answer}

    Feedback:
    {feedback}
    """

    try:
        response = _safe_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=config.TEMPERATURE,
        )
        return response.choices[0].message.content or answer
    except Exception:
        return answer


def parse_score(text: str) -> float:
    """
    Extract score from LLM output
    Expected format:
    Score: 0.8
    """
    match = re.search(r"Score:\s*([0-9]*\.?[0-9]+)", text)

    if match:
        score = float(match.group(1))
        return min(max(score, 0.0), 1.0)

    return 0.5  # fallback


def parse_feedback(text: str) -> str:
    """
    Extract feedback section
    """
    if "Feedback:" in text:
        return text.split("Feedback:")[1].strip()

    return text


def llm_evaluate(answer, context):
    if client is None:
        return 1.0, "OPENAI_API_KEY is not set. Evaluation fallback applied."

    prompt = f"""
    Evaluate this answer strictly.

    Criteria:
    - Accuracy
    - Completeness
    - Relevance

    Output EXACTLY:
    Score: <0 to 1>
    Feedback: <text>

    Answer:
    {answer}

    Context:
    {context}
    """

    try:
        response = _safe_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )

        text = response.choices[0].message.content

        score = parse_score(text)
        feedback = parse_feedback(text)

        return score, feedback
    except Exception as exc:
        return 1.0, f"Evaluation fallback applied. {_friendly_openai_error(exc)}"