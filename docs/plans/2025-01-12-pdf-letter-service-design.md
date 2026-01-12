# PDF Letter Microservice Design

## Overview
FastAPI-based microservice untuk generating surat formal PDF secara dinamis dari JSON data dan HTML templates.

## Tech Stack
- **FastAPI** - Web framework dengan async support & auto-documentation
- **Jinja2** - Template engine untuk HTML templates
- **WeasyPrint** - HTML to PDF converter (CSS paged media support)
- **Pydantic** - Data validation & serialization
- **Pytest** - Testing framework

## Project Structure
```
fastapi-pdf-service/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── api/                 # API routers
│   │   └── v1/
│   │       └── letters.py   # Letter generation endpoint
│   ├── models/              # Pydantic models
│   │   └── letter.py        # Request/response schemas
│   ├── templates/           # Jinja2 templates (HTML)
│   │   ├── base.html        # Base template dengan kop surat
│   │   ├── surat_dinas.html
│   │   ├── surat_edaran.html
│   │   └── surat_pemberitahuan.html
│   ├── services/            # Business logic
│   │   └── pdf_generator.py # PDF generation service
│   └── static/              # Assets
│       └── logo.png
├── tests/
├── docs/
└── requirements.txt
```

## API Endpoints

### POST /api/v1/letters/generate
Generate PDF dari JSON data

**Request:**
```json
{
  "type": "surat_dinas",
  "data": {
    "nomor": "123/IT/X/2025",
    "tanggal": "12 Januari 2025",
    "perihal": "Undangan Rapat",
    "penerima": {
      "nama": "Budi Santoso",
      "jabatan": "Manager IT"
    },
    "isi": "Dengan hormat, Mengundang Anda untuk...",
    "penandatangan": {
      "nama": "Ahmad Direktur",
      "jabatan": "Direktur Utama"
    }
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "PDF generated successfully",
  "data": {
    "filename": "surat_dinas_123_IT_X_2025.pdf",
    "size_bytes": 45678,
    "download_url": "/api/v1/letters/download/{uuid}"
  }
}
```

### GET /api/v1/letters/templates
List available templates

### GET /api/v1/letters/download/{uuid}
Download generated PDF (temporary link, 15 min expiry)

### GET /api/v1/letters/preview/{uuid}
Preview PDF in browser

### GET /docs
Auto-generated Swagger UI documentation

## Data Models

```python
class Penerima(BaseModel):
    nama: str
    jabatan: str = ""

class Penandatangan(BaseModel):
    nama: str
    jabatan: str

class LetterData(BaseModel):
    nomor: str
    tanggal: str
    perihal: str
    penerima: Penerima
    isi: str
    penandatangan: Penandatangan

class GenerateLetterRequest(BaseModel):
    type: Literal["surat_dinas", "surat_edaran", "surat_pemberitahuan"]
    data: LetterData
```

## PDF Generation Service

```python
class PDFGenerator:
    def __init__(self):
        self.jinja_env = Environment(
            loader=FileSystemLoader("app/templates"),
            autoescape=False
        )

    async def generate(
        self,
        template_type: str,
        data: LetterData
    ) -> bytes:
        # 1. Render HTML dari Jinja2 template
        template = self.jinja_env.get_template(f"{template_type}.html")
        html = template.render(**data.model_dump())

        # 2. Convert HTML ke PDF via WeasyPrint
        pdf_bytes = HTML(string=html).write_pdf()

        return pdf_bytes
```

## Storage Strategy
- Temporary storage: `/tmp/pdfs/` dengan UUID filename
- Expiry: Auto-delete setelah 15 menit (background task)
- No database: Stateless service

## Error Handling

| Error | Status Code | Response |
|-------|-------------|----------|
| Invalid template | 400 | `{"error": "Template not found: X"}` |
| Validation failed | 422 | Pydantic auto-validation |
| PDF generation failed | 500 | `{"error": "Failed to generate PDF"}` |

## Dependencies
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
weasyprint==60.2
jinja2==3.1.3
pydantic==2.5.3
python-multipart==0.0.6
pytest==8.0.0
httpx==0.26.0  # for testing
```

## Quick Start
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pytest tests/ -v
```

## Future Enhancements (Post-MVP)
- Bulk generation dari DOCX parsing
- Template dinamis via database admin
- Sertifikat dengan QR code
- Rate limiting & authentication (API Key/JWT)
- Cloud storage for PDF persistence
- Multi-organization support (dynamic kop surat)
