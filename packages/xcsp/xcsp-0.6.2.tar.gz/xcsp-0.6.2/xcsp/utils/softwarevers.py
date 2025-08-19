from typing import List

from packaging.version import Version


def normalize(v):
    return v.replace("#", ".")


def sort_versions(versions: List[str]) -> List[str]:
    return sorted(versions, key=lambda v: Version(normalize(v)))

