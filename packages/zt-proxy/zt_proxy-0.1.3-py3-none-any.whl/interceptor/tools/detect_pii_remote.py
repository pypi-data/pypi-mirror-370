
import httpx

async def get_anonymized_prompt(prompt: str, token: str) -> dict:
    """
    Sends a prompt to the ZeroTrusted API and returns the anonymized response details.
    Args:
        prompt (str): The user input prompt containing potential PII.
        token (str): The bearer token for authorization.
    Returns:
        dict: A dictionary containing relevant anonymization data.
    """
    url = "https://dev-gliner.zerotrusted.ai/get-anonymized-prompts-with-models"

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9,hi;q=0.8",
        "authorization": f"Bearer {token}",
        "origin": "https://dev.zerotrusted.ai",
        "priority": "u=1, i",
        "referer": "https://dev.zerotrusted.ai/",
        "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    }

    print(f"[DEBUG] sending pii detection message for body: {prompt}")

    # httpx requires files as a dict of (name, (filename, content, content_type))
    files = {
        "pii_entities": (None, "email, email address, gmail, person, organization, phone number, address, passport number, credit card number, social security number, health insurance id number, itin, date time, us passport_number, date, time, crypto currency number, url, date of birth, mobile phone number, bank account number, medication, cpf, driver's license number, tax identification number, medical condition, identity card number, national id number, ip address, iban, credit card expiration date, username, health insurance number, registration number, student id number, insurance number, flight number, landline phone number, blood type, cvv, reservation number, digital signature, social media handle, license plate number, cnpj, postal code, serial number, vehicle registration number, credit card brand, fax number, visa number, insurance company, identity document number, transaction number, national health insurance number, cvc, birth certificate number, train ticket number, passport expiration date, social_security_number, medical license"),
        "prompt": (None, prompt),
        "anonymize_keywords": (None, ""),
        "keyword_safeguard": (None, "test, deteyryrysad asd"),
        "uploaded_file": (None, ""),
        "do_not_anonymize_keywords": (None, "")
    }

    try:
        async with httpx.AsyncClient(timeout=240, verify=False) as client:
            response = await client.post(url, headers=headers, files=files)
        response.raise_for_status()
        result = response.json()
        return {
            "success": result.get("success"),
            "anonymized_prompt": result["data"].get("anonymized_prompt"),
            "highlighted_original_prompt": result["data"].get("highlighted_original_prompt"),
            "highlighted_anonymized_prompt": result["data"].get("highlighted_anonymized_prompt"),
            "pii_list": result["data"].get("pii_list"),
            "pii_entities": result["data"].get("pii_entities"),
            "errors": result.get("error_message"),
        }
    except httpx.TimeoutException:
        return None
    except Exception:
        return None
