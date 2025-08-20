class Modifier:
    # pylint: disable=redefined-builtin
    def __init__(self, name: str, ascii: str = "", alt_names: list[str] | None = None):
        self.name = name
        self.ascii = ascii or name
        self.alt_names = alt_names or []

    def __eq__(self, value: object) -> bool:
        if isinstance(value, str):
            name = value
        elif isinstance(value, Modifier):
            name = value.name
        else:
            return False
        return name in [self.name, self.ascii, *self.alt_names]

    def __hash__(self) -> int:
        return hash(self.name)

    def __repr__(self):
        names = set([self.name, self.ascii, *self.alt_names])
        return f"Modifier({names})"


class Modifiers:
    class NotFound(Exception):
        ...

    AUG = Modifier("+", alt_names=["aug"])
    DIM7 = Modifier("dim⁷", "dim7")
    MAJ7 = Modifier("maj⁷", "maj7")
    MINOR = Modifier("m")
    MINOR7 = Modifier("m⁷", "m7")
    SEVEN = Modifier("⁷", "7")
    SUS2 = Modifier("sus2")
    SUS4 = Modifier("sus4")

    @classmethod
    def get(cls, name: str) -> Modifier:
        for value in cls.__dict__.values():
            if isinstance(value, Modifier) and value == name:
                return value
        raise Modifiers.NotFound(f"Modifier {name} not found")
