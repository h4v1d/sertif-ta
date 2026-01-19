"""Tests for utility modules."""

import pytest
from app.utils.date_parser import parse_indonesian_date
from app.utils.school_info import preprocess_school_info
from app.schemas.letter import SchoolInfo


class TestDateParser:
    def test_parse_indonesian_date_valid(self):
        assert parse_indonesian_date("1 Juli 2024") == "01-07-2024"
        assert parse_indonesian_date("12 Januari 2025") == "12-01-2025"
        assert parse_indonesian_date("31 Desember 2026") == "31-12-2026"

    def test_parse_indonesian_date_case_insensitive(self):
        assert parse_indonesian_date("1 juli 2024") == "01-07-2024"
        assert parse_indonesian_date("1 JANUARI 2024") == "01-01-2024"

    def test_parse_indonesian_date_with_padding(self):
        assert parse_indonesian_date("01 Juli 2024") == "01-07-2024"

    def test_parse_indonesian_date_invalid_month(self):
        # Invalid month returns "00" for month part
        result = parse_indonesian_date("1 InvalidMonth 2024")
        assert result == "01-00-2024"

    def test_parse_indonesian_date_malformed(self):
        assert parse_indonesian_date("invalid") == "invalid"

    def test_all_months(self):
        test_cases = [
            ("1 Januari 2024", "01-01-2024"),
            ("1 Februari 2024", "01-02-2024"),
            ("1 Maret 2024", "01-03-2024"),
            ("1 April 2024", "01-04-2024"),
            ("1 Mei 2024", "01-05-2024"),
            ("1 Juni 2024", "01-06-2024"),
            ("1 Juli 2024", "01-07-2024"),
            ("1 Agustus 2024", "01-08-2024"),
            ("1 September 2024", "01-09-2024"),
            ("1 Oktober 2024", "01-10-2024"),
            ("1 November 2024", "01-11-2024"),
            ("1 Desember 2024", "01-12-2024"),
        ]
        for input_date, expected in test_cases:
            assert parse_indonesian_date(input_date) == expected


class TestSchoolInfoPreprocessing:
    def test_preprocess_remove_duplicate_kelurahan(self):
        school = SchoolInfo(
            nama_sekolah="SMK Test",
            alamat_jalan="Jl. Test, Tunjungtirto",
            kelurahan="Tunjungtirto",
            kecamatan="Singosari",
            kab_kota="Kab. Malang",
            provinsi="Jawa Timur"
        )
        result = preprocess_school_info(school)
        assert result.kelurahan is None
        assert result.kecamatan == "Singosari"

    def test_preprocess_remove_duplicate_kecamatan(self):
        school = SchoolInfo(
            nama_sekolah="SMK Test",
            alamat_jalan="Jl. Test, Singosari",
            kelurahan="Tunjungtirto",
            kecamatan="Singosari",
            kab_kota="Kab. Malang",
            provinsi="Jawa Timur"
        )
        result = preprocess_school_info(school)
        assert result.kecamatan is None
        assert result.kelurahan == "Tunjungtirto"

    def test_preprocess_remove_both_duplicates(self):
        school = SchoolInfo(
            nama_sekolah="SMK Test",
            alamat_jalan="Jl. Tunjungtirto, Singosari",
            kelurahan="Tunjungtirto",
            kecamatan="Singosari",
            kab_kota="Kab. Malang",
            provinsi="Jawa Timur"
        )
        result = preprocess_school_info(school)
        assert result.kelurahan is None
        assert result.kecamatan is None

    def test_preprocess_no_duplicates(self):
        school = SchoolInfo(
            nama_sekolah="SMK Test",
            alamat_jalan="Jl. Test No. 1",
            kelurahan="Tunjungtirto",
            kecamatan="Singosari",
            kab_kota="Kab. Malang",
            provinsi="Jawa Timur"
        )
        result = preprocess_school_info(school)
        assert result.kelurahan == "Tunjungtirto"
        assert result.kecamatan == "Singosari"

    def test_preprocess_none_values(self):
        school = SchoolInfo(
            nama_sekolah="SMK Test",
            alamat_jalan="Jl. Test No. 1",
            kelurahan=None,
            kecamatan=None,
            kab_kota="Kab. Malang",
            provinsi="Jawa Timur"
        )
        result = preprocess_school_info(school)
        assert result.kelurahan is None
        assert result.kecamatan is None
