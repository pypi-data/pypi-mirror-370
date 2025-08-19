from re import match
from typing import Any, Dict, List, Optional, Tuple


def match_key(regex_dict: Dict[str, Any], path: str) -> Tuple[Optional[str], Tuple[str, ...]]:
    for key, value in regex_dict.items():
        match_result = match(key, path)
        if match_result and match_result.group(0) == path:
            return value, match_result.groups()
    return None, ()


def get_fixed_path(splited_path: List[str]) -> str:
    result = "/"
    for part in splited_path:
        result += f"{part}/"
    return result


def get_regex_path(splited_path: List[str], args: List[str]) -> str:
    regex = "/"
    for part in splited_path:
        if part in args:
            regex += f"(?P<{part}>[^/]+)/"
            continue
        regex += f"{part}/"
    return regex
