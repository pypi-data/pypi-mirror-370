import json
from typing import Any, Dict
from warnings import deprecated
from dataclasses import dataclass, field
from dataclasses_json import DataClassJsonMixin, LetterCase, config
from marshmallow import fields

# NOTE - 삭제예정
from sslib.base.dict import DictEx


TDatetimeField = field(metadata=config(mm_field=fields.DateTime(format='%Y-%m-%d %H:%M:%S')))


class MyJsonMixin(DataClassJsonMixin):
    dataclass_json_config = config(letter_case=LetterCase.CAMEL)["dataclasses_json"]

    @staticmethod
    def _remove_empty_lists(obj: Any) -> Any:
        """
        dict 내에서 빈 리스트를 가진 키를 모두 제거하고,
        리스트 안의 객체도 재귀적으로 정리합니다.
        """
        if isinstance(obj, dict):
            cleaned: Dict[str, Any] = {}
            for k, v in obj.items():
                v2 = JsonEntity._remove_empty_lists(v)
                # 빈 리스트면 스킵
                if isinstance(v2, list) and len(v2) == 0:
                    continue
                cleaned[k] = v2
            return cleaned

        if isinstance(obj, list):
            return [JsonEntity._remove_empty_lists(item) for item in obj]

        return obj

    def to_json(self, *, ensure_ascii=False, **kwargs):
        return super().to_json(ensure_ascii=ensure_ascii, **kwargs)

    @classmethod
    def dumps(cls, objs, *, ensure_ascii=False, **kw):
        many = isinstance(objs, (list, tuple))
        raw = cls.schema(many=many).dump(objs)
        objs = cls._remove_empty_lists(obj=raw)
        return json.dumps(objs, ensure_ascii=ensure_ascii, **kw)


@dataclass
class JsonEntity(MyJsonMixin):
    pass


@dataclass
class JsonWithIdEntity(MyJsonMixin):
    id: int = field(default=0)


@deprecated('CamelEntity 사용')
class Entity(DictEx):
    pass


@deprecated('JsonWithIdEntity 사용')
@dataclass
class EntityWithId(Entity):
    id: int = field(default=0)
