from enum import Enum
from datetime import datetime
from typing import Any
from sslib.util.string_util import StringUtil


class DictEx:
    def to_dict(self, include_none: bool = False, camel_case: bool = True) -> dict:
        output = {}
        for k, v in self.__dict__.items():
            if not include_none and v is None:
                continue
            if camel_case:
                k = StringUtil.camel_case(k)
            output[k] = self._convert(src=v)
        return output

    def _convert(self, src: Any) -> Any:
        if isinstance(src, datetime):
            return StringUtil.datetime_or_none(src)
        if isinstance(src, Enum):
            return src.value

        from sslib.base import Entity

        if isinstance(src, list) is True or isinstance(src, Entity) is True:
            from sslib.util import JsonUtil

            # return JsonUtil.from_json(src=JsonUtil.to_json(src=src))
            return JsonUtil.to_json(src=src)
        return src
