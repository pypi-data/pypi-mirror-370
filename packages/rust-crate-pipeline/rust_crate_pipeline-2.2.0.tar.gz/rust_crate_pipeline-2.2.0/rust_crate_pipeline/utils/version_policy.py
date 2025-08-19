from __future__ import annotations

import re
from typing import Dict, List, Tuple


def _parse_semver(version: str) -> Tuple[int, int, int]:
    m = re.match(r"^(\d+)\.(\d+)\.(\d+)", version)
    if not m:
        return (0, 0, 0)
    return (int(m.group(1)), int(m.group(2)), int(m.group(3)))


def select_minor_lines(versions: List[str], max_minor_per_major: int = 3) -> List[str]:
    """
    Pick the last N minor lines per major, preserving latest patch within each minor.
    """
    if not versions:
        return []

    # Group by (major, minor) keeping highest patch
    latest_by_minor: Dict[Tuple[int, int], str] = {}
    for v in versions:
        maj, min_, pat = _parse_semver(v)
        key = (maj, min_)
        if key not in latest_by_minor:
            latest_by_minor[key] = v
        else:
            _, _, cur_pat = _parse_semver(latest_by_minor[key])
            if pat >= cur_pat:
                latest_by_minor[key] = v

    # Order minors by (major, minor) descending, limit per major
    by_major: Dict[int, List[Tuple[int, str]]] = {}
    for (maj, min_), v in latest_by_minor.items():
        by_major.setdefault(maj, []).append((min_, v))

    selected: List[str] = []
    for _, entries in by_major.items():
        entries.sort(key=lambda x: x[0], reverse=True)
        for _, v in entries[:max_minor_per_major]:
            selected.append(v)

    # Sort overall by semver descending for stability
    selected.sort(key=lambda x: _parse_semver(x), reverse=True)
    return selected
