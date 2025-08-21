try:
    from bliss import current_session
except ImportError:
    current_session = None

from pathlib import Path

from ..processor import Scan
from ..utils.directories import get_filename


def export_filename_prefix(scan: Scan, lima_name: str) -> str:
    scan_filename = Path(get_filename(scan))
    scan_nb = scan.scan_info.get("scan_nb")
    return f"{scan_filename.stem}_{scan_nb:04d}_{lima_name}"


def get_current_filename() -> str:
    if current_session is None:
        raise ImportError("Bliss cannot be imported")

    return current_session.scan_saving.filename
