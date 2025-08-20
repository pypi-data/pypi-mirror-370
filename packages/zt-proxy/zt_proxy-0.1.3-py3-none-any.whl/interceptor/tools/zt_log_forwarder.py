import os
import httpx
import traceback
import json
from services.get_blocklist_service import get_blocked_hosts

API_ENDPOINT = "https://dev-history.zerotrusted.ai/api/llm/logs/create"

async def send_log_to_api(api_key, host, path, url, method, headers, body, pii_entities, anonymized_prompt, compliance_report):
    try:
        payload = {
            "host": host,
            "path": path,
            "url": url,
            "method": method,
            "headers": headers or {},
            "piiDetected": pii_entities or [],
            "anonymizedRequest": anonymized_prompt or {},
            "type": "Proxy",
            "extra": {
                "complianceReport": compliance_report or {},
                "originalRequest": body or {}
            }
        }

        # Add custom token header
        request_headers = {
            "X-Custom-Token": api_key,
            "Content-Type": "application/json"
        }

        print("Sending to:", API_ENDPOINT)
        print("Payload:", json.dumps(payload, indent=2))

        async with httpx.AsyncClient(verify=False, timeout=10) as client:
            response = await client.post(API_ENDPOINT, json=payload, headers=request_headers)

        print("✅ Response Status:", response.status_code)
        print("✅ Response Body:", response.text)

        return response.status_code, response.text

    except httpx.RequestError as req_err:
        print("🚨 HTTPX Request failed:", str(req_err))
        traceback.print_exc()
        return None, str(req_err)

    except Exception as e:
        print("🚨 Unexpected error:", str(e))
        traceback.print_exc()
        return None, str(e)
