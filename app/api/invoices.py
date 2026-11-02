from datetime import date
from decimal import Decimal
from pathlib import Path
from uuid import uuid4


from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from sqlalchemy import func
from sqlalchemy.orm import Session
from pypdf.errors import PdfReadError

from app.database import get_db
from app.models.invoice import Invoice
from app.services.pdf_extractor import extract_pdf_text
from app.services.bedrock_service import extract_invoice_data
from app.services.invoice_validator import validate_invoice_data
router = APIRouter(prefix="/invoices", tags=["Invoices"])

PROJECT_ROOT = Path(__file__).resolve().parents[2]
UPLOAD_DIR = PROJECT_ROOT / "uploads"

MAX_FILE_SIZE = 10 * 1024 * 1024



@router.post("/upload")
async def upload_invoice(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # 1. Validate the uploaded file
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are accepted."
        )

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Invalid content type. Please upload a PDF."
        )

    file_content = await file.read(MAX_FILE_SIZE + 1)

    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File exceeds the 10 MB upload limit."
        )

    if not file_content.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a valid PDF."
        )

    # 2. Extract text from the PDF
    try:
        extracted_text = extract_pdf_text(file_content)
    except (PdfReadError, ValueError):
        raise HTTPException(
            status_code=400,
            detail="Unable to read this PDF. It may be damaged or encrypted."
        )

    if not extracted_text.strip():
        raise HTTPException(
            status_code=422,
            detail="No extractable text found. Scanned PDFs require OCR."
        )

    # 3. Extract invoice fields using Amazon Bedrock
    try:
        invoice_data = extract_invoice_data(extracted_text)

        if not isinstance(invoice_data, dict):
            raise ValueError("Bedrock returned an invalid data structure.")

    except (RuntimeError, ValueError) as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Invoice AI extraction failed: {exc}"
        )

    # 4. Validate extracted fields
    validation = validate_invoice_data(invoice_data)

    # 5. Check for duplicate invoice
    duplicate_invoice = None
    duplicate_of_invoice_id = None

    invoice_number = invoice_data.get("invoice_number")
    supplier_name = invoice_data.get("supplier_name")

    if (
        isinstance(invoice_number, str)
        and invoice_number.strip()
        and isinstance(supplier_name, str)
        and supplier_name.strip()
    ):
        duplicate_invoice = (
            db.query(Invoice)
            .filter(
                func.lower(func.trim(Invoice.invoice_number))
                == invoice_number.strip().lower(),
                func.lower(func.trim(Invoice.supplier_name))
                == supplier_name.strip().lower()
            )
            .order_by(Invoice.id.asc())
            .first()
        )

    if duplicate_invoice:
        duplicate_of_invoice_id = duplicate_invoice.id
        status = "needs_review"
    else:
        status = (
            "pending_review"
            if validation["valid"]
            else "needs_review"
        )

    # 6. Convert extracted values
    try:
        invoice_date = (
            date.fromisoformat(invoice_data["invoice_date"])
            if invoice_data.get("invoice_date")
            else None
        )

        due_date = (
            date.fromisoformat(invoice_data["due_date"])
            if invoice_data.get("due_date")
            else None
        )

        def to_decimal(value):
            return Decimal(str(value)) if value is not None else None

        invoice = Invoice(
            invoice_number=invoice_number,
            duplicate_of_invoice_id=duplicate_of_invoice_id,
            supplier_name=supplier_name,
            invoice_date=invoice_date,
            due_date=due_date,
            subtotal=to_decimal(invoice_data.get("subtotal")),
            tax_amount=to_decimal(invoice_data.get("tax_amount")),
            total_amount=to_decimal(invoice_data.get("total_amount")),
            currency=invoice_data.get("currency"),
            status=status,
            source_filename=file.filename
        )

    except (ValueError, TypeError, ArithmeticError) as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Unable to prepare extracted invoice data: {exc}"
        )

    # 7. Save the PDF and database record
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    saved_filename = f"{uuid4().hex}.pdf"
    saved_path = UPLOAD_DIR / saved_filename

    saved_path.write_bytes(file_content)

    try:
        db.add(invoice)
        db.commit()
        db.refresh(invoice)

    except Exception:
        db.rollback()
        saved_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=500,
            detail="Unable to save invoice to the database."
        )

    # 8. Return processing result
    return {
        "message": "Invoice processed successfully.",
        "invoice_id": invoice.id,
        "saved_filename": saved_filename,
        "status": invoice.status,
        "duplicate": duplicate_invoice is not None,
        "duplicate_of_invoice_id": invoice.duplicate_of_invoice_id,
        "validation": validation,
        "invoice": {
            "invoice_number": invoice.invoice_number,
            "supplier_name": invoice.supplier_name,
            "invoice_date": (
                invoice.invoice_date.isoformat()
                if invoice.invoice_date else None
            ),
            "due_date": (
                invoice.due_date.isoformat()
                if invoice.due_date else None
            ),
            "subtotal": (
                str(invoice.subtotal)
                if invoice.subtotal is not None else None
            ),
            "tax_amount": (
                str(invoice.tax_amount)
                if invoice.tax_amount is not None else None
            ),
            "total_amount": (
                str(invoice.total_amount)
                if invoice.total_amount is not None else None
            ),
            "currency": invoice.currency
        }
    }


from pydantic import BaseModel
from typing import Literal


class ReviewRequest(BaseModel):
    action: Literal["approve", "reject"]


def invoice_to_dict(invoice: Invoice):
    return {
        "id": invoice.id,
        "invoice_number": invoice.invoice_number,
        "supplier_name": invoice.supplier_name,
        "invoice_date": (
            invoice.invoice_date.isoformat()
            if invoice.invoice_date else None
        ),
        "due_date": (
            invoice.due_date.isoformat()
            if invoice.due_date else None
        ),
        "subtotal": (
            str(invoice.subtotal)
            if invoice.subtotal is not None else None
        ),
        "tax_amount": (
            str(invoice.tax_amount)
            if invoice.tax_amount is not None else None
        ),
        "total_amount": (
            str(invoice.total_amount)
            if invoice.total_amount is not None else None
        ),
        "currency": invoice.currency,
        "status": invoice.status,
        "duplicate_of_invoice_id": invoice.duplicate_of_invoice_id,
        "source_filename": invoice.source_filename,
        "uploaded_at": (
            invoice.uploaded_at.isoformat()
            if invoice.uploaded_at else None
        )
    }


@router.get("/")
def list_invoices(db: Session = Depends(get_db)):
    invoices = (
        db.query(Invoice)
        .order_by(Invoice.id.desc())
        .all()
    )

    return {
        "count": len(invoices),
        "invoices": [invoice_to_dict(invoice) for invoice in invoices]
    }


@router.get("/{invoice_id}")
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db)
):
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id
    ).first()

    if invoice is None:
        raise HTTPException(
            status_code=404,
            detail="Invoice not found."
        )

    return invoice_to_dict(invoice)


@router.post("/{invoice_id}/review")
def review_invoice(
    invoice_id: int,
    review: ReviewRequest,
    db: Session = Depends(get_db)
):
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id
    ).first()

    if invoice is None:
        raise HTTPException(
            status_code=404,
            detail="Invoice not found."
        )

    if invoice.status not in ["pending_review", "needs_review"]:
        raise HTTPException(
            status_code=409,
            detail="This invoice has already been reviewed."
        )

    if review.action == "approve":
        if invoice.status == "needs_review":
            raise HTTPException(
                status_code=409,
                detail="This invoice needs correction before approval."
            )

        invoice.status = "approved"

    elif review.action == "reject":
        invoice.status = "rejected"

    db.commit()
    db.refresh(invoice)

    return {
        "message": (
            "Invoice approved successfully."
            if review.action == "approve"
            else "Invoice rejected successfully."
        ),
        "invoice": invoice_to_dict(invoice)
    }

