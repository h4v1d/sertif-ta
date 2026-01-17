"""Helper functions for processing school information."""

from app.schemas.letter import SchoolInfo


def preprocess_school_info(school: SchoolInfo) -> SchoolInfo:
    """
    Preprocess school info to remove redundant kelurahan/kecamatan
    if they appear in alamat_jalan.

    This fixes duplication issues like "Tunjungtirto, Tunjungtirto"
    in the address display.
    """
    addr = school.alamat_jalan

    # Clear kelurahan if it's already in the address
    if school.kelurahan and school.kelurahan in addr:
        school.kelurahan = None

    # Clear kecamatan if it's already in the address
    if school.kecamatan and school.kecamatan in addr:
        school.kecamatan = None

    return school
