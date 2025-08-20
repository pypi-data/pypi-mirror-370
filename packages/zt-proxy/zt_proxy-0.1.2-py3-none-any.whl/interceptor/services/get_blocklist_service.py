# services/proxy_block_service.py
import os
import requests
from typing import List

API_URL = "https://dev-settings.zerotrusted.ai/api/proxyblockfeatures/by-token"

def get_blocked_hosts(api_key) -> List[str]:
    """
    Fetches the list of blocked hosts from the ZeroTrusted API and returns only their host names.
    
    Returns:
        List[str]: A list of hostName strings.
    Raises:
        Exception: If the API call fails or the response is invalid.
    """
    headers = {
        "Accept": "application/json",
        "X-Custom-Token": api_key
    }

    print('invoking blocked hosts')
    try:
        response = requests.get(API_URL, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Extract hostName values from the list of dicts
        return [item["hostName"] for item in data if "hostName" in item]
    except requests.RequestException as e:
        raise Exception(f"Failed to fetch blocked hosts: {e}")
    except ValueError:
        raise Exception("Invalid JSON response from API.")
