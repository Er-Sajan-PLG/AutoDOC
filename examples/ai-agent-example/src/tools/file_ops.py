"""Read a known prompt file within the example root. Never accept arbitrary paths."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]


def read_prompt(name: str) -> str:
    """Read a prompt by simple filename from the designated prompt directory."""
    if not name.endswith('.md') or Path(name).name != name:
        raise ValueError('simple .md filename required')
    path = (ROOT / 'src/prompts' / name).resolve()
    if not path.is_relative_to((ROOT / 'src/prompts').resolve()):
        raise ValueError('prompt outside allowlist')
    return path.read_text(encoding='utf-8')
