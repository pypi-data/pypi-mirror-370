import re


class NumberUtil:
    _NO_NUM_PATTERN_ = re.compile(r'-')
    _BILLION_PATTERN_ = re.compile(r'(\d+)\s*억')
    _DIGIT_PATTERN_ = re.compile(r'\d+')
    _KOREAN_MONEY_PATTERN_ = re.compile(r'(\d+)([억천백십만])?')
    _PERCENT_PATTERN_ = re.compile(r'\d+%')
    _AREA_PATTERN_ = re.compile(r'\d+\.?\d*(?=㎡)')
    _CLEAN_TARGET_PATTERN_ = re.compile(r'^.*?-')

    # 상수 정의
    MAN_UNIT = 10000
    BILLION_UNIT = 100_000_000
    HUNDRED_MILLION_UNIT = 100_000_000
    TEN_MILLION_UNIT = 10_000_000

    @staticmethod
    def is_number(src: str | None) -> bool:
        if not src:
            return False
        return bool(not NumberUtil._NO_NUM_PATTERN_.search(src))

    @staticmethod
    def to_int(src: str | None, fallback: int | None = 0) -> int | None:
        '''문자열에서 정수 변환'''
        if not src:
            return fallback

        # 성능 최적화: 정규식으로 한 번에 처리
        target = NumberUtil._CLEAN_TARGET_PATTERN_.sub('', src).strip()

        # 한국어 금액 처리 - 로직 중복 제거
        if any(keyword in target for keyword in ['천', '백', '십', '만', '억']):
            return NumberUtil.parse_korean_money(target, fallback)

        # 기존 로직
        unit = NumberUtil.MAN_UNIT if target.endswith('만') else 1
        unit = 1000000 if target.endswith('백만') or target.endswith('백만원') else unit
        unit = NumberUtil.TEN_MILLION_UNIT if target.endswith('천만') else unit

        m = NumberUtil._BILLION_PATTERN_.search(target)
        if m:
            unit = NumberUtil.BILLION_UNIT

        find = NumberUtil._DIGIT_PATTERN_.findall(target)
        return int(''.join(find)) * unit if find and len(find) > 0 else fallback

    @staticmethod
    def parse_korean_money(target: str, fallback: int | None = None) -> int | None:
        '''한국어 금액을 숫자로 변환'''
        try:
            # "원" 제거
            target = target.replace('원', '')

            result = 0
            current_num = 0

            # 정규식으로 숫자와 단위 분리
            matches = NumberUtil._KOREAN_MONEY_PATTERN_.findall(target)

            for num_str, unit in matches:
                num = int(num_str)
                if unit:
                    if unit == '만':
                        result += current_num * NumberUtil.MAN_UNIT
                        current_num = num
                    elif unit == '억':
                        result += current_num * NumberUtil.BILLION_UNIT
                        current_num = num
                    elif unit == '천':
                        current_num += num * 1000
                    elif unit == '백':
                        current_num += num * 100
                    elif unit == '십':
                        current_num += num * 10
                else:
                    current_num = num

            # 마지막 숫자 처리 - 만 단위가 있으면 곱하기
            if current_num > 0:
                if '만' in target:
                    result += current_num * NumberUtil.MAN_UNIT
                else:
                    result += current_num

            return result
        except (ValueError, TypeError, AttributeError):
            return fallback

    @staticmethod
    def find_price(src: str | None, fallback: int | None = None) -> int | None:
        '''문자열에서 돈 찾기'''
        if not src:
            return fallback
        target = src.split('-')[-1].strip().split('원')[0]
        return NumberUtil.to_int(src=target, fallback=fallback)

    @staticmethod
    def find_percent(src: str, fallback: int = 0) -> int:
        '''문자열에 퍼센트 찾기'''
        find = NumberUtil._PERCENT_PATTERN_.search(src)
        return int(find.group().replace('%', '')) if find is not None else fallback

    @staticmethod
    def find_area(src: str | None, ndigits: int | None = None, fallback: float | None = None) -> float | None:
        '''문자열에서 면적 찾기'''
        if not src:
            return fallback
        find = NumberUtil._AREA_PATTERN_.findall(src)
        ret = sum(map(lambda x: float(re.sub(r'[^0-9.]', '', x).strip().replace(')', '')), find)) if find else fallback
        return round(ret, ndigits=ndigits) if ret else ret


if __name__ == '__main__':
    TEST = '5천만원'
    print(NumberUtil.find_price(src=TEST))
