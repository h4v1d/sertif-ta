# PDF Letter Service - API Documentation

## Overview

The PDF Letter Service is a RESTful API for generating formal PDF letters from JSON data. The service supports multiple Indonesian letter templates including official letters (surat_dinas), announcements (surat_edaran), and notifications (surat_pemberitahuan).

**Base URL:** `http://localhost:8000`

**API Version:** v1

**Content Type:** `application/json`

---

## Endpoints

### 1. Health Check

Check if the service is running.

**Endpoint:** `GET /health`

**Authentication:** None required

**Response:**
```json
{
  "status": "healthy"
}
```

**Status Codes:**
- `200 OK`: Service is healthy

---

### 2. List Templates

Get a list of available letter templates.

**Endpoint:** `GET /api/v1/letters/templates`

**Authentication:** None required

**Response:**
```json
{
  "templates": [
    "surat_dinas",
    "surat_edaran",
    "surat_pemberitahuan"
  ],
  "count": 3
}
```

**Status Codes:**
- `200 OK`: Templates retrieved successfully

---

### 3. Generate Letter

Generate a PDF letter from JSON data.

**Endpoint:** `POST /api/v1/letters/generate`

**Authentication:** None required

**Request Body:**
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
    "isi": "Dengan hormat,\n\nKami mengundang Anda untuk menghadiri rapat evaluasi kinerja triwulan yang akan diselenggarakan pada:\n\nHari/Tanggal : Senin, 15 Januari 2025\nWaktu        : 09.00 - 12.00 WIB\nTempat       : Ruang Rapat Utama Lt. 3\n\nDemikian undangan ini kami sampaikan. Atas perhatian dan kehadiran Anda, kami ucapkan terima kasih.",
    "penandatangan": {
      "nama": "Ahmad",
      "jabatan": "Direktur"
    }
  }
}
```

**Request Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| type | string | Yes | Letter template type. Must be one of: `surat_dinas`, `surat_edaran`, `surat_pemberitahuan` |
| data | object | Yes | Letter data object |
| data.nomor | string | Yes | Letter number (e.g., "123/IT/X/2025") |
| data.tanggal | string | Yes | Letter date in Indonesian format |
| data.perihal | string | Yes | Subject of the letter |
| data.penerima | object | Yes | Recipient information |
| data.penerima.nama | string | Yes | Recipient name |
| data.penerima.jabatan | string | No | Recipient position/title |
| data.isi | string | Yes | Letter body content (supports \n for line breaks) |
| data.penandatangan | object | Yes | Signatory information |
| data.penandatangan.nama | string | Yes | Signatory name |
| data.penandatangan.jabatan | string | Yes | Signatory position/title |

**Success Response:**
```json
{
  "success": true,
  "message": "PDF generated successfully",
  "data": {
    "doc_id": "550e8400-e29b-41d4-a716-446655440000",
    "download_url": "/api/v1/letters/download/550e8400-e29b-41d4-a716-446655440000",
    "filename": "123-IT-X-2025_surat_dinas.pdf"
  }
}
```

**Status Codes:**
- `200 OK`: PDF generated successfully
- `400 Bad Request`: Invalid request data or unsupported template type
- `500 Internal Server Error`: Failed to generate PDF

---

### 4. Download PDF

Download a generated PDF file as an attachment.

**Endpoint:** `GET /api/v1/letters/download/{doc_id}`

**Authentication:** None required

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| doc_id | string | Yes | Unique document ID returned from generate endpoint |

**Response:**
- Content-Type: `application/pdf`
- Content-Disposition: `attachment; filename="<filename>.pdf"`
- Body: PDF file binary data

**Status Codes:**
- `200 OK`: PDF file returned successfully
- `404 Not Found`: Document ID not found or PDF file not on disk

---

### 5. Preview PDF

Preview a generated PDF file inline in the browser.

**Endpoint:** `GET /api/v1/letters/preview/{doc_id}`

**Authentication:** None required

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| doc_id | string | Yes | Unique document ID returned from generate endpoint |

**Response:**
- Content-Type: `application/pdf`
- Content-Disposition: `inline`
- Body: PDF file binary data

**Status Codes:**
- `200 OK`: PDF file returned successfully
- `404 Not Found`: Document ID not found or PDF file not on disk

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message description"
}
```

### Common Error Codes

| Status Code | Description |
|-------------|-------------|
| 400 | Bad Request - Invalid input data or parameters |
| 404 | Not Found - Resource or document not found |
| 500 | Internal Server Error - Server-side error occurred |

### Error Examples

**Invalid Template Type:**
```json
{
  "detail": "Template 'invalid_type' is not supported. Supported templates: surat_dinas, surat_edaran, surat_pemberitahuan"
}
```

**Document Not Found:**
```json
{
  "detail": "Document with ID '550e8400-e29b-41d4-a716-446655440000' not found"
}
```

**PDF File Not on Disk:**
```json
{
  "detail": "PDF file not found on disk"
}
```

---

## Usage Examples

### Example 1: Generate Surat Dinas

```bash
curl -X POST http://localhost:8000/api/v1/letters/generate \
  -H "Content-Type: application/json" \
  -d '{
    "type": "surat_dinas",
    "data": {
      "nomor": "001/DIR/IX/2025",
      "tanggal": "12 Januari 2025",
      "perihal": "Rapat Koordinasi Proyek",
      "penerima": {
        "nama": "Budi Santoso",
        "jabatan": "Manager Proyek"
      },
      "isi": "Dengan hormat,\n\nSehubungan dengan pelaksanaan proyek pengembangan sistem, kami meminta kehadiran Bapak/Ibu untuk menghadiri rapat koordinasi.\n\nHari/Tanggal : Senin, 15 Januari 2025\nWaktu        : 10.00 - 12.00 WIB\nTempat       : Ruang Rapat Lt. 2\n\nMohon konfirmasi kehadiran.",
      "penandatangan": {
        "nama": "Drs. H. Ahmad Fauzi",
        "jabatan": "Direktur Utama"
      }
    }
  }'
```

### Example 2: Generate Surat Edaran

```bash
curl -X POST http://localhost:8000/api/v1/letters/generate \
  -H "Content-Type: application/json" \
  -d '{
    "type": "surat_edaran",
    "data": {
      "nomor": "005/HRD/I/2025",
      "tanggal": "12 Januari 2025",
      "perihal": "Libur Nasional",
      "penerima": {
        "nama": "Seluruh Karyawan",
        "jabatan": ""
      },
      "isi": "Diberitahukan kepada seluruh karyawan bahwa dalam rangka hari raya, kantor akan libur pada tanggal 17-18 Januari 2025. Kantor kembali beroperasi normal pada tanggal 20 Januari 2025.\n\nDemikian edaran ini disampaikan untuk diperhatikan.",
      "penandatangan": {
        "nama": "Siti Aminah",
        "jabatan": "HRD Manager"
      }
    }
  }'
```

### Example 3: Download Generated PDF

```bash
# First get the doc_id from generate response
DOC_ID="550e8400-e29b-41d4-a716-446655440000"

# Download the PDF
curl -O http://localhost:8000/api/v1/letters/download/$DOC_ID
```

### Example 4: Preview PDF in Browser

Simply navigate to the preview URL in your browser:
```
http://localhost:8000/api/v1/letters/preview/550e8400-e29b-41d4-a716-446655440000
```

---

## Interactive API Documentation

The service provides interactive API documentation powered by Swagger UI and ReDoc:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

These interfaces allow you to:
- Browse all available endpoints
- View request/response schemas
- Test API endpoints directly from the browser

---

## Notes

### Storage Implementation

The current implementation uses in-memory storage (`pdf_storage` dict) which is suitable for:
- Single-worker deployments
- Development and testing environments
- Stateless scenarios with short-lived PDF URLs

For production deployments with multiple workers or persistent PDF storage, consider using:
- Redis for distributed caching
- Database storage for document metadata
- Object storage (S3, GCS) for PDF files

### PDF Cleanup

Generated PDFs are stored in the `output/` directory. Implement a cleanup strategy for production:
- Scheduled cleanup jobs for old files
- TTL-based expiration for document IDs
- Manual cleanup endpoint with authentication

### Security Considerations

- The service implements path traversal protection for PDF filenames
- PDF size is limited to 10MB to prevent disk exhaustion
- Jinja2 templates use autoescape to prevent XSS attacks
- Consider adding authentication/authorization for production use
- Implement rate limiting to prevent abuse

### Template Customization

Templates are stored in `app/templates/` directory. To add custom templates:
1. Create a new HTML file in the templates directory
2. Add the template name to `SUPPORTED_TEMPLATES` in `PDFGenerator`
3. Update the `Literal` type hint in `GenerateLetterRequest` model

---

## Support

For issues, questions, or contributions, please refer to the project repository.
