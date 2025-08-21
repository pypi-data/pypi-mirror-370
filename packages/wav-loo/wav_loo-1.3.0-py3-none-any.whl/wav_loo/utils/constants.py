from typing import Dict, List

ZONE_NAMES_4: List[str] = [
    "zhujia",
    "fujia",
    "zhujiahoupai",
    "fujiahoupai",
]

TWO_ZONE_MAPPING: Dict[str, List[str]] = {
    "zone_a": ["zhujia", "zhujiahoupai"],
    "zone_b": ["fujia", "fujiahoupai"],
} 