import re
from datetime import date, datetime, timedelta
from typing import Tuple
from dateutil.relativedelta import relativedelta
from sslib.util.number_util import NumberUtil

_DEFAULT_DATE_FORMAT_ = '%Y-%m-%d'

# 날짜 찾는 정규식 미리 컴파일
_DATE_EXTRACTOR_ = re.compile(r'(\d{4})[\s년/.-]*(\d{1,2})[\s월/.-]*(\d{1,2})[\s일]*')


class DatetimeUtil:
    @staticmethod
    def format_date(src: str) -> datetime | None:
        '''문자열 날짜를 datetime으로 변경'''
        if not src:
            return None
        match = _DATE_EXTRACTOR_.search(src)
        if not match:
            return None
        try:
            # 정수 변환 후 datetime 객체 생성하면 자동으로 제로 패딩 적용
            year, month, day = map(int, match.groups())
            dt = datetime(year=year, month=month, day=day)
        except ValueError:
            return None
        return dt

    @staticmethod
    def format_date_str(src: str | None, date_format: str = _DEFAULT_DATE_FORMAT_, excludes: list[str] | None = None) -> str | None:
        '''문자열 날짜를 형식화된(기본:YYYY-MM-DD) 문자열로 변경'''
        if not src:
            return src
        if excludes and src in excludes:
            return src
        dt = DatetimeUtil.format_date(src=src)
        if dt:
            return dt.strftime(date_format)
        return None

    @staticmethod
    def to_date(src: str, date_format: str = _DEFAULT_DATE_FORMAT_) -> date:
        '''문자열 날짜(기본:YYYY-MM-DD)를 date 객체로 응답'''
        return datetime.strptime(src, date_format).date()

    @staticmethod
    def find_nums_to_date_or_none(src: str | None) -> date | None:
        if not src:
            return None
        nums = re.findall(r'\d+', src)
        if len(nums) != 3:
            return None
        year, month, day = map(int, nums)
        return date(year=year, month=month, day=day)

    @staticmethod
    def to_date_or_none(src: str | None, date_format: str = _DEFAULT_DATE_FORMAT_) -> date | None:
        return DatetimeUtil.to_date(src, date_format=date_format) if src else None

    @staticmethod
    def after_date(src: str, after: str) -> str | None:
        if isinstance(src, str):
            dt = DatetimeUtil.format_date(src=src)
            if dt is None:
                return None
            if after.endswith('년'):
                after_dt = dt + relativedelta(years=NumberUtil.to_int(after) or 0)
                return after_dt.strftime(_DEFAULT_DATE_FORMAT_)
        return None

    @staticmethod
    def day_range(src: str, format: str = _DEFAULT_DATE_FORMAT_) -> Tuple[datetime, datetime]:
        '''src: YYYY-MM-DD 포맷의 날짜 문자열로 오늘~내일(00:00:00) 반환'''
        s = datetime.strptime(src, format)
        e = s + timedelta(days=1)
        return s, e


if __name__ == '__main__':
    TEST_DATE = '2025.07.10'
    print(DatetimeUtil.format_date_str(src=TEST_DATE, date_format='%Y/%m/%d'))

# NOTE - 명령어 > python -m sslib.util.datetime_util
