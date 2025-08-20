from chordist.abstract_chord import AbstractChord
from chordist.modifier import Modifier, Modifiers
from chordist.note import Note, Notes


class Chord(AbstractChord):
    base: Note
    modifier: Modifier | None

    class NotFound(Exception):
        ...

    def __init__(self, base: Note, modifier: Modifier | None = None):
        self.base = base
        self.modifier = modifier
        self.name = base.name + (modifier.name if modifier else "")
        self.ascii = base.ascii + (modifier.ascii if modifier else "")

    def __hash__(self) -> int:
        return hash((self.base, self.modifier))

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    @classmethod
    def get(cls, name: str) -> "Chord":
        for idx in range(len(name), 0, -1):
            try:
                base = Notes.get(name[:idx])
                if idx < len(name):
                    modifier = Modifiers.get(name[idx:])
                else:
                    modifier = None
                return Chord(base, modifier)
            except (Notes.NotFound, Modifiers.NotFound):
                pass
        raise Chord.NotFound(f"Unknown chord: {name}")

    @classmethod
    def get_or_null(cls, name: str) -> "Chord | None":
        try:
            return cls.get(name)
        except Exception:
            return None

    def transpose(self, steps: int) -> "Chord":
        return Chord(base=self.base.transpose(steps), modifier=self.modifier)
