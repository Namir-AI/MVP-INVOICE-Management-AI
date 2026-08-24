# AI Invoice & Expense Agent — MVP

A fast portfolio prototype for construction-project invoice and expense management.

## Demo workflow

**Invoice PDF/image → field extraction → expense classification → project assignment → clarification/manual review → SQLite → reports/P&L**

## Features

- PDF upload and embedded-text extraction with PyMuPDF
- Optional local OCR path for images/scans via Tesseract
- Structured fields: supplier, invoice number/date, subtotal, VAT/tax, total, currency, description
- Basic arithmetic validation
- Rule-based expense categorization for a zero-key demo
- Construction-project matching with confidence and clarification when ambiguous
- SQLite persistence
- Manual invoice review/editing
- Project expense and P&L reports
- Controlled natural-language reporting examples

## Architecture

```text
PDF / Image
    ↓
Text Extraction / OCR
    ↓
Structured Invoice Parser
    ↓
Validation + Classification
    ↓
Project Match + Confidence
   ↙                 ↘
Clear               Uncertain
  ↓                    ↓
Save              Ask / Select
   \                  /
      SQLite Database
        ↙       ↘
     Review    Reports / P&L / Ask
```

## Why the MVP uses local rules

The public demo intentionally works without API credentials. The extraction and classification layer is designed to be replaceable in production by an LLM and invoice-aware document service such as Google Document AI, Azure Document Intelligence, or AWS Textract.

## Run

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python generate_sample_invoices.py
streamlit run app.py
```

For scanned images, install Tesseract locally or use a cloud document-processing provider in a production implementation.

## Suggested demo

1. Start the app.
2. Upload `sample_invoices/alpha_materials.pdf`.
3. Review extracted fields, category and Project Alpha assignment.
4. Save the invoice.
5. Upload `sample_invoices/ambiguous_transport.pdf`.
6. Show that the system requests project clarification instead of silently guessing.
7. Select a project and save.
8. Open **Invoices** to review or edit records.
9. Open **Reports** to show expenses, VAT and project P&L.
10. Open **Ask** and try:
   - `Show expenses for Project Alpha`
   - `Give me P&L for Project Beta`

## Sample data

All projects, suppliers and invoices are fictional and generated only for demonstration.

Seed projects:

- Project Alpha — Residential tower, Riverside site
- Project Beta — Commercial fit-out, Central district
- Project Gamma — Warehouse and logistics hub, North zone
- Project Delta — Road and drainage package, East zone

## Technology stack

- Python
- Streamlit
- SQLite
- PyMuPDF
- Pandas
- Pillow / optional Tesseract OCR

## MVP limitations

This is a portfolio prototype, not an accounting system. OCR accuracy, authentication, audit controls, production security, multi-company tenancy, and financial/accounting integrations are intentionally outside MVP scope.

## Production roadmap

- LLM structured extraction/classification
- Invoice-aware OCR/document processing
- PostgreSQL / Supabase
- WhatsApp Business API
- n8n orchestration
- Authentication and roles
- Approval workflow and audit trail
- Duplicate-invoice detection
- Purchase-order matching
- Accounting-system integrations
- Scheduled project and VAT reports

## Security

No credentials are hard-coded. Environment files, local databases and local secrets are excluded from Git.

## License

MIT — demonstration/portfolio project.
