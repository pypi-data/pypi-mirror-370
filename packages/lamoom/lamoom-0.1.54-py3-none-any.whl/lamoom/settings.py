from dataclasses import dataclass, field
import json
import os

from lamoom.utils import parse_bool


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMP_SCRIPTS_DIR = os.environ.get(
    "LAMOOM_TEMP_SCRIPTS_DIR", os.path.join(BASE_DIR, "temp_scripts")
)
SAVE_PROMPTS_LOCALLY = os.environ.get("LAMOOM_SAVE_PROMPTS_LOCALLY", False)
ENVIRONMENT = os.environ.get("LAMOOM_ENVIRONMENT", "prod")

DEFAULT_MAX_BUDGET = os.environ.get("LAMOOM_DEFAULT_MAX_BUDGET", 120000)
DEFAULT_SAMPLE_MIN_BUDGET = os.environ.get("LAMOOM_DEFAULT_ANSWER_BUDGET", 12000)
DEFAULT_PROMPT_BUDGET = os.environ.get(
    "LAMOOM_DEFAULT_PROMPT_BUDGET", DEFAULT_MAX_BUDGET - DEFAULT_SAMPLE_MIN_BUDGET
)

EXPECTED_MIN_BUDGET_FOR_VALUABLE_INPUT = os.environ.get(
    "LAMOOM_EXPECTED_MIN_BUDGET_FOR_VALUABLE_INPUT", 100
)

SAFE_GAP_TOKENS: int = os.environ.get("LAMOOM_SAFE_GAP_TOKENS", 100)
SAFE_GAP_PER_MSG: int = os.environ.get("LAMOOM_SAFE_GAP_PER_MSG", 4)
DEFAULT_ENCODING = "cl100k_base"

USE_API_SERVICE = parse_bool(os.environ.get("LAMOOM_USE_API_SERVICE", True))
LAMOOM_API_URI = os.environ.get("LAMOOM_API_URI") or os.environ.get("FLOW_PROMPT_API_URI") or "https://api.lamoom.com"
LAMOOM_GOOGLE_SEARCH_RESULTS_COUNT = os.environ.get("LAMOOM_GOOGLE_SEARCH_RESULTS_COUNT", 3)
CACHE_PROMPT_FOR_EACH_SECONDS = int(
    os.environ.get("LAMOOM_CACHE_PROMPT_FOR_EACH_SECONDS", 5 * 60)
)  # 5 minutes by default
RECEIVE_PROMPT_FROM_SERVER = parse_bool(
    os.environ.get("LAMOOM_RECEIVE_PROMPT_FROM_SERVER", True)
)
SHOULD_INCLUDE_REASONING = parse_bool(os.environ.get("SHOULD_INCLUDE_REASONING", True))
PIPE_PROMPTS = {}

# Parse FALLBACK_MODELS from environment variable
# Can be either a list of model names or a dict with model names as keys and weights as values
fallback_models_env = os.environ.get("LAMOOM_FALLBACK_MODELS", "[]")
try:
    if fallback_models_env.startswith("{"):
        # Parse as dict with weights
        FALLBACK_MODELS = json.loads(fallback_models_env)
    else:
        # Parse as list
        FALLBACK_MODELS = json.loads(fallback_models_env)
except (json.JSONDecodeError, ValueError):
    # Default to empty list if parsing fails
    FALLBACK_MODELS = []

LAMOOM_CUSTOM_PROVIDERS = json.loads(
    os.getenv("custom_keys", os.getenv("LAMOOM_CUSTOM_PROVIDERS", "{}"))
)


@dataclass
class Secrets:
    API_TOKEN: str = field(default_factory=lambda: os.getenv("LAMOOM_API_TOKEN", os.getenv("FLOW_PROMPT_API_TOKEN")))
    OPENAI_API_KEY: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    CLAUDE_API_KEY: str = field(default_factory=lambda: os.getenv("CLAUDE_API_KEY"))
    GEMINI_API_KEY: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY"))
    NEBIUS_API_KEY: str = field(default_factory=lambda: os.getenv("NEBIUS_API_KEY"))
    OPENROUTER_KEY: str = field(default_factory=lambda: os.getenv("OPENROUTER_KEY"))
    CUSTOM_API_KEY: str = field(default_factory=lambda: os.getenv("CUSTOM_API_KEY"))
    OPENAI_ORG: str = field(default_factory=lambda: os.getenv("OPENAI_ORG"))
    azure_keys: dict = field(
        default_factory=lambda: json.loads(
            os.getenv("azure_keys", os.getenv("AZURE_OPENAI_KEYS", os.getenv("AZURE_KEYS", "{}")))
        )
    )
    custom_keys: dict = field(
        default_factory=lambda: json.loads(
            os.getenv("custom_keys", os.getenv("LAMOOM_CUSTOM_PROVIDERS", "{}"))
        )
    )
