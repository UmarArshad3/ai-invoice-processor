# AI Invoice Processing System

An AI-powered invoice processing application that extracts structured information from PDF invoices using Amazon Bedrock, validates the extracted data, detects potential duplicates, and stores invoice records in PostgreSQL for human review.

This project demonstrates practical AI integration, backend API development, database design, automated testing, containerization, and cloud-ready architecture.

## Screenshots

![AI Invoice Processor architecture diagram](docs/screenshots/ai-invoice-processor-architecture.png)

### API documentation
![API documentation](docs/screenshots/api-documentation.png)

### Invoice list
![Invoice list](docs/screenshots/invoice-list.png)

### Invoice details
![Invoice list with details](docs/screenshots/invoice-list-details.png)

### Duplicate detection
![Duplicate detection](docs/screenshots/duplicate-detection.png)

### Human review workflow
![Human review workflow](docs/screenshots/human-review-workflow.png)

### CI pipeline passing
![GitHub Actions passing](docs/screenshots/github-actions-passing.png)

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
| Cloud infrastructure | AWS, Terraform (configuration validated locally) |

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

## Continuous Integration (GitHub Actions)

GitHub Actions automatically runs the project's CI pipeline on every push and pull request targeting the `main` branch.

### Automated checks

The pipeline includes two jobs:

**Python Tests**
- Sets up Python 3.12.
- Installs project dependencies.
- Runs the automated test suite using `pytest -v`.
- Uses an isolated SQLite database and placeholder Bedrock configuration, so CI does not require AWS credentials or invoke Amazon Bedrock.

**Terraform Validation**
- Sets up Terraform 1.16.4.
- Checks Terraform formatting using `terraform fmt -check -recursive`.
- Initializes Terraform using the committed provider lock file.
- Validates the Terraform configuration using `terraform validate`.

The pipeline validates infrastructure configuration only. It does not run `terraform plan` or `terraform apply`, provision AWS resources, or incur AWS infrastructure deployment costs.

Both jobs must pass for the CI workflow to complete successfully.

## Docker Compose

The application and PostgreSQL database can run together using Docker Compose.

### Services

| Service | Description | Host port |
|---|---|---|
| `web` | FastAPI application | 8001 |
| `db` | PostgreSQL database | 5433 |

The application connects to PostgreSQL through the internal Docker Compose hostname `db` on port `5432`.

### Configure environment variables

Create `.env` from the example:

```bash
cp .env.example .env
```

Configure your Amazon Bedrock model ID, AWS region, and database settings as required.

Make sure AWS credentials are available to the container through your configured AWS credentials directory or environment.

### Start the services

```bash
docker compose up -d --build
```

Check service status:

```bash
docker compose ps
```

View application logs:

```bash
docker compose logs -f web
```

### Verify the application

Health endpoint:

```bash
curl http://localhost:8001/health
```

Interactive API documentation:

http://localhost:8001/docs

### Database migrations

Check the current migration:

```bash
docker compose exec web alembic current
```

Apply pending migrations:

```bash
docker compose exec web alembic upgrade head
```

Check model and database schema consistency:

```bash
docker compose exec web alembic check
```

### Stop the services

```bash
docker compose down
```

The PostgreSQL data is stored in a named Docker volume and is preserved when the services are stopped. Avoid `docker compose down -v` unless you intentionally want to delete that volume.
### End-to-End Verification

The Dockerized application was tested successfully through the complete invoice processing workflow.

**Test environment:**
- FastAPI application running in Docker.
- PostgreSQL 17 running in Docker.
- Amazon Bedrock accessed from inside the application container.
- A generated PDF invoice with a unique invoice number.

**Verified workflow:**
1. Uploaded a PDF invoice through the FastAPI endpoint.
2. Extracted invoice text from the PDF.
3. Processed invoice data using Amazon Bedrock.
4. Validated the extracted fields and invoice totals.
5. Checked for duplicate invoices.
6. Stored the invoice in PostgreSQL.
7. Retrieved the saved invoice through the API.
8. Approved the invoice through the human review endpoint.
9. Verified that the approved status persisted in PostgreSQL.

**Test result:** Successful. The test invoice was processed, validated, stored, retrieved, and approved.

The local test PDF is excluded from Git. Its generator script is included in `test-data/create_test_invoice.py` so the test document can be reproduced.
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
- Terraform infrastructure configuration is implemented and validated locally, but AWS resources have not been deployed.
- CI/CD and CloudWatch monitoring are planned enhancements.

## Future improvements

- OCR support for scanned invoices.
- Amazon S3 storage for uploaded documents.
- AWS deployment using Terraform when the budget permits.
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

- Terraform infrastructure configuration, formatting, and validation.

Further cloud deployment and integration enhancements are planned.
