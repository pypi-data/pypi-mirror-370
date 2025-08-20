import dataclasses
import itertools
import re
from typing import Generator, Iterable

from chordist.chord import Chord


CHORD_PATT = r"[A-H][^\]\s]*"


@dataclasses.dataclass
class LyricsRowPiece:
    lyric: str
    chord_name: str | None = None
    chord: Chord | None = None

    def __post_init__(self):
        if self.chord_name and not self.chord:
            self.chord = Chord.get_or_null(self.chord_name)

    def __bool__(self):
        return bool(self.lyric) or bool(self.chord_name)

    def get_chord_name(self, only_ascii: bool = False) -> str:
        if self.chord:
            return self.chord.ascii if only_ascii else self.chord.name

        return self.chord_name or ""

    def get_inline(self, only_ascii: bool = False):
        chord_name = self.get_chord_name(only_ascii)

        if chord_name:
            return f"[{chord_name}]{self.lyric}"
        return self.lyric

    def get_lyric(self, only_ascii: bool = False) -> str:
        chord_name = self.get_chord_name(only_ascii)
        lyric = self.lyric

        if len(lyric) <= len(chord_name):
            lyric += "-"
            lyric = f"{lyric:{len(chord_name) + 1}s}"

        return lyric

    def transpose(self, steps: int):
        if not self.chord_name:
            return self

        if self.chord is None:
            raise ValueError(f"Could not transpose lyric '{self.lyric}': unidentified chord '{self.chord_name}'")

        chord = self.chord.transpose(steps)

        return LyricsRowPiece(lyric=self.lyric, chord_name=chord.name, chord=chord)


@dataclasses.dataclass
class LyricsRow:
    pieces: list[LyricsRowPiece] = dataclasses.field(default_factory=list)
    used_chords: list[Chord] = dataclasses.field(default_factory=list, init=False)

    def __post_init__(self):
        for piece in self.pieces:
            if piece.chord and piece.chord not in self.used_chords:
                self.used_chords.append(piece.chord)

    def __bool__(self):
        return any(self.pieces)

    @classmethod
    def create_inline(cls, row: str):
        pieces: list[LyricsRowPiece] = []

        for chord_name, lyric in re.findall(rf"(?:\[({CHORD_PATT})\])?([^[]*)", row):
            if chord_name or lyric:
                pieces.append(LyricsRowPiece(lyric, chord_name))

        return cls(pieces=pieces)

    @classmethod
    def create_split(cls, lyrics_row: str, chords_row: str = ""):
        pieces: list[LyricsRowPiece] = []
        matches = list(re.finditer(rf"(?: +)|(?:({CHORD_PATT}) *)", chords_row))

        if not matches:
            pieces.append(LyricsRowPiece(lyric=lyrics_row))
        else:
            for idx, match in enumerate(matches):
                chord_name = match.group(1)
                lyric = lyrics_row[match.start():match.end() if idx < len(matches) - 1 else len(lyrics_row)]
                pieces.append(LyricsRowPiece(lyric=lyric, chord_name=chord_name))

        return cls(pieces=pieces)

    def get_chords_row(self, only_ascii: bool = False):
        result = ""

        for piece in self.pieces:
            result += f"{piece.get_chord_name(only_ascii):{len(piece.get_lyric(only_ascii))}s}"

        return result.rstrip()

    def get_inline_row(self, only_ascii: bool = False):
        result = ""

        for piece in self.pieces:
            result += piece.get_inline(only_ascii=only_ascii)

        return result.strip()

    def get_lyrics_row(self, only_ascii: bool = False):
        result = ""

        for piece in self.pieces:
            result += piece.get_lyric(only_ascii)

        return result.rstrip(" -")

    def print(self, only_ascii: bool = False, chords_inline: bool = False):
        if chords_inline:
            print(self.get_inline_row(only_ascii=only_ascii))
        else:
            chords_row = self.get_chords_row(only_ascii=only_ascii)

            if chords_row:
                print(chords_row)

            print(self.get_lyrics_row(only_ascii=only_ascii))

    def transpose(self, steps: int):
        return LyricsRow([p.transpose(steps) for p in self.pieces])


@dataclasses.dataclass
class Lyrics:
    rows: list[LyricsRow] = dataclasses.field(default_factory=list)
    used_chords: list[Chord] = dataclasses.field(default_factory=list, init=False)

    def __post_init__(self):
        for row in self.rows:
            for chord in row.used_chords:
                if chord not in self.used_chords:
                    self.used_chords.append(chord)

    @classmethod
    def create(cls, lyrics: Iterable[Iterable[str] | str] | str, chords_inline: bool = True):
        lyrics_rows: list[LyricsRow] = []
        rows = cls.normalize_lyrics(lyrics)

        if not chords_inline:
            while True:
                try:
                    row = next(rows)

                    if row.strip() and cls.is_chord_row(row):
                        lyrics_rows.append(LyricsRow.create_split(lyrics_row=next(rows), chords_row=row))
                    else:
                        lyrics_rows.append(LyricsRow.create_split(lyrics_row=row))
                except StopIteration:
                    break

        for row in rows:
            lyrics_rows.append(LyricsRow.create_inline(row))

        return Lyrics(rows=lyrics_rows).strip()

    @staticmethod
    def is_chord_row(row: str):
        return re.match(rf"^( *({CHORD_PATT})* *)*$", row) is not None

    @staticmethod
    def normalize_lyrics(lyrics: Iterable[Iterable[str] | str] | str) -> "Generator[str]":
        """Inserts blank row between verses"""
        if isinstance(lyrics, str):
            lyrics = re.split("\r?\n", lyrics)

        for idx, row in enumerate(lyrics):
            if isinstance(row, str):
                yield row
            else:
                if idx > 0:
                    yield ""
                yield from row

    def print(self, only_ascii: bool = False, chords_inline: bool = False):
        for row in self.rows:
            row.print(only_ascii=only_ascii, chords_inline=chords_inline)

    def strip(self):
        rows = list(itertools.dropwhile(lambda r: not r, self.rows))

        for idx in range(len(rows) - 1, 0, -1):
            if not rows[idx]:
                del rows[idx]
            else:
                break

        return Lyrics(rows=rows)

    def transpose(self, steps: int):
        return Lyrics([r.transpose(steps) for r in self.rows])
