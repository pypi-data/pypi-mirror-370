import os
from typing import Dict, List
import re
from urllib.parse import urlparse
from services.get_blocklist_service import get_blocked_hosts

# Full domains to block (matches exact or subdomain)
SHADOW_AI_DOMAINS = [
    "chatgpt.com",
    "openai.com",
    "poe.com",
    "perplexity.ai",
    "huggingface.co",
    "anthropic.com",
    "groq.com",
    "openrouter.ai",
    "llama.family",
    "mistral.ai",
    "cohere.ai"
]

api_key = os.getenv("ZT_PROXY_API_KEY")
if not api_key:
    raise ValueError("ZT_PROXY_API_KEY environment variable is not set.")

blocked_hosts = get_blocked_hosts(api_key)

def extract_domains(urls: List[str]) -> List[str]:
    """
    Extracts domains from a list of URLs.
    """
    domains = []
    for url in urls:
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path  # Handle cases without scheme
        domain = domain.lower().strip()
        if domain.startswith("www."):
            domain = domain[4:]
        domains.append(domain)
    return domains

blocked_domains = extract_domains(blocked_hosts)
for domain in blocked_domains:
    if domain not in SHADOW_AI_DOMAINS:
        SHADOW_AI_DOMAINS.append(domain)

# AI model keywords for fallback body analysis
SHADOW_AI_MODEL_KEYWORDS = [
    "gpt", "llama", "claude", "mistral", "mixtral", "command-r", "phi", "cohere", "zephyr"
]

def is_shadow_ai_request(
    host: str,
    path: str,
    headers: Dict[str, str],
    body: str,
    parsed_body: Dict
) -> bool:
    """Returns True if this request is suspected to be going to a Shadow AI system."""

    host_l = host.lower()
    path_l = path.lower()

    print(f"shadow ai domains: {SHADOW_AI_DOMAINS}")

    # Rule 1: Hostname matches domain or subdomain
    for domain in SHADOW_AI_DOMAINS:
        if host_l == domain or host_l.endswith(f".{domain}"):
            return True

    # Rule 2: Path hints (common for AI inference APIs)
    if re.search(r"/v\d+/(chat|completion|generate|inference)", path_l):
        return True

    # Rule 3: Model name in body
    if isinstance(parsed_body, dict):
        for key in ["model", "model_name", "llm"]:
            model_val = parsed_body.get(key, "").lower()
            if any(k in model_val for k in SHADOW_AI_MODEL_KEYWORDS):
                return True
        # Rule 4: Known AI-related keys in body
        if any(key in parsed_body for key in ["used_input_tokens", "prompt", "max_tokens", "temperature"]):
            return True
    elif isinstance(parsed_body, list):
        # Try to find dicts inside the list and apply same rules
        for item in parsed_body:
            if isinstance(item, dict):
                for key in ["model", "model_name", "llm"]:
                    model_val = item.get(key, "").lower()
                    if any(k in model_val for k in SHADOW_AI_MODEL_KEYWORDS):
                        return True
                if any(key in item for key in ["used_input_tokens", "prompt", "max_tokens", "temperature"]):
                    return True
    return False
