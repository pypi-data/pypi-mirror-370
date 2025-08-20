class Instrument:
    string_count: int

    @classmethod
    def min_chord_width(cls) -> int:
        return (cls.string_count * 2) - 1 + 5
