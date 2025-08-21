class BitFlag8:
    def __init__(self, value: int = 0) -> None:
        self.value = value

    def less(self, flag: int) -> bool:
        return self.value < flag

    def set_flag(self, flag: int) -> 'BitFlag8':
        self.value |= flag
        return self

    def clear_flag(self, flag: int) -> 'BitFlag8':
        self.value &= ~flag
        return self

    def is_set(self, flag: int) -> bool:
        return (self.value & flag) == flag
