
import httpx
import json

async def get_compliance_report(pii_entities, request_body, token):
    """
    Calls the ZeroTrusted compliance report API and returns the compliance data.

    Args:
        pii_entities (list): List of PII entities (e.g., [["Alex", "Firstname"], ...])
        request_body (str): The original request body or prompt.
        token (str): Bearer token for authorization.

    Returns:
        dict: Compliance report data from the API response.
    """
    url = "https://dev-agents.zerotrusted.ai/zt-ml/api/v1/get-compliance-reports-v2"
    payload = {
        "compliance_array": [
            "gdpr", "ccpa", "hipaa", "hitech", "hitrust", "pci_dss", "glba", "lgpd", "appi"
        ],
        "compliance_report": True,
        "file_pii_array": [],
        "pii_array": [pii_entities, "Fictionalize", request_body],
        "is_api_key_encrypted": True,
        "file_name": ""
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
        "origin": "https://dev.zerotrusted.ai",
        "referer": "https://dev.zerotrusted.ai/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
    }
    try:
        async with httpx.AsyncClient(timeout=240, verify=False) as client:
            response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        return result.get("data", {})
    except httpx.TimeoutException:
        return None
    except Exception:
        return None
