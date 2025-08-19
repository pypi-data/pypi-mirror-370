# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

from textual.app import App, ComposeResult
from textual.containers import HorizontalScroll, Vertical, VerticalScroll
from textual.widgets import Footer, Header, Static

from geneva.tui._screen import DismissOnQuitScreen


class InfoScreen(DismissOnQuitScreen):
    def __init__(self, *args, msg: str, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.title = "Info"
        self.msg = msg

    def compose(self) -> ComposeResult:
        yield Header(name=self.title)
        yield Footer()
        yield Vertical(
            VerticalScroll(HorizontalScroll(Static(self.msg))),
            Static("q to dismiss", id="dismiss_msg"),
            id="msg_group",
        )

    CSS = """
    InfoScreen {
        background: rgba(128, 128, 128, 0.5);
        align: center middle;
    }
    #dismiss_msg {
        text-align: center;
    }
    #msg_group {
        height: 50%;
        width: 50%;
        background: rgba(64, 74, 89, 1);
        border: dashed white;
    }
    """


def show_info(app: App, *, msg: str) -> None:
    app.push_screen(InfoScreen(msg=msg))
