import os
import json
from typing import Optional


DEFAULT_CONFIG_PATHS = [
    os.path.join(os.getcwd(), "config.json"),
    os.path.expanduser("~/.config/trading-indicators/config.json"),
    os.path.expanduser("~/.trading-indicators.json"),
]


def load_token(explicit_token: Optional[str] = None, config_path: Optional[str] = None) -> str:
    """Resolve API token from (precedence):
    1) explicit_token argument
    2) env var BITQUERY_TOKEN or BITQUERY_OAUTH_TOKEN
    3) config json file with key "oauth_token" or "token"
    Raises ValueError if not found.
    """
    if explicit_token:
        return explicit_token

    env_token = os.getenv("BITQUERY_TOKEN") or os.getenv("BITQUERY_OAUTH_TOKEN")
    if env_token:
        return env_token

    candidate_paths = [config_path] if config_path else DEFAULT_CONFIG_PATHS
    for path in candidate_paths:
        if not path:
            continue
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                token = data.get("oauth_token") or data.get("token")
                if token:
                    return token
            except Exception:
                # Silently ignore malformed config and continue searching
                pass

    raise ValueError(
        "Bitquery token not found. Set env var BITQUERY_TOKEN, pass --token, or add oauth_token to config.json"
    )


