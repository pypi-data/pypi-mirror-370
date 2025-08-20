from pii_detection.schema.detect_anonymize_pii import AnonymizePromptRequest, AnonymizePromptResponse, AnonymizedPromptResponse
from pii_detection.services.detect_anonymize_pii_service import get_anonymize_prompt_gliner
import logging

logger = logging.getLogger(__name__)

async def get_anonymized_prompt(
    prompt: str,
    pii_entities: str = "email, email address, gmail, person, organization, phone number, address, passport number, credit card number, social security number, health insurance id number, itin, date time, us passport_number, date, time, crypto currency number, url, date of birth, mobile phone number, bank account number, medication, cpf, driver's license number, tax identification number, medical condition, identity card number, national id number, ip address, iban, credit card expiration date, username, health insurance number, registration number, student id number, insurance number, flight number, landline phone number, blood type, cvv, reservation number, digital signature, social media handle, license plate number, cnpj, postal code, serial number, vehicle registration number, credit card brand, fax number, visa number, insurance company, identity document number, transaction number, national health insurance number, cvc, birth certificate number, train ticket number, passport expiration date, social_security_number, medical license",
    anonymize_keywords: str = "",
    do_not_anonymize_keywords: str = "",
    keyword_safeguard: str = "test, deteyryrysad asd",
    uploaded_file: str = "",
) -> AnonymizePromptResponse:
    try:
        logger.info(
            f"Received get anonymize prompt api request with prompt and pii entities: "
        )

        # Validate request data
        form_data = AnonymizePromptRequest(
            pii_entities=pii_entities,
            prompt=prompt,
            anonymize_keywords=anonymize_keywords,
            deanonymize_keywords=do_not_anonymize_keywords,
            keyword_safeguard=keyword_safeguard,
            uploaded_file=uploaded_file,
        )

        response = await get_anonymize_prompt_gliner(form_data)

        return AnonymizePromptResponse(success=True, data=response)

    except Exception as e:
        logger.error(f"Error occurred during get anonymized prompt api processing: {e}")
        return AnonymizePromptResponse(
            success=False, data=AnonymizedPromptResponse(), error_message=str(e)
        )