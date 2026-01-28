import pytest
from pathlib import Path
from app.utils.filename import get_next_increment


def test_get_next_increment_no_files(tmp_path, monkeypatch):
    """Return 001 when no files exist."""
    monkeypatch.chdir(tmp_path)
    Path("output").mkdir()

    result = get_next_increment("LEMBAR_PERSETUJUAN", "JTV_MALANG", "28-01-2026")

    assert result == "001"


def test_get_next_increment_one_file(tmp_path, monkeypatch):
    """Return 002 when one file exists."""
    monkeypatch.chdir(tmp_path)
    output_dir = Path("output")
    output_dir.mkdir()
    (output_dir / "LEMBAR_PERSETUJUAN_JTV_MALANG_28-01-2026_001.pdf").touch()

    result = get_next_increment("LEMBAR_PERSETUJUAN", "JTV_MALANG", "28-01-2026")

    assert result == "002"


def test_get_next_increment_multiple_files(tmp_path, monkeypatch):
    """Return 004 when files 001, 002, 003 exist."""
    monkeypatch.chdir(tmp_path)
    output_dir = Path("output")
    output_dir.mkdir()
    (output_dir / "LEMBAR_PERSETUJUAN_JTV_MALANG_28-01-2026_001.pdf").touch()
    (output_dir / "LEMBAR_PERSETUJUAN_JTV_MALANG_28-01-2026_002.pdf").touch()
    (output_dir / "LEMBAR_PERSETUJUAN_JTV_MALANG_28-01-2026_003.pdf").touch()

    result = get_next_increment("LEMBAR_PERSETUJUAN", "JTV_MALANG", "28-01-2026")

    assert result == "004"


def test_get_next_increment_reset_daily(tmp_path, monkeypatch):
    """Increment resets for different dates."""
    monkeypatch.chdir(tmp_path)
    output_dir = Path("output")
    output_dir.mkdir()
    (output_dir / "LEMBAR_PERSETUJUAN_JTV_MALANG_28-01-2026_001.pdf").touch()

    result = get_next_increment("LEMBAR_PERSETUJUAN", "JTV_MALANG", "29-01-2026")

    assert result == "001"


def test_get_next_increment_different_identifier(tmp_path, monkeypatch):
    """Different identifiers have separate counters."""
    monkeypatch.chdir(tmp_path)
    output_dir = Path("output")
    output_dir.mkdir()
    (output_dir / "LEMBAR_PERSETUJUAN_JTV_MALANG_28-01-2026_001.pdf").touch()

    result = get_next_increment("LEMBAR_PERSETUJUAN", "BACAMALANG", "28-01-2026")

    assert result == "001"


def test_get_next_increment_different_prefix(tmp_path, monkeypatch):
    """Different prefixes have separate counters."""
    monkeypatch.chdir(tmp_path)
    output_dir = Path("output")
    output_dir.mkdir()
    (output_dir / "LEMBAR_PERSETUJUAN_JTV_MALANG_28-01-2026_001.pdf").touch()

    result = get_next_increment("SURAT_TUGAS", "JTV_MALANG", "28-01-2026")

    assert result == "001"


def test_get_next_increment_ignores_unrelated_files(tmp_path, monkeypatch):
    """Ignore files that don't match the pattern."""
    monkeypatch.chdir(tmp_path)
    output_dir = Path("output")
    output_dir.mkdir()
    (output_dir / "OTHER_FILE.pdf").touch()
    (output_dir / "LEMBAR_PERSETUJUAN_JTV_MALANG_28-01-2026_001.pdf").touch()
    (output_dir / "LEMBAR_PERSETUJUAN_DIFFERENT_28-01-2026_005.pdf").touch()

    result = get_next_increment("LEMBAR_PERSETUJUAN", "JTV_MALANG", "28-01-2026")

    assert result == "002"
