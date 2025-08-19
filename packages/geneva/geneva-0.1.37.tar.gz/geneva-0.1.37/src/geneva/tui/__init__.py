# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

import argparse

from textual_serve.server import Server

from geneva.tui.main import GenevaLake


def server() -> None:
    Server(f"python -m {__name__}.main").serve(debug=True)


def run_console(args: argparse.Namespace) -> None:
    if args.server:
        server()
    else:
        GenevaLake().run()


def register_console_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("console", description="Run a textual server")

    parser.add_argument("--server", action="store_true", help="Run a textual server")

    parser.set_defaults(func=run_console)
