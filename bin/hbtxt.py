#!/usr/bin/python
import logging
import sys

import habits_txt.cli as cli
import habits_txt.config as config_


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    config_.setup()
    cli.cli(
        sys.argv[1:],
        default_map={
            "fill": {
                "file": config_.get("journal", "CLI"),
            },
            "filter": {
                "file": config_.get("journal", "CLI"),
            },
            "info": {
                "file": config_.get("journal", "CLI"),
            },
            "edit": {
                "file": config_.get("journal", "CLI"),
            },
            "check": {
                "file": config_.get("journal", "CLI"),
            },
        },
    )


if __name__ == "__main__":
    main()
