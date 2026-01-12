# PDF Letter Microservice Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build FastAPI microservice untuk generate surat formal PDF dari JSON data dan HTML templates.

**Architecture:** Stateless FastAPI service dengan Jinja2 untuk template rendering dan WeasyPrint untuk HTML-to-PDF conversion. PDF disimpan temporary di filesystem dengan auto-expiry.

**Tech Stack:** FastAPI, Jinja2, WeasyPrint, Pydantic, Pytest

---

## Task 1: Setup Project Structure & Dependencies

**Files:**
- Create: `requirements.txt`
- Create: `pyproject.toml`
- Create: `app/__init__.py`
- Create: `app/main.py`
- Create: `.gitignore`

**Step 1: Create requirements.txt**

```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
weasyprint==60.2
jinja2==3.1.3
pydantic==2.5.3
python-multipart==0.0.6
pytest==8.0.0
httpx==0.26.0
```

Run: `cat requirements.txt`

**Step 2: Create pyproject.toml**

```toml
[project]
name = "fastapi-pdf-service"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "weasyprint>=60.2",
    "jinja2>=3.1.3",
    "pydantic>=2.5.3",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "httpx>=0.26.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = [".]
```

Run: `cat pyproject.toml`

**Step 3: Create .gitignore**

```gitignore
__pycache__/
*.py[cod]
*$py.class
.venv/
venv/
.env
*.pdf
/tmp/pdfs/
.pytest_cache/
.coverage
htmlcov/
dist/
build/
*.egg-info/
```

Run: `cat .gitignore`

**Step 4: Create app directory structure**

Run: `mkdir -p app/api/v1 app/models app/services app/templates app/static tests`

**Step 5: Create app/__init__.py**

```python
# PDF Letter Microservice
```

Run: `echo "# PDF Letter Microservice" > app/__init__.py`

**Step 6: Create minimal FastAPI app in app/main.py**

```python
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(
    title="PDF Letter Service",
    description="Microservice untuk generate surat formal PDF",
    version="0.1.0"
)

@app.get("/")
async def root():
    return JSONResponse(content={"message": "PDF Letter Service is running"})

@app.get("/health")
async def health():
    return JSONResponse(content={"status": "healthy"})
```

Run: `cat app/main.py`

**Step 7: Verify app starts**

Run: `python -c "from app.main import app; print('App imports successfully')"`

Expected: No errors, prints "App imports successfully"

**Step 8: Test the app runs**

Run: `uvicorn app.main:app --host 0.0.0.0 --port 8000 &` then `sleep 2` then `curl http://localhost:8000/`

Expected: `{"message":"PDF Letter Service is running"}`

Run: `pkill -f uvicorn`

**Step 9: Create tests directory structure**

Run: `mkdir -p tests/api/v1 tests/services`

**Step 10: Create tests/__init__.py**

Run: `touch tests/__init__.py`

**Step 11: Commit**

Run:
```bash
git init
git add requirements.txt pyproject.toml .gitignore app/ tests/
git commit -m "feat: setup project structure and FastAPI app"
```

---

## Task 2: Implement Pydantic Models

**Files:**
- Create: `app/models/__init__.py`
- Create: `app/models/letter.py`
- Create: `tests/models/test_letter.py`

**Step 1: Create app/models/__init__.py**

```python
from app.models.letter import (
    Penerima,
    Penandatangan,
    LetterData,
    GenerateLetterRequest
)

__all__ = [
    "Penerima",
    "Penandatangan",
    "LetterData",
    "GenerateLetterRequest"
]
```

Run: `cat app/models/__init__.py`

**Step 2: Create app/models/letter.py**

```python
from pydantic import BaseModel
from typing import Literal

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

class GenerateLetterResponse(BaseModel):
    success: bool
    message: str
    data: dict | None = None
```

Run: `cat app/models/letter.py`

**Step 3: Write failing tests for models**

Create `tests/models/test_letter.py`:

```python
import pytest
from app.models.letter import (
    Penerima,
    Penandatangan,
    LetterData,
    GenerateLetterRequest
)

def test_penerima_model():
    penerima = Penerima(nama="Budi Santoso", jabatan="Manager IT")
    assert penerima.nama == "Budi Santoso"
    assert penerima.jabatan == "Manager IT"

def test_penerima_jabatan_optional():
    penerima = Penerima(nama="Budi Santoso")
    assert penerima.jabatan == ""

def test_penandatangan_model():
    ttd = Penandatangan(nama="Ahmad Direktur", jabatan="Direktur Utama")
    assert ttd.nama == "Ahmad Direktur"
    assert ttd.jabatan == "Direktur Utama"

def test_letter_data_model():
    data = LetterData(
        nomor="123/IT/X/2025",
        tanggal="12 Januari 2025",
        perihal="Undangan Rapat",
        penerima={"nama": "Budi", "jabatan": "Manager"},
        isi="Isi surat...",
        penandatangan={"nama": "Direktur", "jabatan": "Direktur Utama"}
    )
    assert data.nomor == "123/IT/X/2025"
    assert data.penerima.nama == "Budi"

def test_generate_letter_request_valid_type():
    request = GenerateLetterRequest(
        type="surat_dinas",
        data={
            "nomor": "001",
            "tanggal": "12 Januari 2025",
            "perihal": "Test",
            "penerima": {"nama": "Test"},
            "isi": "Test",
            "penandatangan": {"nama": "Test", "jabatan": "Test"}
        }
    )
    assert request.type == "surat_dinas"

def test_generate_letter_request_invalid_type():
    with pytest.raises(ValueError):
        GenerateLetterRequest(
            type="invalid_type",
            data={
                "nomor": "001",
                "tanggal": "12 Januari 2025",
                "perihal": "Test",
                "penerima": {"nama": "Test"},
                "isi": "Test",
                "penandatangan": {"nama": "Test", "jabatan": "Test"}
        }
        )
```

Run: `cat tests/models/test_letter.py`

**Step 4: Run tests to verify they pass**

Run: `pytest tests/models/test_letter.py -v`

Expected: All 6 tests PASS

**Step 5: Commit**

Run:
```bash
git add app/models/ tests/models/
git commit -m "feat: add Pydantic models for letter data"
```

---

## Task 3: Implement PDF Generator Service

**Files:**
- Create: `app/services/__init__.py`
- Create: `app/services/pdf_generator.py`
- Create: `tests/services/test_pdf_generator.py`
- Create: `app/templates/base.html`
- Create: `app/templates/surat_dinas.html`

**Step 1: Create app/services/__init__.py**

```python
from app.services.pdf_generator import PDFGenerator

__all__ = ["PDFGenerator"]
```

Run: `cat app/services/__init__.py`

**Step 2: Create app/templates/base.html**

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @page {
            margin: 2.5cm;
            size: A4 portrait;
        }
        body {
            font-family: 'Times New Roman', serif;
            font-size: 12pt;
            line-height: 1.5;
            margin: 0;
            padding: 0;
        }
        .kop-surat {
            text-align: center;
            margin-bottom: 30px;
        }
        .kop-surat h1 {
            font-size: 16pt;
            margin: 5px 0;
            font-weight: bold;
        }
        .kop-surat p {
            font-size: 11pt;
            margin: 2px 0;
        }
        .nomor-surat {
            text-align: right;
            margin-bottom: 20px;
        }
        .surat-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 20px;
        }
        .perihal {
            margin-bottom: 20px;
        }
        .isi-surat {
            text-align: justify;
            line-height: 1.6;
            min-height: 300px;
        }
        .ttd-area {
            margin-top: 80px;
            float: right;
            text-align: center;
            width: 250px;
        }
        .ttd-area .nama {
            margin-top: 60px;
            font-weight: bold;
            text-decoration: underline;
        }
        .ttd-area .jabatan {
            margin-top: 5px;
        }
        .halaman {
            text-align: center;
            font-size: 10pt;
            margin-top: 20px;
        }
        .tembusan {
            margin-top: 100px;
            clear: both;
            page-break-inside: avoid;
        }
    </style>
</head>
<body>
    {% block content %}{% endblock %}
</body>
</html>
```

Run: `cat app/templates/base.html`

**Step 3: Create app/templates/surat_dinas.html**

```html
{% extends "base.html" %}

{% block content %}
<div class="kop-surat">
    <h1>PEMERINTAH KOTA CONTOH</h1>
    <p>DINAS CONTOH</p>
    <p>Jl. Contoh No. 123, Kota Contoh 12345</p>
</div>

<div class="nomor-surat">
    <p><strong>Nomor: {{ data.nomor }}</strong></p>
</div>

<div class="surat-header">
    <div>
        <p>Kepada Yth.</p>
        <p><strong>{{ data.penerima.nama }}</strong></p>
        {% if data.penerima.jabatan %}
        <p>{{ data.penerima.jabatan }}</p>
        {% endif %}
        <p>di Tempat</p>
    </div>
    <div style="text-align: right;">
        <p>Kota, {{ data.tanggal }}</p>
    </div>
</div>

<div class="perihal">
    <p><strong>Perihal: {{ data.perihal }}</strong></p>
</div>

<div class="isi-surat">
    {{ data.isi | replace('\n', '<br>') | safe }}
</div>

<div class="ttd-area">
    <p>Salam hormat,</p>
    <p class="nama">{{ data.penandatangan.nama }}</p>
    <p class="jabatan">{{ data.penandatangan.jabatan }}</p>
</div>
{% endblock %}
```

Run: `cat app/templates/surat_dinas.html`

**Step 4: Create placeholder templates**

Run:
```bash
cat > app/templates/surat_edaran.html << 'EOF'
{% extends "base.html" %}
{% block content %}
<p>Template surat edaran belum diimplementasi</p>
{% endblock %}
EOF
```

Run:
```bash
cat > app/templates/surat_pemberitahuan.html << 'EOF'
{% extends "base.html" %}
{% block content %}
<p>Template surat pemberitahuan belum diimplementasi</p>
{% endblock %}
EOF
```

**Step 5: Create PDF generator service**

Create `app/services/pdf_generator.py`:

```python
import os
import uuid
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from app.models.letter import LetterData

class PDFGenerator:
    def __init__(self, template_dir: str = "app/templates"):
        self.template_dir = Path(template_dir)
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=False
        )
        self.output_dir = Path("/tmp/pdfs")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(
        self,
        template_type: str,
        data: LetterData
    ) -> tuple[bytes, str]:
        template_path = f"{template_type}.html"

        if not (self.template_dir / template_path).exists():
            raise ValueError(f"Template not found: {template_type}")

        template = self.jinja_env.get_template(template_path)
        html = template.render(data=data.model_dump())

        pdf_bytes = HTML(string=html).write_pdf()

        filename = f"{template_type}_{uuid.uuid4().hex}.pdf"

        return pdf_bytes, filename

    def save_pdf(self, pdf_bytes: bytes, filename: str) -> Path:
        filepath = self.output_dir / filename
        filepath.write_bytes(pdf_bytes)
        return filepath
```

Run: `cat app/services/pdf_generator.py`

**Step 6: Write test for PDF generator**

Create `tests/services/test_pdf_generator.py`:

```python
import pytest
from pathlib import Path
from app.services.pdf_generator import PDFGenerator
from app.models.letter import LetterData

@pytest.fixture
def generator():
    return PDFGenerator()

@pytest.fixture
def sample_letter_data():
    return LetterData(
        nomor="123/IT/X/2025",
        tanggal="12 Januari 2025",
        perihal="Undangan Rapat",
        penerima={"nama": "Budi Santoso", "jabatan": "Manager IT"},
        isi="Dengan hormat,\n\nKami mengundang Anda untuk menghadiri rapat.",
        penandatangan={"nama": "Ahmad Direktur", "jabatan": "Direktur Utama"}
    )

def test_generator_initializes(generator):
    assert generator.template_dir == Path("app/templates")
    assert generator.output_dir == Path("/tmp/pdfs")

def test_generate_pdf_returns_bytes(generator, sample_letter_data):
    pdf_bytes, filename = generator.generate("surat_dinas", sample_letter_data)

    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0
    assert filename.endswith(".pdf")

def test_generate_pdf_invalid_template(generator, sample_letter_data):
    with pytest.raises(ValueError, match="Template not found"):
        generator.generate("invalid_template", sample_letter_data)

def test_save_pdf_creates_file(generator, sample_letter_data):
    pdf_bytes, filename = generator.generate("surat_dinas", sample_letter_data)
    filepath = generator.save_pdf(pdf_bytes, filename)

    assert filepath.exists()
    assert filepath.stat().st_size > 0

    # Cleanup
    filepath.unlink()
```

Run: `cat tests/services/test_pdf_generator.py`

**Step 7: Run tests**

Run: `pytest tests/services/test_pdf_generator.py -v`

Expected: All 5 tests PASS

**Step 8: Commit**

Run:
```bash
git add app/services/ app/templates/ tests/services/
git commit -m "feat: add PDF generator service with Jinja2 templates"
```

---

## Task 4: Implement API Endpoint

**Files:**
- Create: `app/api/__init__.py`
- Create: `app/api/v1/__init__.py`
- Create: `app/api/v1/letters.py`
- Modify: `app/main.py`
- Create: `tests/api/v1/test_letters.py`

**Step 1: Create app/api/__init__.py**

Run: `touch app/api/__init__.py`

**Step 2: Create app/api/v1/__init__.py**

Run: `touch app/api/v1/__init__.py`

**Step 3: Create letters router**

Create `app/api/v1/letters.py`:

```python
import uuid
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse
from app.models.letter import (
    GenerateLetterRequest,
    GenerateLetterResponse
)
from app.services.pdf_generator import PDFGenerator

router = APIRouter(prefix="/letters", tags=["letters"])

generator = PDFGenerator()
pdf_storage = {}

@router.get("/templates")
async def list_templates():
    return {
        "templates": [
            {"type": "surat_dinas", "name": "Surat Dinas"},
            {"type": "surat_edaran", "name": "Surat Edaran"},
            {"type": "surat_pemberitahuan", "name": "Surat Pemberitahuan"}
        ]
    }

@router.post("/generate", response_model=GenerateLetterResponse)
async def generate_letter(request: GenerateLetterRequest):
    try:
        pdf_bytes, filename = generator.generate(request.type, request.data)
        filepath = generator.save_pdf(pdf_bytes, filename)

        doc_id = str(uuid.uuid4())
        pdf_storage[doc_id] = {"filepath": filepath, "filename": filename}

        return GenerateLetterResponse(
            success=True,
            message="PDF generated successfully",
            data={
                "filename": filename,
                "size_bytes": len(pdf_bytes),
                "download_url": f"/api/v1/letters/download/{doc_id}"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

@router.get("/download/{doc_id}")
async def download_pdf(doc_id: str):
    if doc_id not in pdf_storage:
        raise HTTPException(status_code=404, detail="PDF not found")

    pdf_info = pdf_storage[doc_id]
    return FileResponse(
        path=pdf_info["filepath"],
        filename=pdf_info["filename"],
        media_type="application/pdf"
    )

@router.get("/preview/{doc_id}")
async def preview_pdf(doc_id: str):
    if doc_id not in pdf_storage:
        raise HTTPException(status_code=404, detail="PDF not found")

    pdf_info = pdf_storage[doc_id]
    return FileResponse(
        path=pdf_info["filepath"],
        media_type="application/pdf"
    )
```

Run: `cat app/api/v1/letters.py`

**Step 4: Update app/main.py to include router**

```python
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.api.v1 import letters

app = FastAPI(
    title="PDF Letter Service",
    description="Microservice untuk generate surat formal PDF",
    version="0.1.0"
)

app.include_router(letters.router, prefix="/api/v1")

@app.get("/")
async def root():
    return JSONResponse(content={"message": "PDF Letter Service is running"})

@app.get("/health")
async def health():
    return JSONResponse(content={"status": "healthy"})
```

Run: `cat app/main.py`

**Step 5: Write API tests**

Create `tests/api/v1/test_letters.py`:

```python
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_list_templates(client):
    response = await client.get("/api/v1/letters/templates")
    assert response.status_code == 200
    data = response.json()
    assert "templates" in data
    assert len(data["templates"]) == 3

@pytest.mark.asyncio
async def test_generate_letter_success(client):
    payload = {
        "type": "surat_dinas",
        "data": {
            "nomor": "001/TEST/X/2025",
            "tanggal": "12 Januari 2025",
            "perihal": "Test Surat",
            "penerima": {
                "nama": "Test User",
                "jabatan": "Tester"
            },
            "isi": "Ini adalah test surat.\n\nBaris kedua.",
            "penandatangan": {
                "nama": "Test TTD",
                "jabatan": "Test Manager"
            }
        }
    }
    response = await client.post("/api/v1/letters/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "download_url" in data["data"]

@pytest.mark.asyncio
async def test_generate_letter_invalid_template(client):
    payload = {
        "type": "invalid_template",
        "data": {
            "nomor": "001",
            "tanggal": "12 Januari 2025",
            "perihal": "Test",
            "penerima": {"nama": "Test"},
            "isi": "Test",
            "penandatangan": {"nama": "Test", "jabatan": "Test"}
        }
    }
    response = await client.post("/api/v1/letters/generate", json=payload)
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_download_pdf_after_generation(client):
    payload = {
        "type": "surat_dinas",
        "data": {
            "nomor": "002/TEST/X/2025",
            "tanggal": "12 Januari 2025",
            "perihal": "Test Download",
            "penerima": {"nama": "Test"},
            "isi": "Test",
            "penandatangan": {"nama": "Test", "jabatan": "Test"}
        }
    }
    gen_response = await client.post("/api/v1/letters/generate", json=payload)
    download_url = gen_response.json()["data"]["download_url"]
    doc_id = download_url.split("/")[-1]

    download_response = await client.get(f"/api/v1/letters/download/{doc_id}")
    assert download_response.status_code == 200
    assert download_response.headers["content-type"] == "application/pdf"

@pytest.mark.asyncio
async def test_download_pdf_invalid_id(client):
    response = await client.get("/api/v1/letters/download/invalid-id")
    assert response.status_code == 404
```

Run: `cat tests/api/v1/test_letters.py`

**Step 6: Create tests/api/v1/__init__.py**

Run: `touch tests/api/v1/__init__.py`

**Step 7: Run all tests**

Run: `pytest tests/ -v`

Expected: All tests PASS

**Step 8: Manual test - start server**

Run: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &`

Expected: Server starts on port 8000

**Step 9: Test API endpoint**

Run:
```bash
curl -X POST http://localhost:8000/api/v1/letters/generate \
  -H "Content-Type: application/json" \
  -d '{
    "type": "surat_dinas",
    "data": {
      "nomor": "123/IT/X/2025",
      "tanggal": "12 Januari 2025",
      "perihal": "Undangan Rapat",
      "penerima": {"nama": "Budi Santoso", "jabatan": "Manager IT"},
      "isi": "Dengan hormat, kami mengundang Anda.",
      "penandatangan": {"nama": "Ahmad", "jabatan": "Direktur"}
    }
  }'
```

Expected: JSON response with `success: true` and `download_url`

**Step 10: Stop server**

Run: `pkill -f uvicorn`

**Step 11: Commit**

Run:
```bash
git add app/api/ app/main.py tests/api/
git commit -m "feat: add letter generation API endpoint"
```

---

## Task 5: Add Background Cleanup Task

**Files:**
- Modify: `app/main.py`
- Create: `app/services/cleanup.py`
- Create: `tests/services/test_cleanup.py`

**Step 1: Create cleanup service**

Create `app/services/cleanup.py`:

```python
import asyncio
import time
from pathlib import Path
from datetime import datetime, timedelta

class PDFCleanupService:
    def __init__(self, pdf_dir: str = "/tmp/pdfs", expiry_minutes: int = 15):
        self.pdf_dir = Path(pdf_dir)
        self.expiry_minutes = expiry_minutes
        self.running = False

    async def cleanup_old_pdfs(self):
        now = time.time()
        expiry_seconds = self.expiry_minutes * 60

        for pdf_file in self.pdf_dir.glob("*.pdf"):
            file_age = now - pdf_file.stat().st_mtime
            if file_age > expiry_seconds:
                pdf_file.unlink()

    async def start_cleanup_task(self, interval_seconds: int = 300):
        self.running = True
        while self.running:
            await self.cleanup_old_pdfs()
            await asyncio.sleep(interval_seconds)

    def stop(self):
        self.running = False
```

Run: `cat app/services/cleanup.py`

**Step 2: Write cleanup tests**

Create `tests/services/test_cleanup.py`:

```python
import pytest
import asyncio
from pathlib import Path
from app.services.cleanup import PDFCleanupService

@pytest.fixture
def cleanup_service(tmp_path):
    return PDFCleanupService(pdf_dir=str(tmp_path), expiry_minutes=0)

def test_cleanup_removes_old_files(cleanup_service, tmp_path):
    old_file = tmp_path / "old.pdf"
    old_file.write_bytes(b"test content")

    asyncio.run(cleanup_service.cleanup_old_pdfs())

    assert not old_file.exists()

def test_cleanup_keeps_recent_files(tmp_path):
    service = PDFCleanupService(pdf_dir=str(tmp_path), expiry_minutes=15)
    new_file = tmp_path / "new.pdf"
    new_file.write_bytes(b"test content")

    asyncio.run(service.cleanup_old_pdfs())

    assert new_file.exists()
```

Run: `cat tests/services/test_cleanup.py`

**Step 3: Run cleanup tests**

Run: `pytest tests/services/test_cleanup.py -v`

Expected: All tests PASS

**Step 4: Commit**

Run:
```bash
git add app/services/cleanup.py tests/services/test_cleanup.py
git commit -m "feat: add PDF cleanup service for file expiry"
```

---

## Task 6: Final Integration & Documentation

**Files:**
- Create: `README.md`
- Create: `docs/api-documentation.md`
- Modify: `app/services/__init__.py`

**Step 1: Update app/services/__init__.py**

```python
from app.services.pdf_generator import PDFGenerator
from app.services.cleanup import PDFCleanupService

__all__ = ["PDFGenerator", "PDFCleanupService"]
```

Run: `cat app/services/__init__.py`

**Step 2: Create README.md**

```markdown
# PDF Letter Microservice

FastAPI-based microservice untuk generate surat formal PDF dari JSON data.

## Installation

```bash
pip install -r requirements.txt
```

## Running

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API Documentation: http://localhost:8000/docs

## API Usage

### Generate Letter

```bash
curl -X POST http://localhost:8000/api/v1/letters/generate \\
  -H "Content-Type: application/json" \\
  -d '{
    "type": "surat_dinas",
    "data": {
      "nomor": "123/IT/X/2025",
      "tanggal": "12 Januari 2025",
      "perihal": "Undangan Rapat",
      "penerima": {"nama": "Budi Santoso", "jabatan": "Manager IT"},
      "isi": "Dengan hormat...\\n\\nIsi surat...",
      "penandatangan": {"nama": "Ahmad", "jabatan": "Direktur"}
    }
  }'
```

## Testing

```bash
pytest tests/ -v
```
```

Run: `cat README.md`

**Step 3: Create docs/api-documentation.md**

```markdown
# API Documentation

## Endpoints

### POST /api/v1/letters/generate

Generate PDF letter from JSON data.

**Request:**
```json
{
  "type": "surat_dinas",
  "data": {
    "nomor": "string",
    "tanggal": "string",
    "perihal": "string",
    "penerima": {
      "nama": "string",
      "jabatan": "string (optional)"
    },
    "isi": "string",
    "penandatangan": {
      "nama": "string",
      "jabatan": "string"
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
    "filename": "string",
    "size_bytes": number,
    "download_url": "string"
  }
}
```

### GET /api/v1/letters/templates

List available letter templates.

### GET /api/v1/letters/download/{doc_id}

Download generated PDF.

## Error Codes

- 400: Invalid template type
- 404: PDF not found or expired
- 422: Validation error
- 500: Internal server error
```

Run: `cat docs/api-documentation.md`

**Step 4: Run full test suite**

Run: `pytest tests/ -v --cov=app`

Expected: All tests pass with coverage report

**Step 5: Verify server starts and docs work**

Run: `uvicorn app.main:app --host 0.0.0.0 --port 8000 &`

Expected: Server starts successfully

Run: `curl http://localhost:8000/docs | head -20`

Expected: HTML output for Swagger UI

Run: `pkill -f uvicorn`

**Step 6: Final commit**

Run:
```bash
git add README.md docs/
git commit -m "docs: add README and API documentation"
```

---

## Summary

Total tasks: 6
Total estimated steps: ~50

Tech stack used:
- FastAPI for web framework
- Pydantic for validation
- Jinja2 for templating
- WeasyPrint for PDF generation
- Pytest for testing

All code follows TDD, DRY, YAGNI principles with frequent commits.
