from typing import Any


class DictUtil:
    @staticmethod
    def get(key: str, source: dict, fallback: Any = None) -> Any:
        return source[key] if source[key] is not None else fallback

    @staticmethod
    def clean(source: dict) -> dict:
        ret = {}
        for k, v in source.items():
            if v is not None:
                ret[k] = v
        return ret
