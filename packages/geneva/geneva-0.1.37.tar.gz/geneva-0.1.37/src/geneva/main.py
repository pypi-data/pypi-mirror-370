# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

#!/usr/bin/env python3

import argparse
import logging

from geneva.debug.entrypoint import register_debug_parser
from geneva.tui import register_console_parser


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="Enable verbose logging",
    )

    subparsers = parser.add_subparsers(dest="actions", required=True)

    register_debug_parser(subparsers)
    register_console_parser(subparsers)

    args = parser.parse_args()
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)
    args.func(args)


if __name__ == "__main__":
    main()
