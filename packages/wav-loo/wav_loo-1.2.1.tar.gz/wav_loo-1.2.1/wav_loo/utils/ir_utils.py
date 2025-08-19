import re
from pathlib import Path
from typing import Dict, List, Optional


def match_zone_from_name(name_lower: str, zone_names: List[str]) -> Optional[str]:
    matches: List[str] = []
    for zone in zone_names:
        pattern = rf"(^|[^a-z]){re.escape(zone)}([^a-z]|$)"
        if re.search(pattern, name_lower):
            matches.append(zone)
    if not matches:
        return None
    matches.sort(key=len, reverse=True)
    return matches[0]


def index_ir_by_zone(root: Path, zone_names: List[str]) -> Dict[str, List[Path]]:
    zone_to_files: Dict[str, List[Path]] = {z: [] for z in zone_names}
    if not root.exists():
        return zone_to_files
    for sub in root.rglob("*"):
        if not sub.is_dir():
            continue
        name_lower = sub.name.lower()
        matched_zone = match_zone_from_name(name_lower, zone_names)
        if matched_zone is None:
            continue
        files = [p for p in sub.rglob("*.wav") if p.is_file()]
        if files:
            zone_to_files[matched_zone].extend(files)
    for z in zone_to_files:
        unique = sorted({p.resolve() for p in zone_to_files[z]})
        zone_to_files[z] = [Path(p) for p in unique]
    return zone_to_files 