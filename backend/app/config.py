import os
from dotenv import load_dotenv

load_dotenv()


def _as_bool(value: str, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    
    # Model configs
    MODEL_NAME = "gpt-4o-mini"
    TEMPERATURE = 0.3
    
    # Threshold for routing
    CONFIDENCE_THRESHOLD = 0.7
    RETRIEVAL_SCORE_THRESHOLD = 0.35
    MAX_REFINEMENT_ITERATIONS = int(os.getenv("MAX_REFINEMENT_ITERATIONS", "1"))

    # Rate-limit mitigation knobs
    USE_LLM_QUERY_SCORER = _as_bool(os.getenv("USE_LLM_QUERY_SCORER"), False)
    LLM_MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "2"))
    LLM_RETRY_BASE_SECONDS = float(os.getenv("LLM_RETRY_BASE_SECONDS", "1.0"))
    LLM_MIN_CALL_INTERVAL_SECONDS = float(os.getenv("LLM_MIN_CALL_INTERVAL_SECONDS", "0.6"))

config = Config()