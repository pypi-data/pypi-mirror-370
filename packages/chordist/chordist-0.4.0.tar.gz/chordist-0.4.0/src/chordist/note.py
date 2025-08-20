class Note:
    # pylint: disable=redefined-builtin
    def __init__(self, name: str, c_distance: int, ascii: str = "", alt_names: list[str] | None = None):
        self.name = name
        self.c_distance = c_distance
        self.ascii = ascii or name
        self.alt_names = alt_names or []

    def __eq__(self, value: object) -> bool:
        if isinstance(value, str):
            name = value
        elif isinstance(value, Note):
            name = value.name
        else:
            return False
        return name in [self.name, self.ascii, *self.alt_names]

    def __hash__(self) -> int:
        return hash((self.name, self.c_distance))

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    def transpose(self, steps: int):
        note_pos = TONES[self.c_distance].index(self)
        new_tone = TONES[(self.c_distance + steps) % len(TONES)]

        return new_tone[note_pos] if len(new_tone) > note_pos else new_tone[0]


class Notes:
    class NotFound(Exception):
        ...

    C = Note("C", 0)
    C_SHARP = Note("C♯", 1, "C#", ["D♭", "Db"])
    D_FLAT = Note("D♭", 1, "Db", ["C♯", "C#"])
    D = Note("D", 2)
    D_SHARP = Note("D♯", 3, "D#", ["E♭", "Eb"])
    E_FLAT = Note("E♭", 3, "Eb", ["D♯", "D#"])
    E = Note("E", 4)
    F = Note("F", 5)
    F_SHARP = Note("F♯", 6, "F#", ["G♭", "Gb"])
    G_FLAT = Note("G♭", 6, "Gb", ["F♯", "F#"])
    G = Note("G", 7)
    G_SHARP = Note("G♯", 8, "G#", ["A♭", "Ab"])
    A_FLAT = Note("A♭", 8, "Ab", ["G♯", "G#"])
    A = Note("A", 9)
    A_SHARP = Note("A♯", 10, "A#", ["B♭", "Bb"])
    B_FLAT = Note("B♭", 10, "Bb", ["A♯", "A#"])
    B = Note("B", 11, alt_names=["H"])

    @classmethod
    def get(cls, name: str) -> Note:
        for value in cls.__dict__.values():
            if isinstance(value, Note) and value == name:
                return value
        raise Notes.NotFound(f"Note {name} not found")


TONES = [
    [Notes.C],
    [Notes.C_SHARP, Notes.D_FLAT],
    [Notes.D],
    [Notes.D_SHARP, Notes.E_FLAT],
    [Notes.E],
    [Notes.F],
    [Notes.F_SHARP, Notes.G_FLAT],
    [Notes.G],
    [Notes.G_SHARP, Notes.A_FLAT],
    [Notes.A],
    [Notes.A_SHARP, Notes.B_FLAT],
    [Notes.B],
]
