import sys

from chordist.instrument import Instrument
from chordist.instrument_chord import (
    InstrumentChord,
    InstrumentChordCollection,
)
from chordist.song import Song


class Banjo(Instrument):
    string_count = 4


class BanjoChord(InstrumentChord):
    instrument = Banjo


# (fret number, string number, [finger number])
BASE_CHORDS = InstrumentChordCollection(
    BanjoChord.create("A", (2, 1, 1), (2, 2, 1), (2, 3, 1), (2, 4, 1)),
    BanjoChord.create("A⁷", (2, 1, 1), (2, 2, 1), (2, 3, 1), (2, 4, 1)),
    BanjoChord.create("Adim⁷", (1, 1, 1), (1, 3, 1), (2, 2, 2), (4, 4, 3)),
    BanjoChord.create("Am", (1, 3, 1), (2, 1, 2), (2, 2, 3), (2, 4, 4)),
    BanjoChord.create("Am⁷", (5, 2, 1), (5, 3, 1), (5, 4, 1), (7, 1, 3)),
    BanjoChord.create("Amaj⁷", (2, 1, 1), (2, 2, 1), (2, 3, 1), (6, 4, 4)),
    BanjoChord.create("A♭", (1, 1, 1), (1, 2, 1), (1, 3, 1), (1, 4, 1)),
    BanjoChord.create("A♭⁷", (4, 3, 1), (4, 4, 1), (5, 2, 2), (6, 1, 3)),
    BanjoChord.create("A♭dim⁷", (1, 2, 1), (3, 4, 3)),
    BanjoChord.create("A♭m", (1, 1, 1), (1, 2, 2), (1, 4, 3)),
    BanjoChord.create("A♭m⁷", (4, 2, 1), (4, 3, 1), (4, 4, 1), (6, 1, 3)),
    BanjoChord.create("A♭maj⁷", (1, 1, 1), (1, 2, 1), (1, 3, 1), (1, 4, 1)),
    BanjoChord.create("B", (4, 1, 1), (4, 2, 1), (4, 3, 1), (4, 4, 1)),
    BanjoChord.create("B⁷", (1, 1, 1), (1, 4, 2), (2, 2, 3)),
    BanjoChord.create("Bdim⁷", (1, 2, 1), (3, 4, 3)),
    BanjoChord.create("Bm", (3, 3, 1), (4, 1, 2), (4, 2, 3)),
    BanjoChord.create("Bm⁷", (7, 2, 1), (7, 3, 1), (7, 4, 1), (9, 1, 3)),
    BanjoChord.create("Bmaj⁷", (1, 1, 1), (3, 2, 2), (4, 4, 3)),
    BanjoChord.create("B♭", (3, 2, 1), (3, 3, 1), (3, 4, 1)),
    BanjoChord.create("B♭⁷", (6, 3, 1), (6, 4, 1), (7, 2, 2), (8, 1, 3)),
    BanjoChord.create("B♭dim⁷", (2, 1, 1), (2, 3, 1), (2, 4, 1), (3, 2, 2)),
    BanjoChord.create("B♭m", (6, 2, 1), (6, 3, 1), (8, 1, 3), (8, 4, 4)),
    BanjoChord.create("B♭m⁷", (6, 2, 1), (6, 3, 1), (6, 4, 1), (8, 1, 3)),
    BanjoChord.create("B♭maj⁷", (3, 1, 1), (3, 2, 1), (3, 3, 1), (7, 4, 4)),
    BanjoChord.create("C", (1, 3, 1), (2, 1, 2), (2, 4, 3)),
    BanjoChord.create("C⁷", (1, 3, 1), (2, 1, 3), (2, 4, 2), (3, 2, 4)),
    BanjoChord.create("Cdim⁷", (1, 3, 1), (2, 1, 3), (2, 4, 2), (3, 2, 4)),
    BanjoChord.create("Cm", (1, 1, 1), (1, 3, 2), (1, 4, 3)),
    BanjoChord.create("Cm⁷", (1, 1, 1), (1, 3, 1), (1, 4, 1), (3, 2, 2)),
    BanjoChord.create("Cmaj⁷", (1, 3, 1), (2, 4, 2), (2, 1, 3), (4, 2, 4)),
    BanjoChord.create("C♯", (6, 1, 1), (6, 2, 1), (6, 3, 1), (6, 4, 1)),
    BanjoChord.create("C♯⁷", (9, 3, 1), (9, 4, 1), (10, 2, 2), (11, 1, 3)),
    BanjoChord.create("C♯dim⁷", (2, 1, 1), (3, 2, 2), (2, 3, 1), (2, 4, 1)),
    BanjoChord.create("C♯m", (9, 2, 1), (9, 3, 1), (11, 1, 3), (11, 4, 4)),
    BanjoChord.create("C♯m⁷", (9, 2, 1), (9, 3, 1), (9, 4, 1), (11, 1, 3)),
    BanjoChord.create("C♯maj⁷", (6, 1, 1), (6, 2, 1), (6, 3, 1), (10, 4, 4)),
    BanjoChord.create("D", (2, 2, 1), (3, 3, 2), (4, 4, 3)),
    BanjoChord.create("D⁷", (1, 3, 1), (2, 2, 2), (4, 4, 4)),
    BanjoChord.create("Ddim⁷", (1, 2, 1), (3, 4, 2)),
    BanjoChord.create("Dm", (2, 2, 1), (3, 3, 2), (3, 4, 3)),
    BanjoChord.create("Dm⁷", (1, 3, 1), (2, 2, 2), (3, 4, 4)),
    BanjoChord.create("Dmaj⁷", (2, 2, 1), (2, 3, 1), (4, 4, 3)),
    BanjoChord.create("E", (1, 2, 1), (2, 1, 2), (2, 4, 3)),
    BanjoChord.create("E⁷", (1, 2, 1), (2, 1, 2)),
    BanjoChord.create("Edim⁷", (2, 1, 1), (2, 3, 1), (2, 4, 1), (3, 2, 2)),
    BanjoChord.create("Em", (2, 1, 2), (2, 4, 3)),
    BanjoChord.create("Em⁷", (2, 1, 2)),
    BanjoChord.create("Emaj⁷", (1, 1, 1), (1, 2, 2), (2, 4, 3)),
    BanjoChord.create("E♭", (3, 2, 1), (4, 3, 2), (5, 1, 3), (5, 4, 4)),
    BanjoChord.create("E♭⁷", (1, 1, 1), (2, 3, 2), (3, 2, 3), (5, 4, 4)),
    BanjoChord.create("E♭dim⁷", (1, 1, 1), (1, 3, 1), (2, 2, 2), (4, 4, 4)),
    BanjoChord.create("E♭m", (3, 2, 1), (4, 1, 2), (4, 3, 3), (4, 4, 4)),
    BanjoChord.create("E♭m⁷", (1, 1, 1), (2, 3, 2), (3, 2, 3), (4, 4, 4)),
    BanjoChord.create("E♭maj⁷", (3, 2, 1), (4, 3, 2)),
    BanjoChord.create("F", (1, 3, 1), (2, 2, 2), (3, 1, 3), (3, 4, 4)),
    BanjoChord.create("F⁷", (1, 3, 1), (1, 4, 1), (2, 2, 2), (3, 1, 3)),
    BanjoChord.create("Fdim⁷", (1, 2, 1), (3, 4, 2)),
    BanjoChord.create("Fm", (1, 2, 1), (1, 3, 1), (3, 1, 3), (3, 4, 4)),
    BanjoChord.create("Fm⁷", (1, 2, 1), (1, 3, 1), (1, 4, 1), (3, 1, 3)),
    BanjoChord.create("Fmaj⁷", (1, 3, 1), (2, 1, 2), (2, 2, 3), (3, 4, 4)),
    BanjoChord.create("F♯", (2, 3, 1), (3, 2, 2), (4, 1, 3), (4, 4, 4)),
    BanjoChord.create("F♯⁷", (2, 3, 1), (2, 4, 1), (3, 2, 2), (4, 1, 3)),
    BanjoChord.create("F♯dim⁷", (1, 1, 1), (1, 3, 1), (2, 2, 2), (4, 4, 3)),
    BanjoChord.create("F♯m", (2, 2, 1), (2, 3, 1), (4, 1, 3), (4, 4, 4)),
    BanjoChord.create("F♯m⁷", (2, 2, 1), (2, 3, 1), (2, 4, 1), (4, 1, 3)),
    BanjoChord.create("F♯maj⁷", (2, 3, 1), (3, 1, 2), (3, 2, 3), (4, 4, 4)),
    BanjoChord.create("G"),
    BanjoChord.create("G⁷", (3, 4, 3)),
    BanjoChord.create("Gdim⁷", (2, 1, 1), (2, 3, 1), (2, 4, 1), (3, 2, 2)),
    BanjoChord.create("Gm", (3, 2, 1), (3, 3, 2)),
    BanjoChord.create("Gm⁷", (3, 2, 1), (3, 3, 1), (3, 4, 1), (5, 1, 3)),
    BanjoChord.create("Gmaj⁷", (4, 4, 3)),
)

BASE_CHORD_ALTERNATIVES = InstrumentChordCollection(
    BanjoChord.create("A♭⁷", (4, 3, 1), (4, 4, 1), (5, 2, 2), (6, 1, 3)),
    BanjoChord.create("A♭dim⁷", (1, 2, 1), (3, 1, 3)),
    BanjoChord.create("A⁷", (5, 3, 1), (5, 4, 1), (6, 2, 2), (7, 1, 3)),
    BanjoChord.create("B⁷", (4, 1, 1), (4, 2, 1), (4, 3, 1), (7, 4, 3)),
    BanjoChord.create("B⁷", (4, 2, 1), (4, 3, 1), (4, 4, 1), (7, 1, 3)),
    BanjoChord.create("Bdim⁷", (1, 2, 1), (3, 1, 2)),
    BanjoChord.create("Bm", (3, 3, 1), (4, 1, 2), (4, 2, 3), (4, 4, 4)),
    BanjoChord.create("Bmaj⁷", (1, 4, 1), (3, 2, 2), (4, 1, 3)),
    BanjoChord.create("Bmaj⁷", (4, 1, 1), (4, 2, 1), (4, 3, 1), (8, 4, 3)),
    BanjoChord.create("C", (5, 1, 1), (5, 2, 1), (5, 3, 1), (5, 4, 1)),
    BanjoChord.create("C♯", (9, 3, 1), (10, 2, 2), (11, 1, 3), (11, 4, 4)),
    BanjoChord.create("C⁷", (5, 1, 1), (5, 2, 1), (5, 3, 1), (8, 4, 3)),
    BanjoChord.create("C⁷", (5, 2, 1), (5, 3, 1), (5, 4, 1), (8, 1, 2)),
    BanjoChord.create("C⁷", (8, 3, 1), (8, 4, 1), (9, 2, 2), (10, 1, 3)),
    BanjoChord.create("D", (2, 2, 1), (3, 3, 2), (4, 1, 3)),
    BanjoChord.create("D", (7, 1, 1), (7, 2, 1), (7, 3, 1), (7, 4, 1)),
    BanjoChord.create("Ddim⁷", (1, 2, 1), (3, 1, 2)),
    BanjoChord.create("Dm", (2, 2, 1), (3, 1, 2), (3, 3, 3)),
    BanjoChord.create("E♭dim⁷", (1, 3, 1), (1, 4, 1), (2, 2, 2), (4, 1, 3)),
    BanjoChord.create("E♭maj⁷", (1, 4, 1), (3, 2, 2), (3, 3, 3)),
    BanjoChord.create("E⁷", (1, 2, 1), (2, 4, 2)),
    BanjoChord.create("F", (10, 1, 1), (10, 2, 1), (10, 3, 1), (10, 4, 1)),
    BanjoChord.create("F♯dim⁷", (1, 3, 1), (1, 4, 1), (2, 2, 2), (4, 1, 3)),
    BanjoChord.create("Fdim⁷", (1, 2, 1), (3, 1, 3)),
    BanjoChord.create("Gm", (3, 2, 1), (3, 3, 2), (5, 1, 3), (5, 4, 4)),
    BanjoChord.create("Gmaj⁷", (4, 1, 3)),
    BanjoChord.create("Gmaj⁷", (4, 2, 1), (4, 4, 3)),
)

ALL_CHORDS = BASE_CHORDS + BASE_CHORD_ALTERNATIVES


if __name__ == "__main__":
    arg1 = sys.argv[1] if len(sys.argv) > 1 else None

    if arg1 == "--example":
        Song.print_example(chords=BASE_CHORDS)
    else:
        BASE_CHORDS.print_matrix()
