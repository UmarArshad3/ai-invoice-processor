
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models.invoice import Invoice
import app.api.invoices as invoice_api


# Create an isolated in-memory SQLite database for tests.
TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


@pytest.fixture
def client(tmp_path, monkeypatch):
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    # Prevent tests from writing into the real uploads directory.
    monkeypatch.setattr(invoice_api, "UPLOAD_DIR", tmp_path)

    # Mock PDF extraction and Bedrock.
    monkeypatch.setattr(
        invoice_api,
        "extract_pdf_text",
        lambda content: "Sample invoice text"
    )

    monkeypatch.setattr(
        invoice_api,
        "extract_invoice_data",
        lambda text: {
            "invoice_number": "TEST-1001",
            "supplier_name": "Test Supplier Ltd",
            "invoice_date": "2026-10-15",
            "due_date": "2026-11-15",
            "subtotal": 1000.00,
            "tax_amount": 180.00,
            "total_amount": 1180.00,
            "currency": "USD"
        }
    )

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def upload_test_invoice(client):
    return client.post(
        "/invoices/upload",
        files={
            "file": (
                "test-invoice.pdf",
                b"%PDF-1.4\nTest PDF content",
                "application/pdf"
            )
        }
    )


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_reject_non_pdf_upload(client):
    response = client.post(
        "/invoices/upload",
        files={
            "file": (
                "invoice.txt",
                b"Not a PDF",
                "text/plain"
            )
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Only PDF files are accepted."


def test_successful_invoice_upload(client):
    response = upload_test_invoice(client)

    assert response.status_code == 200

    data = response.json()

    assert data["invoice_id"] == 1
    assert data["status"] == "pending_review"
    assert data["duplicate"] is False
    assert data["invoice"]["invoice_number"] == "TEST-1001"


def test_duplicate_invoice_detection(client):
    first_response = upload_test_invoice(client)
    second_response = upload_test_invoice(client)

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    first = first_response.json()
    second = second_response.json()

    assert second["duplicate"] is True
    assert second["duplicate_of_invoice_id"] == first["invoice_id"]
    assert second["status"] == "needs_review"


def test_invoice_retrieval(client):
    upload_response = upload_test_invoice(client)
    invoice_id = upload_response.json()["invoice_id"]

    response = client.get(f"/invoices/{invoice_id}")

    assert response.status_code == 200
    assert response.json()["id"] == invoice_id


def test_invoice_approval(client):
    upload_response = upload_test_invoice(client)
    invoice_id = upload_response.json()["invoice_id"]

    response = client.post(
        f"/invoices/{invoice_id}/review",
        json={"action": "approve"}
    )

    assert response.status_code == 200
    assert response.json()["invoice"]["status"] == "approved"


def test_duplicate_invoice_cannot_be_approved(client):
    upload_test_invoice(client)
    duplicate_response = upload_test_invoice(client)

    duplicate_id = duplicate_response.json()["invoice_id"]

    response = client.post(
        f"/invoices/{duplicate_id}/review",
        json={"action": "approve"}
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "This invoice needs correction before approval."
    )


def test_invoice_rejection(client):
    upload_response = upload_test_invoice(client)
    invoice_id = upload_response.json()["invoice_id"]

    response = client.post(
        f"/invoices/{invoice_id}/review",
        json={"action": "reject"}
    )

    assert response.status_code == 200
    assert response.json()["invoice"]["status"] == "rejected"

