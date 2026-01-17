from typing import List, Optional, Dict, Any, Union, Annotated
from pydantic import BaseModel, Field

class SchoolInfo(BaseModel):
    """Information for the letterhead (Kop Surat)."""
    nama_sekolah: str
    alamat_jalan: str
    kelurahan: str | None = None
    kecamatan: str | None = None
    kab_kota: str
    provinsi: str
    kode_pos: str | None = None
    telepon: str | None = None
    email: str | None = None
    website: str | None = None
    logo_url: str | None = None

    model_config = {"json_schema_extra": {"examples": [{"nama_sekolah": "SMK NEGERI 2 SINGOSARI", "alamat_jalan": "Jalan Perusahaan No. 20", "kab_kota": "Kab. Malang", "provinsi": "Jawa Timur"}]}}

class Person(BaseModel):
    """Generic person model for assignees and signatories."""
    nama: str
    jabatan: str | None = None
    nip: str | None = None
    pangkat: str | None = None
    instansi: str | None = None

class KeyValueItem(BaseModel):
    """Helper for displaying key-value pairs (e.g. 'Waktu' : '08.00')."""
    label: str
    value: str
    separator: str = ":"

# --- Specific Request Models ---

class SuratTugasRequest(BaseModel):
    """Strictly typed request for Surat Tugas generation."""
    nomor_surat: str
    tanggal_surat: str
    tempat_surat: str | None = None
    perihal: str = "SURAT TUGAS"

    school_info: SchoolInfo
    penandatangan: Person

    # Content specific to Surat Tugas
    assignees: List[Person]
    details: List[KeyValueItem]

    pembuka: str | None = None
    penutup: str | None = None

    model_config = {"json_schema_extra": {"examples": [{"nomor_surat": "800/123/SMK.2/2024", "tanggal_surat": "1 Juli 2024", "tempat_surat": "Singosari"}]}}

class LembarPersetujuanRequest(BaseModel):
    """Request schema for Lembar Persetujuan PKL."""
    school_info: SchoolInfo

    # Siswa details
    students: Annotated[List[Person], Field(min_length=1)]

    # DU/DI Info
    nama_perusahaan: str

    # Signature placeholder
    tempat_tanggal: str | None = None

    model_config = {"json_schema_extra": {"examples": [{"nama_perusahaan": "JTV MALANG", "tempat_tanggal": "Malang, 12 Januari 2026"}]}}


# --- Generic/Legacy Request Models ---

class LetterRequest(BaseModel):
    """Top level request to generate a letter (Generic)."""
    template_type: str = Field(..., description="Template name (e.g. surat_tugas)")
    nomor_surat: str
    perihal: str = "SURAT TUGAS"
    tanggal_surat: str
    tempat_surat: str | None = None

    school_info: SchoolInfo
    penandatangan: Person

    # Flexible content
    content: Dict[str, Any]

class PDFResponse(BaseModel):
    filename: str
    file_url: str
    file_size: int
    
