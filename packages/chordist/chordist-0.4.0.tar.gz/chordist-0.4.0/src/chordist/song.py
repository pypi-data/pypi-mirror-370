import dataclasses
import re
from typing import Iterable

from chordist.constants import MAXLEN, XPAD, YPAD
from chordist.instrument_chord import InstrumentChordCollection
from chordist.lyrics import Lyrics


@dataclasses.dataclass
class Song:
    chords: InstrumentChordCollection
    lyrics: Lyrics
    title: str = ""
    used_instrument_chords: InstrumentChordCollection = dataclasses.field(
        default_factory=InstrumentChordCollection,
        init=False,
    )

    def __post_init__(self):
        for chord in self.lyrics.used_chords:
            self.used_instrument_chords.update([c for c in self.chords if c == chord])

    @classmethod
    def create(
        cls,
        lyrics: Iterable[Iterable[str] | str] | str,
        chords: InstrumentChordCollection | None = None,
        title: str | None = None,
        chords_inline: bool = True,
    ):
        return Song(
            title=title or "",
            chords=chords or InstrumentChordCollection(),
            lyrics=Lyrics.create(lyrics=lyrics, chords_inline=chords_inline),
        )

    @classmethod
    def from_string(
        cls,
        string: str,
        chords: InstrumentChordCollection | None = None,
        chords_inline: bool = True,
    ):
        title: str | None = None
        string = string.strip().replace("\r\n", "\n")
        rows = string.split("\n")

        if rows:
            if title_match := re.fullmatch(r"\*\*(.*)\*\*", rows[0]):
                title = title_match.group(1)
                rows = rows[1:]

        return cls.create(lyrics=rows, chords=chords, chords_inline=chords_inline, title=title)

    @classmethod
    def print_example(cls, chords: InstrumentChordCollection):
        verses = [
            [
                "[G]Ain't gonna work on the railroad",
                "Ain't gonna work on the [D7]farm",
                "Gonna [G]lay around the shack",
                "'Til the [C]mail train comes back",
                "And [D7]roll in my sweet baby's [G]arms",
            ],
            [
                "Now [G]where was you last Friday night",
                "While I was lyin' in [D7]jail?",
                "[G]Walkin' the streets with a[C]nother man",
                "[D7]Wouldn't even go my [G]bail",
            ],
        ]
        chorus = [
            "[G]Roll in my sweet baby's arms",
            "Roll in my sweet baby's [D7]arms",
            "Gonna [G]lay around the shack",
            "'Til the [C]mail train comes back",
            "And [D7]roll in my sweet baby's [G]arms",
        ]
        lyrics = [chorus, verses[0], chorus, verses[1], chorus]
        song = cls.create(lyrics=lyrics, chords=chords)
        song.print()

    def print(
        self,
        maxlen: int = MAXLEN,
        xpad: int = XPAD,
        ypad: int = YPAD,
        only_ascii: bool = False,
        variations: bool = True,
        chords_inline: bool = False,
        even_x_distance: bool = True,
    ):
        self.print_title_and_lyrics(only_ascii=only_ascii, chords_inline=chords_inline)
        print()
        self.print_chords(
            maxlen=maxlen,
            xpad=xpad,
            ypad=ypad,
            only_ascii=only_ascii,
            variations=variations,
            even_x_distance=even_x_distance,
        )

    def print_chords(
        self,
        maxlen: int = MAXLEN,
        xpad: int = XPAD,
        ypad: int = YPAD,
        only_ascii: bool = False,
        variations: bool = True,
        even_x_distance: bool = True,
    ):
        self.used_instrument_chords.print_matrix(
            maxlen=maxlen,
            xpad=xpad,
            ypad=ypad,
            only_ascii=only_ascii,
            variations=variations,
            even_x_distance=even_x_distance,
        )

    def print_title(self):
        print(self.title)
        print("=" * len(self.title))

    def print_title_and_lyrics(self, only_ascii: bool = False, chords_inline: bool = False):
        if self.title:
            self.print_title()
        self.lyrics.print(only_ascii=only_ascii, chords_inline=chords_inline)

    def transpose(self, steps: int):
        return Song(
            chords=self.chords,
            lyrics=self.lyrics.transpose(steps),
            title=self.title,
        )


@dataclasses.dataclass
class SongCollection:
    songs: list[Song] = dataclasses.field(default_factory=list)
    chords: InstrumentChordCollection = dataclasses.field(default_factory=InstrumentChordCollection)
    used_instrument_chords: InstrumentChordCollection = dataclasses.field(
        default_factory=InstrumentChordCollection,
        init=False,
    )

    def __post_init__(self):
        for song in self.songs:
            self.used_instrument_chords.update(song.used_instrument_chords)

    def __iter__(self):
        return iter(self.songs)

    def __len__(self):
        return len(self.songs)

    def add_songs(self, *songs: Song):
        self.songs.extend(songs)
        self.used_instrument_chords.update(*[s.used_instrument_chords for s in songs])

    def create_song(
        self,
        lyrics: Iterable[Iterable[str] | str] | str,
        title: str | None = None,
        chords_inline: bool = True,
    ) -> Song:
        song = Song.create(lyrics=lyrics, chords=self.chords, title=title, chords_inline=chords_inline)
        self.add_songs(song)
        return song

    def create_songs_from_file(self, filename: str, chords_inline: bool = True):
        with open(filename, "rt", encoding="utf8") as f:
            text = f.read()
        for song_text in re.split(r"(?:\r?\n){3,}", text):
            self.add_songs(Song.from_string(string=song_text.strip(), chords=self.chords, chords_inline=chords_inline))

    def print(
        self,
        maxlen: int = MAXLEN,
        xpad: int = XPAD,
        ypad: int = YPAD,
        collect_chords: bool = True,
        only_ascii: bool = False,
        variations: bool = True,
        chords_inline: bool = False,
        even_x_distance: bool = True,
    ):
        for idx, song in enumerate(self.songs):
            if idx > 0:
                print("\n")
            song.print_title_and_lyrics(only_ascii, chords_inline=chords_inline)
            if not collect_chords:
                print()
                song.print_chords(
                    only_ascii=only_ascii,
                    maxlen=maxlen,
                    xpad=xpad,
                    ypad=ypad,
                    variations=variations,
                    even_x_distance=even_x_distance,
                )

        if collect_chords:
            print()
            self.print_chords(
                only_ascii=only_ascii,
                maxlen=maxlen,
                xpad=xpad,
                ypad=ypad,
                even_x_distance=even_x_distance,
                variations=variations,
            )

    def print_chords(
        self,
        maxlen: int = MAXLEN,
        xpad: int = XPAD,
        ypad: int = YPAD,
        only_ascii: bool = False,
        variations: bool = True,
        even_x_distance: bool = True,
    ):
        chords = self.used_instrument_chords.sorted(ascii=only_ascii)
        chords.print_matrix(
            maxlen=maxlen,
            xpad=xpad,
            ypad=ypad,
            only_ascii=only_ascii,
            variations=variations,
            even_x_distance=even_x_distance,
        )

    def transpose(self, steps: int):
        return SongCollection(
            songs=[s.transpose(steps) for s in self.songs],
            chords=self.chords,
        )
