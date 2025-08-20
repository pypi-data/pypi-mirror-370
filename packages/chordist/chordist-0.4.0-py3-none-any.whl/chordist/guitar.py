import sys

from chordist.instrument import Instrument
from chordist.instrument_chord import (
    InstrumentChord,
    InstrumentChordCollection,
)
from chordist.song import Song


class Guitar(Instrument):
    string_count = 6


class GuitarChord(InstrumentChord):
    instrument = Guitar


BASE_CHORDS = InstrumentChordCollection(
    GuitarChord.create("A", (1, 1, "x"), (2, 3, 1), (2, 4, 2), (2, 5, 3)),
    GuitarChord.create("A⁷", (1, 1, "x"), (2, 3, 1), (2, 5, 2)),
    GuitarChord.create("Am", (1, 1, "x"), (1, 5, 1), (2, 3, 2), (2, 4, 3)),
    GuitarChord.create(
        "B",
        (1, 1, "x"),
        (2, 2, 1),
        (2, 3, 1),
        (2, 4, 1),
        (2, 5, 1),
        (2, 6, 1),
        (4, 3, 2),
        (4, 4, 3),
        (4, 5, 4),
    ),
    GuitarChord.create("B⁷", (1, 1, "x"), (1, 3, 1), (2, 2, 2), (2, 4, 3), (2, 6, 4)),
    GuitarChord.create("Bm", (1, 1, "x"), (2, 2, 1), (2, 6, 1), (3, 5, 2), (4, 3, 3), (4, 4, 4)),
    GuitarChord.create("C", (1, 1, "x"), (1, 5, 1), (2, 3, 2), (3, 2, 3)),
    GuitarChord.create("C⁷", (1, 1, "x"), (1, 5, 1), (2, 3, 2), (3, 2, 3), (3, 4, 4)),
    GuitarChord.create(
        "Cm",
        (3, 1, "x"),
        (3, 2, 1),
        (3, 3, 1),
        (3, 4, 1),
        (3, 5, 1),
        (3, 6, 1),
        (4, 5, 2),
        (5, 3, 3),
        (5, 4, 4),
    ),
    GuitarChord.create("D", (1, 1, "x"), (1, 2, "x"), (2, 4, 1), (2, 6, 2), (3, 5, 3)),
    GuitarChord.create("D⁷", (1, 1, "x"), (1, 2, "x"), (1, 5, 1), (2, 4, 2), (2, 6, 3)),
    GuitarChord.create("Dm", (1, 1, "x"), (1, 2, "x"), (1, 6, 1), (2, 4, 2), (3, 5, 3)),
    GuitarChord.create("E", (1, 4, 1), (2, 2, 2), (2, 3, 3)),
    GuitarChord.create("E⁷", (1, 4, 1), (2, 2, 2)),
    GuitarChord.create("Em", (2, 2, 1), (2, 3, 2)),
    GuitarChord.create("F", (1, 1, "x"), (1, 2, "x"), (1, 5, 1), (1, 6, 1), (2, 4, 2), (3, 3, 3)),
    GuitarChord.create("F⁷", (1, 1, 1), (1, 2, 1), (1, 3, 1), (1, 4, 1), (1, 5, 1), (1, 6, 1), (2, 4, 2), (3, 2, 3)),
    GuitarChord.create("Fm", (1, 1, 1), (1, 2, 1), (1, 3, 1), (1, 4, 1), (1, 5, 1), (1, 6, 1), (3, 2, 3), (3, 3, 4)),
    GuitarChord.create("G", (2, 2, 1), (3, 1, 2), (3, 6, 3)),
    GuitarChord.create("G⁷", (1, 6, 1), (2, 2, 2), (3, 1, 3)),
    GuitarChord.create("Gm", (3, 1, 1), (3, 2, 1), (3, 3, 1), (3, 4, 1), (3, 5, 1), (3, 6, 1), (5, 2, 3), (5, 3, 4)),
)


if __name__ == "__main__":
    arg1 = sys.argv[1] if len(sys.argv) > 1 else None

    if arg1 == "--example":
        Song.print_example(chords=BASE_CHORDS)
    else:
        BASE_CHORDS.print_matrix()
