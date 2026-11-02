from datetime import date
from decimal import Decimal, InvalidOperation


def validate_invoice_data(data: dict) -> dict:
    errors = []

    # Check required text fields
    required_fields = [
        "invoice_number",
        "supplier_name",
    ]

    for field in required_fields:
        value = data.get(field)

        if not isinstance(value, str) or not value.strip():
            errors.append(f"{field} is missing or invalid.")

    # Validate dates
    date_fields = ["invoice_date", "due_date"]

    for field in date_fields:
        value = data.get(field)

        if value is not None:
            try:
                date.fromisoformat(value)
            except (ValueError, TypeError):
                errors.append(f"{field} must use YYYY-MM-DD format.")

    # Validate monetary values
    amount_fields = ["subtotal", "tax_amount", "total_amount"]
    amounts = {}

    for field in amount_fields:
        value = data.get(field)

        if value is None:
            continue

        try:
            amount = Decimal(str(value))

            if not amount.is_finite() or amount < 0:
                raise InvalidOperation

            amounts[field] = amount

        except (InvalidOperation, ValueError, TypeError):
            errors.append(f"{field} must be a valid non-negative number.")

    # Check that subtotal + tax equals total
    if all(field in amounts for field in amount_fields):
        expected_total = amounts["subtotal"] + amounts["tax_amount"]
        actual_total = amounts["total_amount"]

        if expected_total != actual_total:
            errors.append(
                "Invoice total does not match subtotal plus tax."
            )

    # Validate currency
    currency = data.get("currency")

    if currency is not None:
        if (
            not isinstance(currency, str)
            or len(currency) != 3
            or not currency.isalpha()
        ):
            errors.append("Currency must be a three-letter code.")

    return {
        "valid": len(errors) == 0,
        "errors": errors
    }
