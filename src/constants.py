from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.absolute()
REF_DOCS_DIR = PROJECT_ROOT / "refdocs"

RAW_PENNYLANE_JSON_DIR = REF_DOCS_DIR / "pennylane" / "raw"
FORMATTED_PENNYLANE_JSON_DIR = REF_DOCS_DIR / "pennylane" / "formatted"


SUPPORTED_PENNYLANE_VERSIONS = [
    "v0.35.0",
    "v0.35.1",
    "v0.36.0",
    "v0.37.0",
    "v0.38.0",
    "v0.38.1",
    "v0.39.0",
    "v0.40.0",
    "v0.41.0",
    "v0.41.1",
]
