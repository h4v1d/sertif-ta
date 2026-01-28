# PDF Filename Increment Counter Design

## Problem

PDF filenames can collide when generating multiple files for the same company/assignee on the same date:
```
LEMBAR_PERSETUJUAN_JTV_MALANG_28-01-2026.pdf
LEMBAR_PERSETUJUAN_JTV_MALANG_28-01-2026.pdf  // Overwrites previous file
```

## Solution

Add daily increment counter that resets each day:
```
LEMBAR_PERSETUJUAN_JTV_MALANG_28-01-2026_001.pdf
LEMBAR_PERSETUJUAN_JTV_MALANG_28-01-2026_002.pdf
LEMBAR_PERSETUJUAN_JTV_MALANG_29-01-2026_001.pdf  // Reset
```

## Architecture

```
Endpoint Handler
    ↓
get_next_increment(prefix, identifier, date)
    ↓
Scan output/ for pattern: PREFIX_IDENTIFIER_DATE_###.pdf
    ↓
Return max increment + 1 (or "001" if none)
    ↓
Generate PDF with incremented filename
```

## Implementation

### 1. New Utility: `app/utils/filename.py`

```python
import re
from pathlib import Path

def get_next_increment(prefix: str, identifier: str, date_str: str) -> str:
    """Get next increment number as 3-digit string (001, 002, ...).

    Args:
        prefix: "LEMBAR_PERSETUJUAN" or "SURAT_TUGAS"
        identifier: sanitized company/assignee name
        date_str: "28-01-2026"

    Returns:
        Next increment as "001", "002", etc.
    """
    output_dir = Path("output")
    if not output_dir.exists():
        return "001"

    base_name = f"{prefix}_{identifier}_{date_str}"
    pattern = re.compile(rf"^{re.escape(base_name)}_(\d{{3}})\.pdf$")

    max_increment = 0
    for file in output_dir.glob("*.pdf"):
        match = pattern.match(file.name)
        if match:
            increment = int(match.group(1))
            max_increment = max(max_increment, increment)

    return f"{max_increment + 1:03d}"
```

### 2. Update `app/utils/__init__.py`

```python
from .filename import get_next_increment

__all__ = [..., "get_next_increment"]
```

### 3. Update `app/api/v1/endpoints/letters.py`

**Lembar Persetujuan:**
```python
company_name = re.sub(r'[^a-zA-Z0-9\s]', '', request.nama_perusahaan).replace(" ", "_").upper()
date_str = datetime.now().strftime("%d-%m-%Y")
increment = get_next_increment("LEMBAR_PERSETUJUAN", company_name, date_str)
custom_filename = f"LEMBAR_PERSETUJUAN_{company_name}_{date_str}_{increment}.pdf"
```

**Surat Tugas:**
```python
first_assignee = re.sub(r'[^a-zA-Z0-9\s]', '', request.assignees[0].nama).replace(" ", "_").upper()
date_str = parse_indonesian_date(request.tanggal_surat)
increment = get_next_increment("SURAT_TUGAS", first_assignee, date_str)
custom_filename = f"SURAT_TUGAS_{first_assignee}_{date_str}_{increment}.pdf"
```

## Test Cases

- `test_get_next_increment_no_files`: Returns "001" when directory empty
- `test_get_next_increment_one_file`: Returns "002" after "001" exists
- `test_get_next_increment_reset_daily`: Resets to "001" for new date
- `test_get_next_increment_different_identifier`: Separate counters per identifier

## Filename Format Examples

| Type | Identifier | Date | Increment | Final Filename |
|------|-----------|------|-----------|----------------|
| Lembar Persetujuan | JTV_MALANG | 28-01-2026 | 001 | LEMBAR_PERSETUJUAN_JTV_MALANG_28-01-2026_001.pdf |
| Lembar Persetujuan | JTV_MALANG | 28-01-2026 | 002 | LEMBAR_PERSETUJUAN_JTV_MALANG_28-01-2026_002.pdf |
| Surat Tugas | INASNI_DYAH_RAHMATIKA | 28-01-2026 | 001 | SURAT_TUGAS_INASNI_DYAH_RAHMATIKA_28-01-2026_001.pdf |
