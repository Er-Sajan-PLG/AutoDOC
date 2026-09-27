"""Read only an allowlisted local data file; resolve symlinks before access."""
from pathlib import Path


def read(data_root: Path, filename: str):
    if not isinstance(filename, str) or not filename or Path(filename).name != filename:
        raise ValueError('files.read needs one simple filename')
    target = (data_root / filename).resolve()
    if not target.is_relative_to(data_root.resolve()) or not target.is_file():
        raise ValueError('files.read path is outside the allowed data directory or missing')
    if target.stat().st_size > 8192:
        raise ValueError('files.read exceeds 8192 bytes')
    return target.read_text(encoding='utf-8')
