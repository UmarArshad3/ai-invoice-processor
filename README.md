# AI Invoice Processing System

An AI-powered invoice processing application that extracts structured information from PDF invoices using Amazon Bedrock, validates the extracted data, detects potential duplicates, and stores invoice records in PostgreSQL for human review.

This project demonstrates practical AI integration, backend API development, database design, automated testing, containerization, and cloud-ready architecture.

## Features

- Upload PDF invoices through a FastAPI endpoint.
- Validate file type, content type, PDF signature, and file size.
- Extract text from PDF documents using `pypdf`.
- Use Amazon Bedrock with the Converse API to extract structured invoice data.
- Validate required fields, dates, currency, monetary values, and invoice totals.
- Detect potential duplicate invoices using invoice number and supplier name.
- Store invoice records and processing statuses in PostgreSQL.
- Support invoice listing and individual invoice retrieval.
- Support human approval and rejection workflows.
- Prevent duplicate invoices and invoices requiring correction from being approved.
- Manage database schema changes using Alembic migrations.
- Run automated tests with pytest.
- Build a Docker image for the FastAPI application.

## Architecture

**Technology stack**

| Component | Technology |
|---|---|
| Backend API | Python, FastAPI |
| AI extraction | Amazon Bedrock |
| AI SDK | Boto3 |
| PDF extraction | pypdf |
| Data validation | Python |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Database migrations | Alembic |
| Testing | pytest, HTTPX |
| Containerization | Docker, Docker Compose |
| Cloud infrastructure | AWS, Terraform (planned) |

## Processing workflow

1. A user uploads a PDF invoice.
2. The API validates the uploaded file.
3. Text is extracted from the PDF.
4. The extracted text is sent to Amazon Bedrock.
5. Bedrock returns structured invoice information in JSON format.
6. Python validates the extracted fields and checks the invoice total.
7. The system checks for a potential duplicate.
8. The invoice and its processing status are stored in PostgreSQL.
9. A human reviews the invoice and approves or rejects it.

**Important:** AI-extracted values are treated as untrusted input. Application-side validation checks the extracted information rather than relying on the model's calculations.

## Project structure

```text
ai-invoice-processor/
├── app/
│   ├── api/
│   │   └── invoices.py
│   ├── models/
│   │   └── invoice.py
│   ├── schemas/
│   │   └── invoice.py
│   ├── services/
│   │   ├── bedrock_service.py
│   │   ├── invoice_validator.py
│   │   └── pdf_extractor.py
│   ├── config.py
│   ├── database.py
│   └── main.py
├── migrations/
│   └── versions/
├── tests/
│   ├── test_api.py
│   └── test_invoice_validator.py
├── uploads/
├── .env.example
├── .gitignore
├── alembic.ini
├── compose.yaml
├── Dockerfile
└── requirements.txt
```

## Requirements

- Python 3.12 or later for local development
- Docker Desktop
- AWS account
- AWS CLI
- Amazon Bedrock model access and permission to invoke the configured model

## Local setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/ai-invoice-processor.git
cd ai-invoice-processor
```

Replace `YOUR_USERNAME` with the GitHub account that hosts the repository.

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create your local environment file:

```bash
cp .env.example .env
```

Configure the values in `.env`:

```env
DATABASE_URL=postgresql+psycopg://invoice_user:replace_me@localhost:5433/invoice_db
BEDROCK_MODEL_ID=your-bedrock-model-or-inference-profile-id
AWS_REGION=your-aws-region
```

Use the same PostgreSQL credentials configured in `compose.yaml`. Set the Bedrock model ID and AWS region to values available in your AWS account.

**Never commit `.env` or AWS credentials to Git.**

### 5. Configure AWS credentials

Configure your AWS CLI credentials using an appropriate IAM identity:

```bash
aws configure
```

Verify your AWS identity:

```bash
aws sts get-caller-identity
```

The IAM identity must have permission to invoke the configured Amazon Bedrock model or inference profile.

### 6. Start PostgreSQL

```bash
docker compose up -d db
```

Check the database container:

```bash
docker compose ps
```

### 7. Apply database migrations

```bash
alembic upgrade head
```

This creates the database schema using the project's migration history.

### 8. Start the API

```bash
uvicorn app.main:app --reload --port 8001
```

The API will be available at:

- Health check: http://127.0.0.1:8001/health
- Interactive API documentation: http://127.0.0.1:8001/docs

## API endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Check application health |
| POST | `/invoices/upload` | Upload and process a PDF invoice |
| GET | `/invoices/` | List stored invoices |
| GET | `/invoices/{invoice_id}` | Retrieve an invoice |
| POST | `/invoices/{invoice_id}/review` | Approve or reject an invoice |

The review endpoint accepts an action of `approve` or `reject`.

Invoices that need correction cannot be approved until the underlying issue is addressed. Potential duplicates are flagged for review.

## Running tests

Run the complete test suite:

```bash
pytest -q
```

The tests cover invoice validation and API behavior, including file validation, successful uploads, duplicate detection, retrieval, approval, and rejection.

The API tests use an isolated in-memory SQLite database and mocked external services, so they do not modify your local PostgreSQL invoice records or invoke Amazon Bedrock.

## Docker

Build the application image:

```bash
docker build -t ai-invoice-processor .
```

The Dockerfile packages the FastAPI application and its dependencies.

PostgreSQL is currently managed separately through Docker Compose. The application image has been built successfully; full application-container orchestration is a future enhancement.

## Database migrations

Create a new migration after changing database models:

```bash
alembic revision --autogenerate -m "describe your schema change"
```

Apply migrations:

```bash
alembic upgrade head
```

Check whether model changes require a migration:

```bash
alembic check
```

## Security and design considerations

- Environment variables are used for local configuration.
- AWS credentials are managed outside the source code.
- Uploaded PDFs are stored locally and excluded from Git.
- File uploads are restricted by type and size.
- Extracted values are validated in application code.
- Duplicate invoices are flagged for human review.
- Approval and rejection are explicit review actions.
- The system does not automatically make payments or perform financial transactions.

## Current limitations

- Text-based PDFs are supported; scanned PDFs require an OCR integration.
- PDF uploads are limited to 10 MB.
- PDF files are stored locally rather than in Amazon S3.
- Human review is required before an invoice is approved.
- Accounting platform integrations are not implemented.
- AWS deployment, Terraform infrastructure, CI/CD, and CloudWatch monitoring are planned enhancements.

## Future improvements

- OCR support for scanned invoices.
- Amazon S3 storage for uploaded documents.
- AWS deployment using Terraform.
- Docker Compose orchestration for the application and database.
- GitHub Actions continuous integration.
- CloudWatch logging and monitoring.
- Email-based invoice ingestion.
- Accounting integrations such as QuickBooks.
- Improved review workflows and audit history.

## Project status

The core invoice-processing workflow has been implemented and tested locally.

Completed:
- FastAPI application and invoice endpoints.
- Amazon Bedrock integration.
- PDF text extraction.
- Invoice validation and duplicate detection.
- PostgreSQL persistence.
- Human review workflow.
- Alembic database migrations.
- Automated test suite.
- Successful Docker image build.

Further cloud deployment and integration enhancements are planned.
