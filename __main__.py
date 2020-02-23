from .trains import run
try:
    from .my_defaults import default_map, default_berths
except ImportError:
    default_map = "lec1"
    default_berths = [
        "WY0118",  # Random ones. I do not live here.
        "WS0004",
        "WS0002",
    ]
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m",
        "--map",
        help="Name code for map region, e.g. lec1 (see opentraintimes.com)",
    )
    parser.add_argument(
        "-b",
        "--berths",
        help="Comma-separated name codes for berths to subscribe to (see opentraintimes.com)",
        type=lambda s: s.split(','),
    )
    args = parser.parse_args()
    run(args.map or default_map, args.berths or default_berths)


if __name__ == "__main__":
    main()
