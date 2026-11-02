from sqlalchemy import Column, Integer, String, Date, DateTime, Numeric, ForeignKey
from sqlalchemy.sql import func

from app.database import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    duplicate_of_invoice_id = Column(
    Integer,
    ForeignKey("invoices.id"),
    nullable=True
)
    invoice_number = Column(String(100), nullable=True, index=True)
    supplier_name = Column(String(255), nullable=True)

    invoice_date = Column(Date, nullable=True)
    due_date = Column(Date, nullable=True)

    subtotal = Column(Numeric(12, 2), nullable=True)
    tax_amount = Column(Numeric(12, 2), nullable=True)
    total_amount = Column(Numeric(12, 2), nullable=True)

    currency = Column(String(3), nullable=True)

    status = Column(
        String(30),
        nullable=False,
        default="pending_review"
    )

    source_filename = Column(String(255), nullable=False)

    uploaded_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
