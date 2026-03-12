from typing import List, Optional, Dict, Any, Union, Annotated
from pydantic import BaseModel, Field

class SchoolInfo(BaseModel):
    nama_sekolah: str = Field(..., description="Nama lengkap sekolah", examples=["SMK NEGERI 2 SINGOSARI"])
    alamat_jalan: str = Field(..., description="Alamat jalan sekolah", examples=["Jalan Perusahaan No. 20"])
    kelurahan: str | None = Field(None, description="Kelurahan/Desa", examples=["Tunjungtirto"])
    kecamatan: str | None = Field(None, description="Kecamatan", examples=["Singosari"])
    kab_kota: str | None = Field(None, description="Kabupaten/Kota", examples=["Kab. Malang"])
    provinsi: str | None= Field(None, description="Provinsi", examples=["Jawa Timur"])
    kode_pos: str | None = Field(None, description="Kode pos", examples=["65153"])
    telepon: str | None = Field(None, description="Nomor telepon", examples=["(0341) 4345127"])
    email: str | None = Field(None, description="Alamat email", examples=["smkn2singosari@yahoo.co.id"])
    website: str | None = Field(None, description="Website sekolah", examples=["www.smkn2singosari.sch.id"])
    logo_url: str | None = Field(None, description="URL logo sekolah", examples=["https://upload.wikimedia.org/wikipedia/commons/7/74/Coat_of_arms_of_East_Java.svg"])

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "nama_sekolah": "SMK NEGERI 2 SINGOSARI",
                    "alamat_jalan": "Jalan Perusahaan No. 20",
                    "kelurahan": "Tunjungtirto",
                    "kecamatan": "Singosari",
                    "kab_kota": "Kab. Malang",
                    "provinsi": "Jawa Timur",
                    "kode_pos": "65153",
                    "telepon": "(0341) 4345127",
                    "email": "smkn2singosari@yahoo.co.id",
                    "website": "www.smkn2singosari.sch.id",
                    "logo_url": "https://upload.wikimedia.org/wikipedia/commons/7/74/Coat_of_arms_of_East_Java.svg"
                }
            ]
        }
    }

class Person(BaseModel):
    nama: str = Field(..., description="Nama lengkap", examples=["SUMIJAH, S.Pd., M.Si."])
    jabatan: str | None = Field(None, description="Jabatan/posisi", examples=["Kepala SMK Negeri 2 Singosari"])
    nip: str | None = Field(None, description="Nomor Induk Pegawai", examples=["19700210 199802 2 009"])
    pangkat: str | None = Field(None, description="Pangkat/golongan", examples=["Pembina Tk. I"])
    instansi: str | None = Field(None, description="Instansi/lembaga", examples=["SMK Negeri 2 Singosari"])

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "nama": "SUMIJAH, S.Pd., M.Si.",
                    "jabatan": "Kepala SMK Negeri 2 Singosari",
                    "nip": "19700210 199802 2 009",
                    "pangkat": "Pembina Tk. I",
                    "instansi": "SMK Negeri 2 Singosari"
                },
                {
                    "nama": "Inasni Dyah Rahmatika, S.Pd.",
                    "jabatan": "Guru",
                    "nip": "19850101 201001 2 005",
                    "instansi": "SMK Negeri 2 Singosari"
                },
                {
                    "nama": "Budi Santoso, S.Kom.",
                    "jabatan": "Guru Kejuruan",
                    "instansi": "SMK Negeri 2 Singosari"
                }
            ]
        }
    }

class KeyValueItem(BaseModel):
    label: str = Field(..., description="Label/key", examples=["Keperluan"])
    value: str = Field(..., description="Nilai/value", examples=["Pengantaran Siswa Praktik Kerja Lapangan (PKL)"])
    separator: str = Field(":", description="Pemisah antara label dan value", examples=[":"])

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"label": "Keperluan", "value": "Pengantaran Siswa Praktik Kerja Lapangan (PKL)", "separator": ":"},
                {"label": "Hari / Tanggal", "value": "Senin, 1 Juli 2024", "separator": ":"},
                {"label": "Waktu", "value": "08.00 - Selesai", "separator": ":"},
                {"label": "Tempat", "value": "Institut Teknologi Nasional - Kampus 2", "separator": ":"},
                {"label": "Alamat", "value": "JL. Raya Karanglo No.KM. 2, Tasikmadu, Kec. Lowokwaru, Kota Malang, Jawa Timur 65153", "separator": ":"}
            ]
        }
    }


class Student(BaseModel):
    nama: str = Field(..., description="Nama lengkap siswa", examples=["CHANDA ZULIA LESTARI"])

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"nama": "CHANDA ZULIA LESTARI"},
                {"nama": "DIWA SASRI HALIA"}
            ]
        }
    }

# --- Specific Request Models ---

class SuratTugasRequest(BaseModel):
    nomor_surat: str = Field(..., description="Nomor surat", examples=["800/123/SMK.2/2024"])
    tanggal_surat: str = Field(..., description="Tanggal surat dalam format Indonesia", examples=["1 Juli 2024"])
    tempat_surat: str | None = Field(None, description="Tempat penerbitan surat", examples=["Singosari"])
    perihal: str = Field("SURAT TUGAS", description="Perihal/subjek surat", examples=["SURAT TUGAS"])

    school_info: SchoolInfo = Field(..., description="Informasi sekolah untuk kop surat")
    penandatangan: Person = Field(..., description="Pejabat penandatangan surat")

    assignees: List[Person] = Field(..., description="Daftar orang yang ditugaskan", min_length=1)
    details: List[KeyValueItem] = Field(..., description="Detail tugas dalam format key-value")

    pembuka: str | None = Field(None, description="Kalimat pembuka surat", examples=["Kepala SMK Negeri 2 Singosari Dinas Pendidikan Kabupaten Malang menugaskan kepada :"])
    penutup: str | None = Field(None, description="Kalimat penutup surat", examples=["Demikian surat tugas ini dibuat untuk dilaksanakan dengan sebaik-baiknya dan melaporkan hasilnya kepada kepala sekolah."])

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "nomor_surat": "800/123/SMK.2/2024",
                    "tanggal_surat": "1 Juli 2024",
                    "tempat_surat": "Singosari",
                    "perihal": "SURAT TUGAS",
                    "school_info": {
                        "nama_sekolah": "SMK NEGERI 2 SINGOSARI",
                        "alamat_jalan": "Jalan Perusahaan No. 20",
                        "kelurahan": "Tunjungtirto",
                        "kecamatan": "Singosari",
                        "kab_kota": "Kab. Malang",
                        "provinsi": "Jawa Timur",
                        "kode_pos": "65153",
                        "telepon": "(0341) 4345127",
                        "email": "smkn2singosari@yahoo.co.id",
                        "website": "www.smkn2singosari.sch.id",
                        "logo_url": "https://upload.wikimedia.org/wikipedia/commons/7/74/Coat_of_arms_of_East_Java.svg"
                    },
                    "penandatangan": {
                        "nama": "SUMIJAH, S.Pd., M.Si.",
                        "jabatan": "Kepala SMK Negeri 2 Singosari",
                        "nip": "19700210 199802 2 009",
                        "pangkat": "Pembina Tk. I",
                        "instansi": "SMK Negeri 2 Singosari"
                    },
                    "assignees": [
                        {
                            "nama": "Inasni Dyah Rahmatika, S.Pd.",
                            "jabatan": "Guru",
                            "nip": "19850101 201001 2 005",
                            "instansi": "SMK Negeri 2 Singosari"
                        },
                        {
                            "nama": "Budi Santoso, S.Kom.",
                            "jabatan": "Guru Kejuruan",
                            "instansi": "SMK Negeri 2 Singosari"
                        }
                    ],
                    "details": [
                        {"label": "Keperluan", "value": "Pengantaran Siswa Praktik Kerja Lapangan (PKL)", "separator": ":"},
                        {"label": "Hari / Tanggal", "value": "Senin, 1 Juli 2024", "separator": ":"},
                        {"label": "Waktu", "value": "08.00 - Selesai", "separator": ":"},
                        {"label": "Tempat", "value": "Institut Teknologi Nasional - Kampus 2", "separator": ":"},
                        {"label": "Alamat", "value": "JL. Raya Karanglo No.KM. 2, Tasikmadu, Kec. Lowokwaru, Kota Malang, Jawa Timur 65153", "separator": ":"}
                    ],
                    "pembuka": "Kepala SMK Negeri 2 Singosari Dinas Pendidikan Kabupaten Malang menugaskan kepada :",
                    "penutup": "Demikian surat tugas ini dibuat untuk dilaksanakan dengan sebaik-baiknya dan melaporkan hasilnya kepada kepala sekolah."
                }
            ]
        }
    }

class LembarPersetujuanRequest(BaseModel):
    school_info: SchoolInfo = Field(..., description="Informasi sekolah untuk kop surat")

    students: Annotated[List[Student], Field(min_length=1, description="Daftar siswa PKL")]

    nama_perusahaan: str = Field(..., description="Nama perusahaan/DU/DI tempat PKL", examples=["JTV MALANG"])

    tempat_tanggal: str | None = Field(None, description="Tempat dan tanggal surat", examples=["Malang, 12 Januari 2026"])

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "school_info": {
                        "nama_sekolah": "SMK NEGERI 2 SINGOSARI",
                        "alamat_jalan": "Jalan Perusahaan No. 20",
                        "kab_kota": "Kab. Malang",
                        "provinsi": "Jawa Timur",
                        "kode_pos": "65153",
                        "telepon": "(0341) 458823",
                        "logo_url": "https://upload.wikimedia.org/wikipedia/commons/7/74/Coat_of_arms_of_East_Java.svg"
                    },
                    "students": [
                        {"nama": "CHANDA ZULIA LESTARI"},
                        {"nama": "DIWA SASRI HALIA"}
                    ],
                    "nama_perusahaan": "JTV MALANG",
                    "tempat_tanggal": "Malang, 12 Januari 2026"
                }
            ]
        }
    }


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
    filename: str = Field(..., description="Nama file PDF yang dihasilkan", examples=["SURAT_TUGAS_INASNI_DYAH_RAHMATIKA_01-07-2024.pdf"])
    file_url: str = Field(..., description="URL untuk mengunduh file PDF", examples=["/api/v1/letters/download/SURAT_TUGAS_INASNI_DYAH_RAHMATIKA_01-07-2024.pdf"])
    file_size: int = Field(..., description="Ukuran file dalam bytes", examples=[45678])

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "filename": "SURAT_TUGAS_INASNI_DYAH_RAHMATIKA_01-07-2024.pdf",
                    "file_url": "/api/v1/letters/download/SURAT_TUGAS_INASNI_DYAH_RAHMATIKA_01-07-2024.pdf",
                    "file_size": 45678
                },
                {
                    "filename": "LEMBAR_PERSETUJUAN_JTV_MALANG_12-01-2026.pdf",
                    "file_url": "/api/v1/letters/download/LEMBAR_PERSETUJUAN_JTV_MALANG_12-01-2026.pdf",
                    "file_size": 32456
                }
            ]
        }
    }

class SiswaSertifikat(BaseModel):
    nama: str = Field(..., description="Nama lengkap siswa", examples=["Juliana Silva"])
    nisn: str = Field(..., description="Nomor Induk Siswa Nasional (NISN)", examples=["0123456789"])

class NilaiSertifikat(BaseModel):
    aspek_1: float = Field(..., description="Nilai Aspek 1", examples=[90.0])
    desc_1: str = Field("MENERAPKAN SOFT SKILL YANG DIBUTUHKAN DI DUNIA KERJA (TEMPAT PKL).", description="Deskripsi Aspek 1")
    aspek_2: float = Field(..., description="Nilai Aspek 2", examples=[85.0])
    desc_2: str = Field("MENERAPKAN NORMA, PROSEDUR OPERASIONAL STANDAR (POS), SERTA KESEHATAN, KESELAMATAN KERJA, DAN LINGKUNGAN HIDUP (K3LH) YANG ADA DI DUNIA KERJA (TEMPAT PKL).", description="Deskripsi Aspek 2")
    aspek_3: float = Field(..., description="Nilai Aspek 3", examples=[88.0])
    desc_3: str = Field("MENERAPKAN KOMPETENSI TEKNIS YANG SUDAH DIPELAJARI DI SEKOLAH DAN/ATAU BARU DIPELAJARI DI DUNIA KERJA (TEMPAT PKL).", description="Deskripsi Aspek 3")
    aspek_4: float = Field(..., description="Nilai Aspek 4", examples=[92.0])
    desc_4: str = Field("MEMAHAMI ALUR BISNIS DUNIA KERJA TEMPAT PKL DAN WAWASAN WIRAUSAHA.", description="Deskripsi Aspek 4")

class SertifikatRequest(BaseModel):
    nomor_sertifikat: str = Field(..., description="Nomor surat/sertifikat", examples=["420/1013/101.6.9.19/2026"])
    siswa: SiswaSertifikat = Field(..., description="Data Siswa")
    nama_industri: str = Field(..., description="Nama perusahaan/DU/DI tempat PKL", examples=["PT NAMA STUDIOS INDONESIA"])
    tanggal_mulai: str = Field(..., description="Tanggal mulai PKL (e.g., '14 Juli 2026')", examples=["14 Juli 2026"])
    tanggal_selesai: str = Field(..., description="Tanggal selesai PKL (e.g., '31 Desember 2026')", examples=["31 Desember 2026"])
    hasil_pkl: str = Field(..., description="Hasil evaluasi ('Amat Baik' / 'Baik' / 'Kurang')", examples=["Amat Baik"])
    tanggal_terbit: str = Field(..., description="Tanggal sertifikat diterbitkan (e.g., '31 Desember 2026')", examples=["31 Desember 2026"])
    nilai: NilaiSertifikat = Field(..., description="Data nilai untuk halaman belakang")
    nama_pimpinan: str = Field(..., description="Nama pimpinan perusahaan", examples=["Fatkur Amri"])
    nip_pimpinan: str = Field(..., description="NIP pimpinan perusahaan", examples=["19850101 201001 2 005"])
    jabatan_pimpinan: str = Field(..., description="Jabatan pimpinan perusahaan", examples=["Direktur Utama PT UBIG"])
    nama_pembimbing: str = Field(..., description="Nama pembimbing perusahaan", examples=["Ahamd Fauzan"])
    nip_pembimbing: str = Field(..., description="NIP pembimbing perusahaan", examples=["19850101 201001 2 005"])
    jabatan_pembimbing: str = Field(..., description="Jabatan pembimbing perusahaan", examples=["Pembimbing"])

class StudentPenilaian(BaseModel):
    nama: str = Field(..., description="Nama lengkap siswa", examples=["CHANDA ZULIA LESTARI"])
    nisn: str = Field(..., description="NISN siswa", examples=["0012345678"])
    kelas: str = Field(..., description="Kelas siswa", examples=["XII DKV 1"])
    konsentrasi_keahlian: str = Field(..., description="Konsentrasi Keahlian", examples=["Desain Komunikasi Visual"])
    tempat_pkl: str = Field(..., description="Tempat PKL", examples=["PT NAMA STUDIOS INDONESIA"])
    tanggal_mulai: str = Field(..., description="Tanggal Mulai PKL", examples=["1 Juli 2024"])
    tanggal_selesai: str = Field(..., description="Tanggal Selesai PKL", examples=["31 Desember 2024"])
    nama_instruktur: str = Field(..., description="Nama Instruktur Dunia Kerja", examples=["Bapak / Ibu Pimpinan"])
    jabatan_instruktur: str = Field(..., description="Jabatan Instruktur Dunia Kerja", examples=["Industrial Engineer"])
    nip_instruktur: str = Field(..., description="NIP Instruktur Dunia Kerja", examples=["19850101 201001 2 005"])
    nama_pembimbing: str = Field(..., description="Nama Guru Pembimbing", examples=["Aldian S.Pd."])
    jabatan_pembimbing: str = Field(..., description="Jabatan Guru Pembimbing", examples=["Guru Mapel PKL"])
    nip_pembimbing: str = Field(..., description="NIP Guru Pembimbing", examples=["19850101 201001 2 005"])

class NilaiPenilaianDetail(BaseModel):
    skor_1: float = Field(..., description="Skor untuk Aspek 1", examples=[90.0])
    desc_1: str = Field("Sangat Baik", description="Deskripsi kualitatif Aspek 1", examples=["Sangat Baik"])
    skor_2: float = Field(..., description="Skor untuk Aspek 2", examples=[85.0])
    desc_2: str = Field("Baik", description="Deskripsi kualitatif Aspek 2", examples=["Baik"])
    skor_3: float = Field(..., description="Skor untuk Aspek 3", examples=[88.0])
    desc_3: str = Field("Baik", description="Deskripsi kualitatif Aspek 3", examples=["Baik"])
    skor_4: float = Field(..., description="Skor untuk Aspek 4", examples=[92.0])
    desc_4: str = Field("Sangat Baik", description="Deskripsi kualitatif Aspek 4", examples=["Sangat Baik"])

class PenilaianRequest(BaseModel):
    school_info: SchoolInfo = Field(..., description="Informasi sekolah untuk header")
    siswa: StudentPenilaian = Field(..., description="Data identitas siswa yang dinilai")
    nilai: NilaiPenilaianDetail = Field(..., description="Detail perolehan skor dan deskripsi siswa")
    sakit: int = Field(0, description="Jumlah hari sakit", examples=[2])
    izin: int = Field(0, description="Jumlah hari izin", examples=[1])
    alpa: int = Field(0, description="Jumlah hari tanpa keterangan (alpa)", examples=[0])
    tempat_tanggal: str = Field("Singosari, ...........................................", description="Tempat dan tanggal tanda tangan instruktur", examples=["Singosari, 31 Desember 2024"])
