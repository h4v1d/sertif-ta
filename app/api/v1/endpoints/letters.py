import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.schemas.letter import LetterRequest, SuratTugasRequest, LembarPersetujuanRequest, PDFResponse
from app.services.pdf_generator import PDFGenerator
from app.utils import parse_indonesian_date
from datetime import datetime

router = APIRouter()
pdf_service = PDFGenerator()

@router.post("/surat-tugas", response_model=PDFResponse)
async def generate_surat_tugas(request: SuratTugasRequest):
    """
    Generate a Surat Tugas PDF from the provided SuratTugasRequest.
    
    Preprocesses the request.school_info to remove redundant kelurahan/kecamatan if they appear in alamat_jalan, converts the request into a generic LetterRequest for the PDF service, and constructs a custom filename in the form "SURAT_TUGAS_{FIRST_ASSIGNEE}_{dd-mm-yyyy}.pdf". Returns a PDFResponse pointing to the generated file.
    
    Parameters:
        request (SuratTugasRequest): Input data for the Surat Tugas; its fields are mapped into the PDF template and used to build the output filename.
    
    Returns:
        PDFResponse: Contains `filename` (generated file name), `file_url` (download endpoint), and `file_size` (bytes).
    
    Raises:
        HTTPException: Raised with status_code 500 if PDF generation or file handling fails.
    """
    try:
        # Pre-process School Info to ensure Address fits in 1 line (2 lines total with phone)
        # Fix duplication issues like "Tunjungtirto, Tunjungtirto"
        school = request.school_info
        addr = school.alamat_jalan

        if school.kelurahan and school.kelurahan in addr:
            school.kelurahan = None
        if school.kecamatan and school.kecamatan in addr:
            school.kecamatan = None

        # Convert specific request to generic LetterRequest for the service
        generic_request = LetterRequest(
            template_type="surat_tugas",
            nomor_surat=request.nomor_surat,
            tanggal_surat=request.tanggal_surat,
            perihal=request.perihal,
            tempat_surat=request.tempat_surat,
            school_info=request.school_info,
            penandatangan=request.penandatangan,
            content={
                "assignees": request.assignees,
                "details": request.details,
                "pembuka": request.pembuka,
                "penutup": request.penutup
            }
        )

        # Custom Filename: SURAT_TUGAS_{NAME}_dd-mm-yyyy.pdf
        first_assignee = request.assignees[0].nama.replace(" ", "_").upper() if request.assignees else "UNKNOWN"
        date_str = parse_indonesian_date(request.tanggal_surat)
        custom_filename = f"SURAT_TUGAS_{first_assignee}_{date_str}.pdf"

        file_path = pdf_service.generate(generic_request, custom_filename=custom_filename)
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)

        return PDFResponse(
            filename=filename,
            file_url=f"/api/v1/letters/download/{filename}",
            file_size=file_size
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.post("/lembar-persetujuan", response_model=PDFResponse)
async def generate_lembar_persetujuan(request: LembarPersetujuanRequest):
    """Specific endpoint for Lembar Persetujuan PKL."""
    try:
        # Pre-process School Info
        school = request.school_info
        addr = school.alamat_jalan
        if school.kelurahan and school.kelurahan in addr:
            school.kelurahan = None
        if school.kecamatan and school.kecamatan in addr:
            school.kecamatan = None

        # Convert specific request to generic LetterRequest
        generic_request = LetterRequest(
            template_type="lembar_persetujuan",
            nomor_surat="PKL/PST/001",  # Placeholder, not shown in template
            tanggal_surat=datetime.now().strftime("%d %B %Y"), # Placeholder
            perihal="LEMBAR PERSETUJUAN",
            school_info=request.school_info,
            penandatangan=request.students[0], # Placeholder required by schema
            content={
                "students": request.students,
                "nama_perusahaan": request.nama_perusahaan,
                "tempat_tanggal": request.tempat_tanggal
            }
        )

        # Custom Filename: LEMBAR_PERSETUJUAN_{COMPANY}_{DATE}.pdf
        company_name = request.nama_perusahaan.replace(" ", "_").upper()
        date_str = datetime.now().strftime("%d-%m-%Y")
        custom_filename = f"LEMBAR_PERSETUJUAN_{company_name}_{date_str}.pdf"

        file_path = pdf_service.generate(generic_request, custom_filename=custom_filename)
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)

        return PDFResponse(
            filename=filename,
            file_url=f"/api/v1/letters/download/{filename}",
            file_size=file_size
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.get("/download/{filename}")
async def download_letter(filename: str):
    # Basic path traversal protection
    if ".." in filename or "/" in filename:
         raise HTTPException(status_code=400, detail="Invalid filename")

    file_path = f"output/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path, media_type="application/pdf", filename=filename)