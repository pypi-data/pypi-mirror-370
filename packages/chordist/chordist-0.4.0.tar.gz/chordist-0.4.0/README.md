Some helpful stuff for displaying song chords (or just the bare chords) for string instruments.

## Installation

Just run `pip install chordist` or `pipx install chordist`.

## CLI

When installed, the CLI command `chordist` will be made available.

```shell
$ chordist
usage: chordist [-h] [--instrument {guitar,banjo}] [--file FILE] [--chords-inline] [--collect-chords] [--even-x-distance] [--maxlen MAXLEN] [--variations] [--ascii] [--transpose TRANSPOSE]

options:
  -h, --help            show this help message and exit
  --instrument {guitar,banjo}, -i {guitar,banjo}
                        Default: guitar
  --file FILE, -f FILE  Text file with songs; if absent, all chords for the instrument will be printed
  --chords-inline       Input file uses the 'inlined chords' notation
  --collect-chords      When printing multiple songs, output all chords at the bottom instead of individually for each song
  --even-x-distance     Draw chords on equal distances horizontally
  --maxlen MAXLEN       Maximum output row length (default: 50)
  --variations          Print all available variations of each chord
  --ascii               Print chords in their simplified, ASCII only forms
  --transpose TRANSPOSE
                        Transpose all chords in the input file by this number of half notes
```

### On the input text file

A sequence of 2 or more empty rows will be interpreted as a boundary between two songs.

If a song is prefixed by a line enclosed in `**` (two asteriskes), the string within will be used for the song title.

Chords in the input file may be written in an inline fashion, like this:

```
**Roll in my sweet baby's arms**

[G]Roll in my sweet baby's arms
Roll in my sweet baby's [D7]arms
Gonna [G]lay around the shack
'Til the [C]mail train comes back
And [D7]roll in my sweet baby's [G]arms
```
... or above the lyrics, like this:

```
**Roll in my sweet baby's arms**

G
Roll in my sweet baby's arms
                        D7
Roll in my sweet baby's arms
      G
Gonna lay around the shack
         C
'Til the mail train comes back
    D7                      G
And roll in my sweet baby's arms
```
Use the `--chords-inline` parameter for the former notation. Note that the notation needs to be consistent throughout the file.

Chords may be written in the fancy, correct way ("A♭⁷", "C♯m⁷") or the simplified/ASCII way ("Ab7", "C#m7").

## Defining chords

A chord can be defined like so:

```python
from chordist.banjo import BanjoChord

em = BanjoChord.create("Em", (2, 1, 2), (2, 4, 3))
g = BanjoChord.create("G")
```

... where the arguments to `BanjoChord.create()` are the chord name followed by a tuple in the format `(fret number, string number, [finger number])` for each pressed string. String numbers are counted from the top/left, which I am sure somebody will take issue with (feel free to change this in your own fork in that case). The finger number can be omitted, in which case a `*` will be used. It can also be a string, for example `x` for muted strings.

## Bugs/caveats

Not yet able to render the high G string on a 5-string banjo in any useful way.
