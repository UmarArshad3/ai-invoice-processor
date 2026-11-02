
from app.services.invoice_validator import validate_invoice_data


def valid_invoice():
    return {
        "invoice_number": "INV-1001",
        "supplier_name": "Example Technology Ltd",
        "invoice_date": "2026-10-15",
        "due_date": "2026-11-15",
        "subtotal": 1000.00,
        "tax_amount": 180.00,
        "total_amount": 1180.00,
        "currency": "USD"
    }


def test_valid_invoice():
    result = validate_invoice_data(valid_invoice())

    assert result["valid"] is True
    assert result["errors"] == []


def test_missing_invoice_number():
    data = valid_invoice()
    data["invoice_number"] = None

    result = validate_invoice_data(data)

    assert result["valid"] is False
    assert any(
        "invoice_number" in error
        for error in result["errors"]
    )


def test_missing_supplier_name():
    data = valid_invoice()
    data["supplier_name"] = ""

    result = validate_invoice_data(data)

    assert result["valid"] is False
    assert any(
        "supplier_name" in error
        for error in result["errors"]
    )


def test_incorrect_invoice_total():
    data = valid_invoice()
    data["total_amount"] = 1250.00

    result = validate_invoice_data(data)

    assert result["valid"] is False
    assert any(
        "total does not match" in error
        for error in result["errors"]
    )


def test_invalid_invoice_date():
    data = valid_invoice()
    data["invoice_date"] = "15-10-2026"

    result = validate_invoice_data(data)

    assert result["valid"] is False
    assert any(
        "invoice_date" in error
        for error in result["errors"]
    )


def test_negative_invoice_amount():
    data = valid_invoice()
    data["subtotal"] = -100.00

    result = validate_invoice_data(data)

    assert result["valid"] is False


def test_invalid_currency():
    data = valid_invoice()
    data["currency"] = "US"

    result = validate_invoice_data(data)

    assert result["valid"] is False
    assert any(
        "Currency" in error
        for error in result["errors"]
    )

