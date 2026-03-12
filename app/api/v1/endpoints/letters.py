import os
import re
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.schemas.letter import LetterRequest, SuratTugasRequest, LembarPersetujuanRequest, PDFResponse, Person, SertifikatRequest, PenilaianRequest
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

@router.post("/sertifikat/{jurusan}", response_model=PDFResponse, summary="Generate Sertifikat PKL")
async def generate_sertifikat(jurusan: str, request: SertifikatRequest):
    """
    Generate Sertifikat PKL (Internship Certificate) PDF document.

    Creates a 2-page certificate:
    - Page 1: Front side with student info, industry, and PKL result
    - Page 2: Back side with detailed scores

    **Request Body:**
    - `nomor_sertifikat`: Certificate number
    - `siswa`: Student details (nama, nisn)
    - `nama_industri`: Industry name
    - `tanggal_mulai`: Start date of PKL
    - `tanggal_selesai`: End date of PKL
    - `hasil_pkl`: High-level result (e.g. Amat Baik)
    - `tanggal_terbit`: Date of issue
    - `nilai`: 4 specific score aspects
    - `nama_pimpinan`: Name of the industry leader
    - `nip_pimpinan`: NIP of the industry leader
    - `jabatan_pimpinan`: Job title of the industry leader
    - `nama_pembimbing`: Name of the school teacher
    - `nip_pembimbing`: NIP of the school teacher
    - `jabatan_pembimbing`: Job title of the school teacher
    """
    try:
        logger.info(f"Generating Sertifikat PKL ({jurusan}) for {request.siswa.nama}")

        allowed_jurusan = ["dkv", "av", "bc", "mt", "rpl", "tkj", "an",'ei']
        if jurusan.lower() not in allowed_jurusan:
            raise HTTPException(status_code=400, detail=f"Jurusan {jurusan} is not supported. Supported: {allowed_jurusan}")

        total = sum([
            request.nilai.aspek_1,
            request.nilai.aspek_2,
            request.nilai.aspek_3,
            request.nilai.aspek_4
        ])
        rata_rata = round(total / 4, 2)

        content = {
            "nomor_sertifikat": request.nomor_sertifikat,
            "siswa": {
                "nama": request.siswa.nama,
                "nisn": request.siswa.nisn
            },
            "nama_industri": request.nama_industri,
            "tanggal_mulai": request.tanggal_mulai,
            "tanggal_selesai": request.tanggal_selesai,
            "hasil_pkl": request.hasil_pkl,
            "tanggal_terbit": request.tanggal_terbit,
            "nilai": {
                "aspek_1": request.nilai.aspek_1,
                "desc_1": request.nilai.desc_1,
                "aspek_2": request.nilai.aspek_2,
                "desc_2": request.nilai.desc_2,
                "aspek_3": request.nilai.aspek_3,
                "desc_3": request.nilai.desc_3,
                "aspek_4": request.nilai.aspek_4,
                "desc_4": request.nilai.desc_4
            },
            "nama_pimpinan": request.nama_pimpinan,
            "nip_pimpinan": request.nip_pimpinan,
            "jabatan_pimpinan": request.jabatan_pimpinan,
            "nama_pembimbing": request.nama_pembimbing,
            "nip_pembimbing": request.nip_pembimbing,
            "jabatan_pembimbing": request.jabatan_pembimbing,
            "total_nilai": total,
            "rata_rata": rata_rata
        }

        mock_school = {
            "nama_sekolah": "SMK",
            "alamat_jalan": "-"
        }
        mock_person = {
            "nama": "Placeholder"
        }
        
        generic_request = LetterRequest(
            template_type=f"sertif/{jurusan}/kombinasi",
            nomor_surat=request.nomor_sertifikat,
            tanggal_surat=request.tanggal_terbit,
            school_info=mock_school,
            penandatangan=mock_person,
            content=content
        )

        student_name = re.sub(r'[^a-zA-Z0-9\s]', '', request.siswa.nama).replace(" ", "_").upper()
        date_str = datetime.now().strftime("%d-%m-%Y")
        prefix = f"SERTIFIKAT_{jurusan.upper()}"
        increment = get_next_increment(prefix, student_name, date_str)
        custom_filename = f"{prefix}_{student_name}_{date_str}_{increment}.pdf"

        file_path = pdf_service.generate(generic_request, custom_filename=custom_filename)
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)

        logger.info(f"Successfully generated Sertifikat PDF: {filename} ({file_size} bytes)")

        return PDFResponse(
            filename=filename,
            file_url=f"/api/v1/letters/download/{filename}",
            file_size=file_size
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate Sertifikat PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.post("/penilaian", response_model=PDFResponse, summary="Generate Form Penilaian PKL")
async def generate_penilaian(request: PenilaianRequest):
    """
    Generate Form Penilaian PKL PDF.
    
    Creates a 2-page assessment document:
    - Page 1: Student details, scores for 4 learning objectives
    - Page 2: Attendance records and signature sections
    """
    try:
        logger.info(f"Generating Form Penilaian for {request.siswa.nama}")

        request.school_info = preprocess_school_info(request.school_info)

        # Calculate totals
        total_skor = sum([
            request.nilai.skor_1,
            request.nilai.skor_2,
            request.nilai.skor_3,
            request.nilai.skor_4
        ])
        rata_rata = round(total_skor / 4, 2)

        content = {
            "siswa": {
                "nama": request.siswa.nama,
                "nisn": request.siswa.nisn,
                "kelas": request.siswa.kelas,
                "konsentrasi_keahlian": request.siswa.konsentrasi_keahlian,
                "tempat_pkl": request.siswa.tempat_pkl,
                "tanggal_mulai": request.siswa.tanggal_mulai,
                "tanggal_selesai": request.siswa.tanggal_selesai,
                "nama_instruktur": request.siswa.nama_instruktur,
                "jabatan_instruktur": request.siswa.jabatan_instruktur,
                "nip_instruktur": request.siswa.nip_instruktur,
                "nama_pembimbing": request.siswa.nama_pembimbing,
                "jabatan_pembimbing": request.siswa.jabatan_pembimbing,
                "nip_pembimbing": request.siswa.nip_pembimbing
            },
            "nilai": {
                "skor_1": request.nilai.skor_1,
                "desc_1": request.nilai.desc_1,
                "skor_2": request.nilai.skor_2,
                "desc_2": request.nilai.desc_2,
                "skor_3": request.nilai.skor_3,
                "desc_3": request.nilai.desc_3,
                "skor_4": request.nilai.skor_4,
                "desc_4": request.nilai.desc_4
            },
            "total_skor": total_skor,
            "rata_rata": rata_rata,
            "sakit": request.sakit,
            "izin": request.izin,
            "alpa": request.alpa,
            "tempat_tanggal": request.tempat_tanggal
        }

        mock_person = {"nama": "Placeholder"}

        generic_request = LetterRequest(
            template_type="penilaian",
            nomor_surat="-",
            tanggal_surat=datetime.now().strftime("%d %B %Y"),
            perihal="FORM PENILAIAN PKL",
            school_info=request.school_info,
            penandatangan=mock_person,
            content=content
        )

        student_name = re.sub(r'[^a-zA-Z0-9\s]', '', request.siswa.nama).replace(" ", "_").upper()
        konsentrasi = re.sub(r'[^a-zA-Z0-9\s]', '', request.siswa.konsentrasi_keahlian).replace(" ", "_").upper()
        date_str = datetime.now().strftime("%d-%m-%Y")
        prefix = f"PENILAIAN_{konsentrasi}"
        increment = get_next_increment(prefix, student_name, date_str)
        custom_filename = f"{prefix}_{student_name}_{date_str}_{increment}.pdf"

        file_path = pdf_service.generate(generic_request, custom_filename=custom_filename)
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)

        logger.info(f"Successfully generated Penilaian PDF: {filename} ({file_size} bytes)")

        return PDFResponse(
            filename=filename,
            file_url=f"/api/v1/letters/download/{filename}",
            file_size=file_size
        )
    except Exception as e:
        logger.error(f"Failed to generate Penilaian PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")