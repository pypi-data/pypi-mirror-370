import json
from typing import Any, Optional
from sslib.util.string_util import StringUtil


class JsonUtil:
    @staticmethod
    def dumps(src: Any) -> str:
        return json.dumps(obj=JsonUtil.to_json(src), ensure_ascii=False)

    @staticmethod
    def to_json(src: Any) -> Any:
        if src is None:
            return None
        if isinstance(src, list):
            return [JsonUtil.__to_json(item) for item in src]
        return JsonUtil.__to_json(src)

    @staticmethod
    def to_snake(src: str) -> Any:
        json_data = json.loads(src)
        return JsonUtil.__keys_to_snake(obj=json_data)

    @staticmethod
    def from_json(src: Optional[str], fallback: str = '[]') -> Any:
        try:
            return json.loads(src or fallback)
        except (TypeError, json.JSONDecodeError):
            return json.loads(fallback)

    @staticmethod
    def print_json(src: Any, indent: int | None = 2):
        print(json.dumps(JsonUtil.to_json(src), indent=indent, ensure_ascii=False))

    @staticmethod
    def __to_json(src: Any):
        from sslib.base.entity import Entity

        return src.to_dict() if isinstance(src, Entity) else src

    @staticmethod
    def __keys_to_snake(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {StringUtil.camel_to_snake(k): JsonUtil.__keys_to_snake(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [JsonUtil.__keys_to_snake(x) for x in obj]
        return obj
