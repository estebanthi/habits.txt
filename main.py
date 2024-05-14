import logging
import sys

import habits_txt.cli as cli


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    cli.cli(sys.argv[1:], default_map={})


if __name__ == "__main__":
    main()
