# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Header


class DismissOnQuitScreen(Screen):
    """
    Super simple screen that pops itself when 'q' is pressed.
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._result = None

    def action_quit(self) -> None:
        self.dismiss(self._result)


def nested(screen: Screen) -> ComposeResult:
    """
    A generator that yields screens from a nested screen.
    """
    for item in screen.compose():
        if isinstance(item, Footer | Header):
            continue
        yield item
