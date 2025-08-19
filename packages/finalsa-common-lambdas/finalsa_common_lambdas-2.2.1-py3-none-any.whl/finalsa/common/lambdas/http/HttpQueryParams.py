from typing import Any, Dict, Optional


class HttpQueryParams:

    def __init__(self, args: Dict[str, str]) -> None:
        self.args = args

    def get(self, key: str, default: Optional[Any] = None) -> Optional[Any]:
        return self.args.get(key, default)
