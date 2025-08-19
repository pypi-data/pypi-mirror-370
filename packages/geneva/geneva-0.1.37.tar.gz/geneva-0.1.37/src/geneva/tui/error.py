# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

import os
import traceback

from textual.app import App, ComposeResult
from textual.containers import HorizontalScroll, Vertical, VerticalScroll
from textual.widgets import Footer, Header, Static

from geneva.tui._screen import DismissOnQuitScreen


class ErrorScreen(DismissOnQuitScreen):
    def __init__(self, *args, error_msg: str, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.title = "Error"
        self.msg = error_msg

    def compose(self) -> ComposeResult:
        yield Header(name=self.title)
        yield Footer()
        yield Vertical(
            Static("An error occurred. Please try again later.", id="error"),
            VerticalScroll(HorizontalScroll(Static(self.msg, id="error_msg"))).focus(),
            Static("q to dismiss", id="dismiss_msg"),
            id="error_group",
        )

    CSS = """
    ErrorScreen {
        background: rgba(128, 128, 128, 0.5);
        align: center middle;
    }
    #error_msg {
        color: red;
    }
    #dismiss_msg {
        text-align: center;
    }
    #error {
        color: yellow;
    }
    #error_group {
        height: 50%;
        width: 50%;
        background: rgba(11, 3, 168, 1);
        border: dashed white;
    }
    """


_SHOULD_PDB_ERRORS = os.environ.get("GENEVA_TUI_PDB", "").lower() in (
    "true",
    "1",
    "yes",
    "y",
)


def show_error(
    app: App,
    *,
    msg: str | None = None,
    ex: Exception | None = None,
    start_pdb: bool = _SHOULD_PDB_ERRORS,
) -> None:
    if start_pdb:
        with app.suspend():
            import pdb  # noqa: T100

            pdb.post_mortem()

    if msg is None and ex is None:
        raise ValueError("Either msg or ex must be provided")

    if ex is not None:
        stack = traceback.format_exception(ex)
        msg = "\n".join(stack)

    assert msg is not None

    app.push_screen(ErrorScreen(error_msg=msg))
