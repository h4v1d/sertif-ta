# Changelog

## 2026-01-28 - PDF Filename Increment Counter

### Feature
- **Filename Increment**: Added daily increment counter to PDF filenames to prevent collision
  - Format: `{PREFIX}_{IDENTIFIER}_{DATE}_{INCREMENT}.pdf`
  - Examples:
    - `LEMBAR_PERSETUJUAN_JTV_MALANG_28-01-2026_001.pdf`
    - `LEMBAR_PERSETUJUAN_JTV_MALANG_28-01-2026_002.pdf`
    - `SURAT_TUGAS_INASNI_DYAH_RAHMATIKA_28-01-2026_001.pdf`
  - Counter resets daily (separate counters per prefix + identifier + date)

### Files Created
- `app/utils/filename.py`: `get_next_increment()` function
- `tests/utils/test_filename.py`: 7 test cases (all passing)
- `docs/plans/2026-01-28-pdf-filename-increment-design.md`: Design document

### Files Modified
- `app/utils/__init__.py`: Export `get_next_increment`
- `app/api/v1/endpoints/letters.py`: Integrate increment into both endpoints

---

## 2025-01-19 - Codebase Improvements

### Security & Configuration
- **.gitignore**: Added `/output` directory to prevent generated PDFs from being tracked
- **CORS**: Changed from hardcoded `["*"]` to environment-based configuration via `CORS_ORIGINS` env var
  - Default: `*` (all origins)
  - Production: Set comma-separated origins (e.g., `https://example.com,https://api.example.com`)

### Testing
Added comprehensive test suite (45 tests, all passing):

- **`tests/schemas/test_letter.py`**: Pydantic model validation tests
  - SchoolInfo, Person, KeyValueItem, Student
  - SuratTugasRequest, LembarPersetujuanRequest

- **`tests/utils/test_utils.py`**: Utility function tests
  - Date parser (Indonesian month names)
  - School info preprocessing (duplicate removal)

- **`tests/services/test_pdf_generator.py`**: PDF generation service tests
  - File creation, custom filenames, error handling

- **`tests/api/v1/test_letters.py`**: API endpoint integration tests
  - Surat Tugas, Lembar Persetujuan, download endpoint
  - Path traversal protection verification

### Files Modified
- `.gitignore`
- `app/main.py`

### Files Created
- `tests/schemas/test_letter.py`
- `tests/utils/test_utils.py`
- `tests/services/test_pdf_generator.py`
- `tests/api/v1/test_letters.py`
- `.claude/CHANGELOG.md`
