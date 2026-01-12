# PDF Letter Microservice

FastAPI-based microservice untuk generate surat formal PDF dari JSON data.

## Installation

```bash
pip install -e .
```

## Running

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API Documentation: http://localhost:8000/docs

## API Usage

### Generate Letter

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
      "isi": "Dengan hormat...\n\nIsi surat...",
      "penandatangan": {"nama": "Ahmad", "jabatan": "Direktur"}
    }
  }'
```

## Testing

```bash
pytest tests/ -v
```
