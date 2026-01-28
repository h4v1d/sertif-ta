import re
from pathlib import Path


def get_next_increment(prefix: str, identifier: str, date_str: str) -> str:
    """
    Get next increment number as 3-digit string (001, 002, ...).

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
