import functools
import operator
from abc import ABC
from typing import Generator, Iterable, Self

from chordist.abstract_chord import AbstractChord
from chordist.chord import Chord
from chordist.constants import MAXLEN, XPAD, YPAD
from chordist.instrument import Instrument
from chordist.utils import split_before


class Finger:
    fret: int
    string: int
    finger: str

    def __init__(self, fret: int, string: int, finger: int | str | None = None):
        self.fret = fret
        self.string = string
        self.finger = str(finger) if finger is not None else "*"

    def __eq__(self, value: object) -> bool:
        if isinstance(value, Finger):
            return value.fret == self.fret and value.string == self.string
        if isinstance(value, (tuple, list)) and len(value) >= 2:
            return value[0] == self.fret and value[1] == self.string
        return False

    def __hash__(self) -> int:
        return hash((self.fret, self.string, self.finger))

    def __repr__(self):
        return f"Finger(fret={self.fret}, string={self.string}, finger={self.finger})"


class InstrumentChord(AbstractChord, ABC):
    instrument: type[Instrument]
    chord: Chord
    fingers: tuple[Finger, ...]
    finger_map: dict[tuple[int, int], Finger]
    start_fret: int
    end_fret: int

    def __init__(self, chord: Chord, *fingers: Finger):
        self.chord = chord
        self.base = chord.base
        self.modifier = chord.modifier
        self.fingers = fingers
        self.finger_map = {(f.fret, f.string): f for f in fingers}
        highest_fret = max((f.fret for f in fingers), default=1)
        lowest_fret = min((f.fret for f in fingers), default=1)
        if highest_fret > 4:
            self.start_fret = lowest_fret
        else:
            self.start_fret = 1
        self.end_fret = max(self.start_fret + 3, highest_fret)

    def __eq__(self, value: object) -> bool:
        if isinstance(value, InstrumentChord):
            return (
                value.instrument == self.instrument and
                value.chord == self.chord and
                set(value.fingers) == set(self.fingers)
            )
        return super().__eq__(value)

    def __hash__(self) -> int:
        return hash((self.instrument, self.chord, self.fingers))

    def __repr__(self):
        return f"{self.__class__.__name__}(chord={self.chord.__repr__()})"

    def __str__(self):
        return self.chord.__str__()

    @property
    def height(self):
        return self.end_fret - self.start_fret + 1

    @property
    def min_width(self):
        return self.instrument.min_chord_width()

    @property
    def width(self):
        width = (self.instrument.string_count * 2) - 1
        if self.start_fret > 1:
            width += len(f" {self.start_fret}fr")

        return width

    @classmethod
    def create(cls, name: str, *fingers: tuple[int, int, int | str] | tuple[int, int]):
        return cls(
            Chord.get(name),
            *(Finger(f[0], f[1], f[2] if len(f) > 2 else "*") for f in fingers),
        )

    def generate_fret(self, fret: int) -> str:
        fret_str = ""

        for string in range(1, self.instrument.string_count + 1):
            if (fret, string) in self.finger_map:
                fret_str += self.finger_map[(fret, string)].finger + " "
            else:
                fret_str += "| "

        fret_str = fret_str.strip()
        if fret == self.start_fret and fret > 1:
            fret_str += f" {fret}fr"

        return fret_str

    def generate_head(self, only_ascii: bool = False) -> str:
        name = self.chord.ascii if only_ascii else self.chord.name
        width = (self.instrument.string_count * 2) - 1
        fill = "_" if self.start_fret == 1 else " "
        head = fill * max(int((width / 2) - (len(name) / 2)), 0)
        head += name
        head += fill * max(width - len(head), 0)
        return head

    def get_row(self, idx: int, pad: int = 0, min_width: int | None = None, only_ascii: bool = False) -> str:
        width = max(min_width, self.width) if min_width else self.width
        if idx == 0:
            row = self.generate_head(only_ascii=only_ascii)
        else:
            row = self.generate_fret(idx + self.start_fret - 1)
        return f"{row:{width + pad}s}"

    def get_width(self, pad: int = 0, min_width: int | None = None) -> int:
        width = self.width + pad
        if min_width and min_width > width:
            return min_width
        return width

    def print(self):
        for idx in range(self.height + 1):
            print(self.get_row(idx))


class InstrumentChordCollection:
    chords: list[InstrumentChord]

    @property
    def min_chord_width(self) -> int | None:
        return max((c.min_width for c in self.chords), default=None)

    def __init__(self, *chords: InstrumentChord):
        self.chords = []
        for chord in chords:
            if chord not in self.chords:
                self.chords.append(chord)

    def __add__(self, other: "InstrumentChordCollection"):
        chords = sorted([*self.chords, *other.chords])
        return InstrumentChordCollection(*chords)

    def __iter__(self):
        return iter(self.chords)

    def __repr__(self):
        return repr(self.chords)

    def add(self, chord: InstrumentChord) -> Self:
        if chord not in self.chords:
            self.chords.append(chord)
        return self

    def filter(self, name: str) -> "InstrumentChordCollection":
        return InstrumentChordCollection(*[c for c in self.chords if c == name])

    def first(self) -> InstrumentChord | None:
        if self.chords:
            return self.chords[0]
        return None

    def generate_matrix(
        self,
        maxlen: int = MAXLEN,
        xpad: int = XPAD,
        ypad: int = YPAD,
        only_ascii: bool = False,
        variations: bool = True,
        even_x_distance: bool = True,
    ) -> "Generator[str]":
        def test_row_length(l: list[InstrumentChord]):
            length = sum(c.get_width(pad=xpad, min_width=self.min_chord_width if even_x_distance else None) for c in l)
            return length > maxlen

        chords: list[InstrumentChord] = []
        for chord in self.chords:
            if variations or not [c for c in chords if c.chord == chord.chord]:
                chords.append(chord)
        rows = list(split_before(chords, test_row_length))

        for idx, row in enumerate(rows):
            if idx > 0 and ypad:
                yield "\n" * (ypad - 1)
            for y in range(max((c.height + 1 for c in row), default=0)):
                yield functools.reduce(
                    operator.add,
                    [
                        c.get_row(
                            y,
                            pad=xpad,
                            min_width=self.min_chord_width if even_x_distance else None,
                            only_ascii=only_ascii,
                        ) for c in row
                    ],
                ).rstrip()

    def print_matrix(
        self,
        maxlen: int = MAXLEN,
        xpad: int = XPAD,
        ypad: int = YPAD,
        only_ascii: bool = False,
        variations: bool = True,
        even_x_distance: bool = True,
    ):
        for row in self.generate_matrix(
            maxlen=maxlen,
            xpad=xpad,
            ypad=ypad,
            only_ascii=only_ascii,
            variations=variations,
            even_x_distance=even_x_distance,
        ):
            print(row)

    # pylint: disable=redefined-builtin
    def sorted(self, ascii: bool = False):
        return InstrumentChordCollection(
            *sorted(self.chords, key=lambda c: c.chord.name if not ascii else c.chord.ascii)
        )

    def update(self, chords: Iterable[InstrumentChord]) -> Self:
        for chord in chords:
            if chord not in self.chords:
                self.chords.append(chord)
        return self
