import os
import re
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.schemas.letter import LetterRequest, SuratTugasRequest, LembarPersetujuanRequest, PDFResponse, Person
from app.services.pdf_generator import PDFGenerator
from app.utils import parse_indonesian_date, preprocess_school_info, get_next_increment
from app.core import get_logger
from datetime import datetime

router = APIRouter(tags=["letters"])
pdf_service = PDFGenerator()
logger = get_logger(__name__)

@router.post("/surat-tugas", response_model=PDFResponse, summary="Generate Surat Tugas PDF")
async def generate_surat_tugas(request: SuratTugasRequest):
    """
    Generate Surat Tugas (Assignment Letter) PDF document.

    Creates a professionally formatted assignment letter containing:
    - School letterhead (kop surat) with logo
    - Letter number, date, and location
    - Assignee details (one or more persons)
    - Assignment details (key-value pairs)
    - Signatory section

    **Request Body:**
    - `nomor_surat`: Letter number (e.g., "800/123/SMK.2/2024")
    - `tanggal_surat`: Date in Indonesian format (e.g., "1 Juli 2024")
    - `tempat_surat`: Place of issue (optional)
    - `perihal`: Subject (default: "SURAT TUGAS")
    - `school_info`: Complete school information
    - `penandatangan`: Signatory details
    - `assignees`: Array of assigned persons
    - `details`: Array of key-value items for assignment details
    - `pembuka`: Opening paragraph (optional)
    - `penutup`: Closing paragraph (optional)

    **Response:**
    Returns filename, download URL, and file size in bytes.

    **Filename Format:** `SURAT_TUGAS_{FIRST_ASSIGNEE}_{dd-mm-yyyy}.pdf`
    """
    try:
        logger.info(f"Generating Surat Tugas: {request.nomor_surat} for {request.school_info.nama_sekolah}")

        # Pre-process School Info to remove redundant kelurahan/kecamatan
        request.school_info = preprocess_school_info(request.school_info)

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

        # Custom Filename: SURAT_TUGAS_{NAME}_{dd-mm-yyyy}_{increment}.pdf
        first_assignee = request.assignees[0].nama if request.assignees else "UNKNOWN"
        first_assignee = re.sub(r'[^a-zA-Z0-9\s]', '', first_assignee).replace(" ", "_").upper()
        date_str = parse_indonesian_date(request.tanggal_surat)
        increment = get_next_increment("SURAT_TUGAS", first_assignee, date_str)
        custom_filename = f"SURAT_TUGAS_{first_assignee}_{date_str}_{increment}.pdf"

        file_path = pdf_service.generate(generic_request, custom_filename=custom_filename)
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)

        logger.info(f"Successfully generated Surat Tugas PDF: {filename} ({file_size} bytes)")

        return PDFResponse(
            filename=filename,
            file_url=f"/api/v1/letters/download/{filename}",
            file_size=file_size
        )
    except Exception as e:
        logger.error(f"Failed to generate Surat Tugas PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.post("/lembar-persetujuan", response_model=PDFResponse, summary="Generate Lembar Persetujuan PKL")
async def generate_lembar_persetujuan(request: LembarPersetujuanRequest):
    """
    Generate Lembar Persetujuan PKL (Internship Approval Letter) PDF.

    Creates a student approval document for PKL placement containing:
    - School information and letterhead
    - Student list (minimum 1 student)
    - Company/industry (DU/DI) information
    - Signature sections for school and company

    **Request Body:**
    - `school_info`: School information for letterhead
    - `students`: Array of students with at least `nama` field
    - `nama_perusahaan`: Company/industry name
    - `tempat_tanggal`: Place and date for signature (optional)

    **Response:**
    Returns filename, download URL, and file size in bytes.

    **Filename Format:** `LEMBAR_PERSETUJUAN_{COMPANY}_{dd-mm-yyyy}.pdf`
    """
    try:
        logger.info(f"Generating Lembar Persetujuan for {request.school_info.nama_sekolah}")

        request.school_info = preprocess_school_info(request.school_info)

        students_as_persons = [Person(nama=s.nama) for s in request.students]

        generic_request = LetterRequest(
            template_type="lembar_persetujuan",
            nomor_surat="PKL/PST/001",
            tanggal_surat=datetime.now().strftime("%d %B %Y"),
            perihal="LEMBAR PERSETUJUAN",
            school_info=request.school_info,
            penandatangan=students_as_persons[0],
            content={
                "students": request.students,
                "nama_perusahaan": request.nama_perusahaan,
                "tempat_tanggal": request.tempat_tanggal
            }
        )

        # Custom Filename: LEMBAR_PERSETUJUAN_{COMPANY}_{DATE}_{increment}.pdf
        company_name = re.sub(r'[^a-zA-Z0-9\s]', '', request.nama_perusahaan).replace(" ", "_").upper()
        date_str = datetime.now().strftime("%d-%m-%Y")
        increment = get_next_increment("LEMBAR_PERSETUJUAN", company_name, date_str)
        custom_filename = f"LEMBAR_PERSETUJUAN_{company_name}_{date_str}_{increment}.pdf"

        file_path = pdf_service.generate(generic_request, custom_filename=custom_filename)
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)

        logger.info(f"Successfully generated Lembar Persetujuan PDF: {filename} ({file_size} bytes)")

        return PDFResponse(
            filename=filename,
            file_url=f"/api/v1/letters/download/{filename}",
            file_size=file_size
        )
    except Exception as e:
        logger.error(f"Failed to generate Lembar Persetujuan PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.get("/download/{filename}", summary="Download generated PDF")
async def download_letter(filename: str):
    """
    Download a previously generated PDF file.

    Returns the PDF file as a downloadable attachment.
    Filenames are validated to prevent path traversal attacks.
    """
    logger.info(f"Downloading PDF: {filename}")

    # Basic path traversal protection
    if ".." in filename or "/" in filename:
        logger.warning(f"Invalid filename attempt: {filename}")
        raise HTTPException(status_code=400, detail="Invalid filename")

    file_path = f"output/{filename}"
    if not os.path.exists(file_path):
        logger.warning(f"File not found: {filename}")
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path, media_type="application/pdf", filename=filename)