from .trains import run
from .my_defaults import default_map, default_berths
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
