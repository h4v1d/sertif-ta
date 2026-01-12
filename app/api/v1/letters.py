"""
API endpoints for PDF letter generation.

NOTE: This implementation uses in-memory storage (pdf_storage dict) which is
suitable for single-worker deployments. For multi-worker or production deployments,
consider using Redis or a database for PDF storage.
"""
import uuid
from pathlib import Path
from typing import Dict

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.models import GenerateLetterRequest, GenerateLetterResponse
from app.services.pdf_generator import PDFGenerator


router = APIRouter(prefix="/letters", tags=["letters"])

# In-memory PDF storage (doc_id -> filepath mapping)
pdf_storage: Dict[str, str] = {}

# Initialize PDF generator
pdf_generator = PDFGenerator()


@router.get("/templates")
async def list_templates() -> dict[str, object]:
    """
    List available letter templates.

    Returns a list of supported template types that can be used
    for PDF generation.
    """
    return {
        "templates": PDFGenerator.SUPPORTED_TEMPLATES,
        "count": len(PDFGenerator.SUPPORTED_TEMPLATES)
    }


@router.post("/generate", response_model=GenerateLetterResponse)
async def generate_letter(request: GenerateLetterRequest):
    """
    Generate a PDF letter from JSON data.

    Takes a letter type and data, then generates a PDF using the
    appropriate template. Returns a download URL for the generated PDF.
    """
    try:
        # Convert request to dict for PDF generator
        data_dict = request.data.model_dump()

        # Generate PDF bytes
        pdf_bytes = pdf_generator.generate(
            template_name=request.type,
            data=data_dict
        )

        # Generate unique document ID
        doc_id = str(uuid.uuid4())

        # Create filename from letter number
        safe_filename = f"{request.data.nomor.replace('/', '-')}_{request.type}"

        # Save PDF to output directory
        filepath = pdf_generator.save_pdf(pdf_bytes, safe_filename)

        # Store mapping in memory
        pdf_storage[doc_id] = filepath

        # Generate download URL
        download_url = f"/api/v1/letters/download/{doc_id}"

        return GenerateLetterResponse(
            success=True,
            message="PDF generated successfully",
            data={
                "doc_id": doc_id,
                "download_url": download_url,
                "filename": Path(filepath).name
            }
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate PDF: {str(e)}"
        )


@router.get("/download/{doc_id}")
async def download_pdf(doc_id: str):
    """
    Download a generated PDF by document ID.

    Returns the PDF file as a download attachment.
    """
    if doc_id not in pdf_storage:
        raise HTTPException(
            status_code=404,
            detail=f"Document with ID '{doc_id}' not found"
        )

    filepath = pdf_storage[doc_id]

    if not Path(filepath).exists():
        # Remove from storage if file doesn't exist
        del pdf_storage[doc_id]
        raise HTTPException(
            status_code=404,
            detail=f"PDF file not found on disk"
        )

    return FileResponse(
        path=filepath,
        media_type="application/pdf",
        filename=Path(filepath).name
    )


@router.get("/preview/{doc_id}")
async def preview_pdf(doc_id: str):
    """
    Preview a generated PDF in the browser.

    Returns the PDF file for inline display in the browser.
    """
    if doc_id not in pdf_storage:
        raise HTTPException(
            status_code=404,
            detail=f"Document with ID '{doc_id}' not found"
        )

    filepath = pdf_storage[doc_id]

    if not Path(filepath).exists():
        # Remove from storage if file doesn't exist
        del pdf_storage[doc_id]
        raise HTTPException(
            status_code=404,
            detail=f"PDF file not found on disk"
        )

    return FileResponse(
        path=filepath,
        media_type="application/pdf",
        filename=Path(filepath).name,
        headers={"Content-Disposition": "inline"}
    )
