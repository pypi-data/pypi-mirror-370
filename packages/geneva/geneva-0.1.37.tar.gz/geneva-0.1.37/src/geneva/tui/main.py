# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

from lancedb.common import Credential
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.theme import BUILTIN_THEMES
from textual.widgets import Button, Footer, Header, Input, ProgressBar, Select, Static

import geneva
from geneva.db import Connection
from geneva.tui.error import show_error
from geneva.tui.tables import TablesList
from geneva.utils.sqlitekv import SQLiteKV


class ThemeSelector(Select[str]):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            [(theme, theme) for theme in BUILTIN_THEMES],
            *args,
            prompt="Theme",
            allow_blank=False,
            **kwargs,
        )

    def _watch_value(self, value) -> None:
        super()._watch_value(value)
        self.app.theme = value


class DbConnectionConfigBlock(Vertical):
    def __init__(self, *args, state: SQLiteKV, **kwargs) -> None:
        self._state = state

        self._uri = Input(
            placeholder="URI", id="uri", value=self._state.get("uri", None)
        )
        self._region = Input(
            placeholder="Region", id="region", value=self._state.get("region", None)
        )
        self._api_key = Input(placeholder="API Key", id="api_key", password=True)
        self._host_override = Input(
            placeholder="Host Override",
            id="host_override",
            value=self._state.get("host_override", None),
        )

        super().__init__(
            self._uri,
            self._region,
            self._api_key,
            self._host_override,
            *args,
            **kwargs,
        )

    def get_connection(self) -> Connection:
        if not self._uri.value:
            raise ValueError("URI is required.")
        if not self._region.value:
            raise ValueError("Region is required.")
        if not self._api_key.value:
            raise ValueError("API Key is required.")
        if not self._host_override.value:
            raise ValueError("Host Override is required.")

        self._state["uri"] = self._uri.value
        self._state["region"] = self._region.value
        self._state["host_override"] = self._host_override.value

        conn = geneva.connect(
            uri=self._uri.value,
            region=self._region.value,
            api_key=Credential(self._api_key.value),
            host_override=self._host_override.value,
        )
        return conn

    DEFAULT_CSS = """
    DbConnectionConfigBlock {
        width: 80%;
    }
    """


class GenevaLake(App):
    def __init__(
        self,
        *args,
        db_connection: Connection | None = None,
        error: str | None = None,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.db_connection = db_connection
        self.error = error
        self._state = SQLiteKV(".geneva_tui.db")

    def compose(self) -> ComposeResult:
        yield Header(name="geneva")
        theme_selector = ThemeSelector(
            value=next(iter(BUILTIN_THEMES)),
        )
        theme_selector_group = Vertical(
            Static("Theme", id="theme_selector_label"),
            theme_selector,
            id="theme_selector_group",
        )

        self.connection_config = DbConnectionConfigBlock(state=self._state)
        reconnect_button = Button("Connect/Refresh", id="connect_button")
        connection_config_group = Vertical(
            Static("DB Connection", id="db_connection_label"),
            self.connection_config,
            reconnect_button,
            id="connection_config_group",
        )

        separator = ProgressBar(
            show_bar=True,
            show_eta=False,
            show_percentage=False,
            id="setting_title_separator",
        )
        separator.total = 100
        separator.progress = 100
        setting_group = Vertical(
            Static("Settings", id="settings_label"),
            separator,
            theme_selector_group,
            connection_config_group,
            id="setting_group",
        )

        self.table_list = TablesList()
        self.table_list.set_connection(self.db_connection)

        db_tree_group = Vertical(
            Static("DB Tree", id="db_tree_label"),
            self.table_list,
            id="db_tree_group",
        )

        yield Horizontal(
            db_tree_group,
            setting_group,
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "connect_button":
            try:
                conn = self.connection_config.get_connection()
                self.table_list.set_connection(conn)
            except Exception as e:
                show_error(self.app, ex=e)
                self.table_list.set_connection(None)

    CSS = """
    #setting_group {
        width: 50vw
    }
    #theme_selector_label {
        text-align: center;
    }
    #settings_label {
        text-align: center;
    }
    #db_tree_label {
        text-align: center;
    }
    #setting_title_separator {
        align: center middle;
        width: 100%;
    }
    #db_connection_label {
        text-align: center;
    }
    #connection_config_group {
        align: center top;
    }
    #connect_button {
        align: center middle;
    }
    """


if __name__ == "__main__":
    GenevaLake().run()
