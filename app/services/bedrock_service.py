import json

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.config import settings


bedrock = boto3.client(
    service_name="bedrock-runtime",
    region_name=settings.aws_region
)


def extract_invoice_data(invoice_text: str) -> dict:
    """
    Send extracted invoice text to Amazon Bedrock
    and return the model's structured JSON response.
    """

    prompt = f"""
You are an invoice data extraction assistant.

Extract the following fields from the invoice text:
- invoice_number
- supplier_name
- invoice_date
- due_date
- subtotal
- tax_amount
- total_amount
- currency

Rules:
1. Return only valid JSON. Do not include Markdown or explanations.
2. Use null when a field is missing or unclear.
3. Dates must use YYYY-MM-DD format.
4. Monetary amounts must be numbers, not strings.
5. Do not calculate or guess missing values.
6. Extract only information supported by the invoice text.

Use exactly this JSON structure:
{{
    "invoice_number": null,
    "supplier_name": null,
    "invoice_date": null,
    "due_date": null,
    "subtotal": null,
    "tax_amount": null,
    "total_amount": null,
    "currency": null
}}

Invoice text:
{invoice_text}
"""

    try:
        response = bedrock.converse(
            modelId=settings.bedrock_model_id,
            messages=[
                {
                    "role": "user",
                    "content": [{"text": prompt}]
                }
            ],
            inferenceConfig={
                "maxTokens": 1000,
                "temperature": 0
            }
        )

        response_text = response["output"]["message"]["content"][0]["text"]
        return json.loads(response_text)

    except json.JSONDecodeError as exc:
        raise ValueError(
            "Bedrock returned a response that was not valid JSON."
        ) from exc

    except (ClientError, BotoCoreError) as exc:
        raise RuntimeError(
            f"Amazon Bedrock request failed: {exc}"
        ) from exc
