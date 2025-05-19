import os

from src.constants import REF_DOCS_DIR


def get_latest_version() -> str:
    def version_to_tuple(v: str) -> tuple:
        return tuple(map(int, v.lstrip("v").split(".")))

    file_list = os.listdir(f"{REF_DOCS_DIR}/pennylane/raw")
    versions = [f.replace(".json", "") for f in file_list if f.endswith(".json")]
    latest_version = max(versions, key=version_to_tuple)

    return latest_version
