"""Tests for letter API endpoints."""

import pytest
import os
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client(tmp_path):
    """Create test client with temporary output directory."""
    # Patch the output directory for testing
    import app.api.v1.endpoints.letters as letters_module
    original_service = letters_module.pdf_service

    from app.services.pdf_generator import PDFGenerator
    letters_module.pdf_service = PDFGenerator(output_dir=str(tmp_path))

    with TestClient(app) as test_client:
        yield test_client

    letters_module.pdf_service = original_service


@pytest.fixture
def sample_surat_tugas_payload():
    """Sample payload for surat tugas endpoint."""
    return {
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
            "kode_pos": "65153"
        },
        "penandatangan": {
            "nama": "SUMIJAH, S.Pd., M.Si.",
            "jabatan": "Kepala Sekolah",
            "nip": "19700210 199802 2 009"
        },
        "assignees": [
            {"nama": "Inasni Dyah Rahmatika, S.Pd.", "jabatan": "Guru"}
        ],
        "details": [
            {"label": "Keperluan", "value": "Test PKL"},
            {"label": "Hari/Tanggal", "value": "Senin, 1 Juli 2024"}
        ]
    }


@pytest.fixture
def sample_lembar_persetujuan_payload():
    """Sample payload for lembar persetujuan endpoint."""
    return {
        "school_info": {
            "nama_sekolah": "SMK NEGERI 2 SINGOSARI",
            "alamat_jalan": "Jalan Perusahaan No. 20",
            "kab_kota": "Kab. Malang",
            "provinsi": "Jawa Timur",
            "kode_pos": "65153"
        },
        "students": [
            {"nama": "CHANDA ZULIA LESTARI"},
            {"nama": "DIWA SASRI HALIA"}
        ],
        "nama_perusahaan": "JTV MALANG",
        "tempat_tanggal": "Malang, 12 Januari 2026"
    }


@pytest.fixture
def sample_penilaian_payload():
    """Sample payload for penilaian endpoint."""
    return {
        "school_info": {
            "nama_sekolah": "SMK NEGERI 2 SINGOSARI",
            "alamat_jalan": "Jalan Perusahaan No. 20",
            "kab_kota": "Kab. Malang",
            "provinsi": "Jawa Timur",
            "kode_pos": "65153"
        },
        "siswa": {
            "nama": "CHANDA ZULIA LESTARI",
            "nisn": "0012345678",
            "kelas": "XII DKV 1",
            "konsentrasi_keahlian": "Desain Komunikasi Visual",
            "tempat_pkl": "PT NAMA STUDIOS INDONESIA",
            "tanggal_mulai": "1 Juli 2024",
            "tanggal_selesai": "31 Desember 2024",
            "nama_instruktur": "Bapak / Ibu Pimpinan",
            "jabatan_instruktur": "Industrial Engineer",
            "nip_instruktur": "19850101 201001 2 005",
            "nama_pembimbing": "Aldian S.Pd.",
            "jabatan_pembimbing": "Guru Mapel PKL",
            "nip_pembimbing": "19850101 201001 2 006"
        },
        "nilai": {
            "skor_1": 90,
            "desc_1": "Sangat Baik",
            "skor_2": 85,
            "desc_2": "Baik",
            "skor_3": 88,
            "desc_3": "Baik",
            "skor_4": 92,
            "desc_4": "Sangat Baik"
        },
        "jenis_nomor": "NP",
        "sakit": 2,
        "izin": 1,
        "alpa": 0,
        "tempat_tanggal": "Singosari, 31 Desember 2024"
    }


@pytest.fixture
def sample_sertifikat_payload():
    """Sample payload for sertifikat endpoint."""
    return {
        "nomor_sertifikat": "420/1013/101.6.9.19/2026",
        "siswa": {
            "nama": "JULIANA SILVA",
            "nisn": "0123456789"
        },
        "nama_industri": "PT NAMA STUDIOS INDONESIA",
        "tanggal_mulai": "14 Juli 2026",
        "tanggal_selesai": "31 Desember 2026",
        "hasil_pkl": "Amat Baik",
        "tanggal_terbit": "31 Desember 2026",
        "nilai": {
            "aspek_1": 90,
            "desc_1": "MENERAPKAN SOFT SKILL YANG DIBUTUHKAN DI DUNIA KERJA (TEMPAT PKL).",
            "aspek_2": 85,
            "desc_2": "MENERAPKAN NORMA, PROSEDUR OPERASIONAL STANDAR (POS), SERTA KESEHATAN, KESELAMATAN KERJA, DAN LINGKUNGAN HIDUP (K3LH) YANG ADA DI DUNIA KERJA (TEMPAT PKL).",
            "aspek_3": 88,
            "desc_3": "MENERAPKAN KOMPETENSI TEKNIS YANG SUDAH DIPELAJARI DI SEKOLAH DAN/ATAU BARU DIPELAJARI DI DUNIA KERJA (TEMPAT PKL).",
            "aspek_4": 92,
            "desc_4": "MEMAHAMI ALUR BISNIS DUNIA KERJA TEMPAT PKL DAN WAWASAN WIRAUSAHA."
        },
        "nama_pimpinan": "Fatkur Amri",
        "jenis_nomor_pimpinan": "NP",
        "nip_pimpinan": "19850101 201001 2 005",
        "jabatan_pimpinan": "Direktur Utama PT UBIG",
        "nama_pembimbing": "Ahamd Fauzan",
        "jenis_nomor_pembimbing": "NIK",
        "nip_pembimbing": "19850101 201001 2 006",
        "jabatan_pembimbing": "Pembimbing"
    }


class TestHealthEndpoint:
    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "uptime_seconds" in data


class TestSuratTugasEndpoint:
    def test_surat_tugas_success(self, client, sample_surat_tugas_payload, tmp_path):
        response = client.post("/api/v1/letters/surat-tugas", json=sample_surat_tugas_payload)
        assert response.status_code == 200
        data = response.json()
        assert "filename" in data
        assert "file_url" in data
        assert "file_size" in data
        assert data["filename"].endswith(".pdf")

    def test_surat_tugas_creates_file(self, client, sample_surat_tugas_payload, tmp_path):
        response = client.post("/api/v1/letters/surat-tugas", json=sample_surat_tugas_payload)
        assert response.status_code == 200
        filename = response.json()["filename"]
        file_path = tmp_path / filename
        assert file_path.exists()

    def test_surat_tugas_missing_required_field(self, client):
        payload = {
            "nomor_surat": "800/123/SMK.2/2024",
            "school_info": {
                "nama_sekolah": "SMK Test",
                "alamat_jalan": "Jl. Test",
                "kab_kota": "Kab. Test",
                "provinsi": "Jawa Timur"
            },
            "penandatangan": {"nama": "Test"},
            "assignees": [{"nama": "Test"}],
            "details": []
        }
        response = client.post("/api/v1/letters/surat-tugas", json=payload)
        assert response.status_code == 422  # Validation error


class TestLembarPersetujuanEndpoint:
    def test_lembar_persetujuan_success(self, client, sample_lembar_persetujuan_payload):
        response = client.post("/api/v1/letters/lembar-persetujuan", json=sample_lembar_persetujuan_payload)
        assert response.status_code == 200
        data = response.json()
        assert "filename" in data
        assert "file_url" in data
        assert "file_size" in data

    def test_lembar_persetujuan_creates_file(self, client, sample_lembar_persetujuan_payload, tmp_path):
        response = client.post("/api/v1/letters/lembar-persetujuan", json=sample_lembar_persetujuan_payload)
        filename = response.json()["filename"]
        file_path = tmp_path / filename
        assert file_path.exists()

    def test_lembar_persetujuan_empty_students(self, client):
        payload = {
            "school_info": {
                "nama_sekolah": "SMK Test",
                "alamat_jalan": "Jl. Test",
                "kab_kota": "Kab. Test",
                "provinsi": "Jawa Timur"
            },
            "students": [],
            "nama_perusahaan": "PT Test"
        }
        response = client.post("/api/v1/letters/lembar-persetujuan", json=payload)
        assert response.status_code == 422


class TestPenilaianEndpoint:
    def test_penilaian_success(self, client, sample_penilaian_payload):
        response = client.post("/api/v1/letters/penilaian", json=sample_penilaian_payload)
        assert response.status_code == 200
        data = response.json()
        assert "filename" in data
        assert "file_url" in data
        assert "file_size" in data
        assert data["filename"].endswith(".pdf")


class TestSertifikatEndpoint:
    def test_sertifikat_success(self, client, sample_sertifikat_payload):
        response = client.post("/api/v1/letters/sertifikat/dkv", json=sample_sertifikat_payload)
        assert response.status_code == 200
        data = response.json()
        assert "filename" in data
        assert "file_url" in data
        assert "file_size" in data
        assert data["filename"].endswith(".pdf")


class TestDownloadEndpoint:
    def test_download_existing_file(self, client, sample_surat_tugas_payload, tmp_path):
        # First create a file
        response = client.post("/api/v1/letters/surat-tugas", json=sample_surat_tugas_payload)
        filename = response.json()["filename"]

        # Then download it
        download_response = client.get(f"/api/v1/letters/download/{filename}")
        assert download_response.status_code == 200
        assert download_response.headers["content-type"] == "application/pdf"

    def test_download_nonexistent_file(self, client):
        response = client.get("/api/v1/letters/download/nonexistent.pdf")
        assert response.status_code == 404

    def test_download_path_traversal_blocked(self, client):
        # The route doesn't match due to path characters, so FastAPI returns 404
        # This is still safe behavior - the file is not accessible
        response = client.get("/api/v1/letters/download/../test.pdf")
        assert response.status_code in (400, 404)

    def test_download_slash_blocked(self, client):
        response = client.get("/api/v1/letters/download/../../etc/passwd")
        assert response.status_code in (400, 404)
