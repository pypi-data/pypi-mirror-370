import asyncio
import os
import threading
import traceback
from mitmproxy import http
from services.get_blocklist_service import get_blocked_hosts
from tools.shadow_ai_detector import is_shadow_ai_request
from tools.zt_log_forwarder import send_log_to_api
from tools.detect_pii import get_anonymized_prompt
import json

ZEROTRUSTED_API_TOKEN = "eyJhbGciOiJSUzI1NiIsImtpZCI6IkRGQkU0NEY1MzU3NDQ2RTBGNzVCRkNFM0U0MzQwOTBEIiwidHlwIjoiYXQrand0In0.eyJuYmYiOjE3NTQwMjkxMTIsImV4cCI6MTc1NDExNTUxMiwiaXNzIjoiaHR0cHM6Ly9kZXYtaWRlbnRpdHkuemVyb3RydXN0ZWQuYWkiLCJhdWQiOiJJZGVudGl0eSIsImNsaWVudF9pZCI6ImlkZW50aXR5LXNlcnZlci1kZW1vLXdlYiIsInN1YiI6IjQ1NTBhNTFlLWZhNmYtNGVjMi05MmYwLTViZmFlNTlhZjdmNCIsImF1dGhfdGltZSI6MTc1NDAyOTEwOSwiaWRwIjoibG9jYWwiLCJoYXNfcGFzc3dvcmQiOnRydWUsImVtYWlsIjoidGVzdDExMTExZGJAZ21haWwuY29tIiwicGxhbl9pZCI6IjYiLCJpc19hZG1pbiI6IkZhbHNlIiwic3RhdHVzIjoiMiIsImFjY291bnRfZGF0ZSI6IjIwMjUtMDQtMDVUMTA6NDA6MDlaIiwicm9sZV9pZCI6IjY3MDMyN2JlLWE1MGItNDg3NC05NTdjLTUxNDQzMDkzOGNhMSIsImlzX3BsYW5faW5oZXJpdGVkX2Zyb21fcGFyZW50IjpmYWxzZSwiaXNfV29ya3NwYWNlX293bmVyIjoiVHJ1ZSIsImNvbXBhbnlfbmFtZSI6Ilplcm90cnVzdGVkLkFJIiwid29ya3NwYWNlX2RvbWFpbiI6IndvcmtzcGFjZS56dGEtZ2F0ZXdheS5jb20iLCJyb2xlIjoiQ3VzdG9tZXJBZG1pbiIsImlzX3NpZ25fdXAiOmZhbHNlLCJqdGkiOiJDQkM5OTMwN0Y5NDlDMTI2OTE5QzVENUJBQjI2Njk4NSIsInNpZCI6IjBFMDhEOEVDOEU3NjcwMURDQkM3OTJGNUY3OTA2Q0E2IiwiaWF0IjoxNzU0MDI5MTEyLCJzY29wZSI6WyJvcGVuaWQiLCJwcm9maWxlIiwiY2xpZW50czp3cml0ZSIsIndlYmFwaTp3cml0ZSIsIndlYmFwaTpyZWFkIl0sImFtciI6WyJwd2QiXX0.Z2_kdF7JBEsdXZRIWNUbAMfhjj6-7FYWDSUporiperlrF6eYu50MCpgo4YEXqwaNGKWqmCd2nn1CdwMjy5ciF0000CH9tFT7WL6UweNy1MuPDyRMGkkSg6761GoB6wiunEADUg3eYFghIJpWoh8sutvpYqzVcJIbS1fnKXSMNmf8y5guvDPobBu_unmXF3FNu3xxIek_AFdfsJ5ryV4QbDTnErCmwsHoF8J762lGlqH91vu0J-bdLdhpI1F1Fs9qqbkNRM_dP1DtXqZAHQ5npTO7UJwUcMJo4od3p4ybh21ACtdezQyV3YIPIagO_hDG6xFLAWAbb8z2ZbUHhzpHMw"


# Fetch the API key from environment variable
api_key = os.getenv("ZT_PROXY_API_KEY")
if not api_key:
    raise ValueError("ZT_PROXY_API_KEY environment variable is not set.")

request_count = 0  # Global counter for successful requests

def run_async_in_thread(coro):
    def runner():
        asyncio.run(coro)
    threading.Thread(target=runner).start()


# Router config
ENABLE_ROUTER = True  # Set to False to disable router logic

ROUTES = {
    "/v2/pet": "https://petstore.swagger.io",
    "/orders": "https://orders.example.com",
    "/billing": "https://billing.example.com",
    "/ai": "https://ai.example.com"
}

class Interceptor:
    async def request(self, flow: http.HTTPFlow):
        global request_count

        host = flow.request.host
        path = flow.request.path
        url = flow.request.pretty_url
        method = flow.request.method
        headers = dict(flow.request.headers)
        body = flow.request.get_text()

        # --- Router logic ---
        if ENABLE_ROUTER:
            for route_path, backend in ROUTES.items():
                if path.startswith(route_path):
                    backend_host = backend.replace("https://", "").replace("http://", "")
                    flow.request.host = backend_host
                    flow.request.scheme = "https"
                    flow.request.port = 443
                    # Optionally update pretty_url if needed
                    flow.request.headers["Host"] = backend_host
                    # After routing, update local variables for logging
                    host = flow.request.host
                    url = flow.request.pretty_url
                    break

        # Try to parse the body to JSON if possible
        parsed_body = {}
        try:
            parsed_body = json.loads(body)
        except Exception:
            pass  # Body might not be JSON; that's okay

        # 🛑 Shadow AI Blocking
        if is_shadow_ai_request(host=host, path=path, headers=headers, body=body, parsed_body=parsed_body):
            print("🚫 Shadow AI request detected! Blocking...")

            log_lines = [
                "\n🔍 [REQUEST INTERCEPTED]",
                f"🌐 Host: {host}",
                f"📍 Path: {path}",
                f"🔗 Full URL: {url}",
                f"📬 Method: {method}",
                f"📄 Headers: {headers}",
                "-" * 80
            ]

            is_llm_call = any(k in parsed_body for k in ["model", "model_name", "llm", "used_input_tokens"])
            is_mcp_call = any(k in parsed_body for k in ["gateway_app_name", "customer_id", "tool", "mcp"])

            if is_llm_call:
                model_name = parsed_body.get("model") or parsed_body.get("model_name") or parsed_body.get("llm", "Unknown")
                log_lines.append("🤖 [LLM CALL DETECTED]")
                log_lines.append(f"📦 Model: {model_name}")
                log_lines.append(f"🌐 LLM Host: {host}")
            elif is_mcp_call:
                gateway_app = parsed_body.get("gateway_app_name", "Unknown")
                customer_id = parsed_body.get("customer_id", "Unknown")
                tool = parsed_body.get("tool", parsed_body.get("mcp", "Unknown"))
                log_lines.append("🛠️ [MCP CALL DETECTED]")
                log_lines.append(f"🏢 App: {gateway_app}")
                log_lines.append(f"🧾 Customer ID: {customer_id}")
                log_lines.append(f"🔧 Tool: {tool}")
            else:
                log_lines.append("❓ [Unknown Request Type]")

            log_lines.append("=" * 80)

            # 🔐 Check PII
            def is_encrypted(text):
                # Simple heuristic: if not decodable as utf-8 or contains lots of non-printable chars
                try:
                    text.encode('utf-8').decode('utf-8')
                except Exception:
                    return True
                # If >30% chars are non-printable, treat as encrypted
                non_printable = sum(1 for c in text if ord(c) < 32 or ord(c) > 126)
                if len(text) > 0 and non_printable / len(text) > 0.3:
                    return True
                return False

            pii_data = None
            compliance_data = None
            if body.strip() and not is_encrypted(body):
                try:
                    print("[DEBUG] Starting PII detection...")
                    print("body:", body)
                    loop = asyncio.get_event_loop()
                    from tools.compliance_report import get_compliance_report
                    pii_data = await get_anonymized_prompt(body, ZEROTRUSTED_API_TOKEN)
                    print(f"[DEBUG] PII Detection Result: {pii_data}")
                    # Fix: Use attributes for Pydantic response object
                    if pii_data and getattr(pii_data, "success", False) and getattr(pii_data, "data", None):
                        pii_entities = getattr(pii_data.data, "pii_entities", [])
                        anonymized_prompt = getattr(pii_data.data, "anonymized_prompt", "")
                        log_lines.append("🛡️ [PII DETECTED]")
                        log_lines.append(f"🔎 PII Entities: {json.dumps(pii_entities, indent=2)}")
                        log_lines.append(f"📝 Anonymized Prompt: {anonymized_prompt}")
                        print("[DEBUG] Starting compliance report API call...")
                        try:
                            compliance_data = await get_compliance_report(
                                pii_entities, body, ZEROTRUSTED_API_TOKEN
                            )
                            print(f"[DEBUG] Compliance Data Result: {compliance_data}")
                            log_lines.append(f"📋 Compliance Data: {json.dumps(compliance_data, indent=2)}")
                        except Exception as e:
                            print(f"[DEBUG] Compliance report API error: {str(e)}")
                            log_lines.append(f"⚠️ [COMPLIANCE REPORT ERROR] {str(e)}")
                    else:
                        log_lines.append(f"⚠️ [PII DETECTION ERROR] {getattr(pii_data, 'error_message', 'Unknown error')}")
                        pii_entities = []
                        anonymized_prompt = ""
                except Exception as e:
                    print(f"[DEBUG] PII detection error: {str(e)}")
                    log_lines.append(f"⚠️ [PII DETECTION ERROR] {str(e)}")
                    pii_entities = []
                    anonymized_prompt = ""
            elif body.strip():
                log_lines.append("🔒 [Body appears encrypted, skipping PII detection]")
                pii_entities = []
                anonymized_prompt = ""

            # Save logs to file
            with open("intercepted_requests.log", "a", encoding="utf-8") as log_file:
                log_file.write("\n".join(log_lines) + "\n")

            # Send to external logging API
            try:
                print("[DEBUG] Preparing to send log to API...")
                compliance_payload = None
                if compliance_data:
                    compliance_payload = {
                        "compliance_violation": compliance_data.get("compliance_violation"),
                        "compliance_violation_fixed_by": compliance_data.get("compliance_violation_fixed_by"),
                        "compliance_violation_fixed_percentage": compliance_data.get("compliance_violation_fixed_percentage"),
                        "compliance_report": compliance_data.get("compliance_report", []),
                    }
                print("[DEBUG] compliance payload assigned")
                if host.lower() not in ["dev-gliner.zerotrusted.ai", "dev-history.zerotrusted.ai", "dev-agents.zerotrusted.ai"]:
                    print("[DEBUG] Awaiting send_log_to_api...")
                    result = await send_log_to_api(
                        api_key=api_key,
                        host=host,
                        path=path,
                        url=url,
                        method=method,
                        headers=headers,
                        body=body,
                        pii_entities=pii_entities,
                        anonymized_prompt=anonymized_prompt,
                        compliance_report=compliance_payload
                    )
                    print(f"[DEBUG] send_log_to_api result: {result}")
            except Exception as e:
                print(f"[DEBUG] API SEND ERROR: {str(e)}")
                print(f"[DEBUG] traceback: {traceback.format_exc()}")

            # Block response
            flow.response = http.Response.make(
                403,
                "🚫 Request Blocked by ZeroTrusted.ai: Shadow AI usage is not allowed.",
                {"Content-Type": "text/plain"}
            )
            return
        
        # ✅ Not blocked → minimal log
        request_count += 1
        log_line = f"✅ Request #{request_count} - Host: {host}, path: {path}"
        print(log_line)

        with open("intercepted_requests.log", "a", encoding="utf-8") as log_file:
            log_file.write(log_line + "\n")



addons = [
    Interceptor()
]
