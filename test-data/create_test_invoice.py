from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

file_path = "test-data/DOCKER-E2E-001.pdf"

pdf = canvas.Canvas(file_path, pagesize=letter)

pdf.setTitle("Test Invoice DOCKER-E2E-001")

pdf.setFont("Helvetica-Bold", 18)
pdf.drawString(72, 740, "TEST INVOICE")

pdf.setFont("Helvetica", 11)
lines = [
    "Invoice Number: DOCKER-E2E-001",
    "Supplier: Docker Test Solutions Ltd",
    "Invoice Date: 2026-11-02",
    "Due Date: 2026-12-02",
    "",
    "Subtotal: 1000.00 USD",
    "Tax: 180.00 USD",
    "Total: 1180.00 USD",
]

y = 700
for line in lines:
    pdf.drawString(72, y, line)
    y -= 25

pdf.save()

print(f"Test invoice created: {file_path}")
