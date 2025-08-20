#!/usr/bin/env python3
import argparse

from chordist.song import SongCollection


def main():
    parser = argparse.ArgumentParser(prog="chordist")
    parser.add_argument("--instrument", "-i", choices=("guitar", "banjo"), default="guitar", help="Default: guitar")
    parser.add_argument(
        "--file",
        "-f",
        type=str,
        help="Text file with songs; if absent, all chords for the instrument will be printed",
    )
    parser.add_argument("--chords-inline", action="store_true", help="Input file uses the 'inlined chords' notation")
    parser.add_argument(
        "--collect-chords",
        action="store_true",
        help="When printing multiple songs, output all chords at the bottom instead of individually for each song",
    )
    parser.add_argument("--even-x-distance", action="store_true", help="Draw chords on equal distances horizontally")
    parser.add_argument("--maxlen", type=int, default=50, help="Maximum output row length (default: 50)")
    parser.add_argument("--variations", action="store_true", help="Print all available variations of each chord")
    parser.add_argument("--ascii", action="store_true", help="Print chords in their simplified, ASCII only forms")
    parser.add_argument(
        "--transpose",
        type=int,
        help="Transpose all chords in the input file by this number of half notes",
    )

    args = parser.parse_args()

    if args.instrument == "guitar":
        from chordist.guitar import BASE_CHORDS as CHORDS
    else:
        if args.variations:
            from chordist.banjo import ALL_CHORDS as CHORDS
        else:
            from chordist.banjo import BASE_CHORDS as CHORDS

    if args.file:
        collection = SongCollection(chords=CHORDS)
        collection.create_songs_from_file(args.file, chords_inline=args.chords_inline)
        if args.transpose:
            collection = collection.transpose(args.transpose)
        collection.print(
            maxlen=args.maxlen,
            collect_chords=args.collect_chords,
            even_x_distance=args.even_x_distance,
            variations=args.variations,
            only_ascii=args.ascii,
        )
    else:
        CHORDS.print_matrix(maxlen=args.maxlen, even_x_distance=args.even_x_distance)


if __name__ == "__main__":
    main()
