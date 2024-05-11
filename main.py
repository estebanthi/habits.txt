import logging
import sys

import habits_txt.cli as cli


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    args = cli.parse_args(sys.argv[1:])
    cli.run_command(args)


if __name__ == "__main__":
    main()
