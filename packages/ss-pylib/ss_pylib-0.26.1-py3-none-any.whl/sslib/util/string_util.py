import re
from datetime import datetime
from stringcase import camelcase


class StringUtil:
    @staticmethod
    def to_int(src: str) -> int:
        try:
            return int(src)
        except ValueError:
            return 0

    @staticmethod
    def to_bool(source: str) -> bool:
        return source.lower() in ('true', '1', 'yes', 'y')

    @staticmethod
    def camel_case(source: str) -> str:
        return camelcase(source)

    @staticmethod
    def datetime_or_none(source: datetime) -> str | None:
        return source.strftime('%Y-%m-%d %H:%M:%S') if source is not None else None

    @staticmethod
    def camel_to_snake(name: str) -> str:
        s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


if __name__ == '__main__':
    KEY = '123456789012345678901234'
    print(KEY)
