# DocuLab

All-in-one document, PDF and image toolkit.

## Requirements

- Windows
- Python 3.14
- LibreOffice installed and available as `soffice`
- Node.js 24+

## Backend

From the project root:

```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r backend\requirements.txt
python -m uvicorn backend.app.main:app --reload
```

API:
- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs

## Frontend

In a second terminal:

```bat
cd frontend
npm install
npm run dev
```

The frontend normally opens at the Vite local URL shown in the terminal.

## Notes

This is a working development foundation. PDF-to-Word quality depends on LibreOffice and the source PDF. Scanned PDFs need OCR, which is planned as a separate module.
