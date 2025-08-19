# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

import json

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, DataTable, Footer, Header, Static

import geneva.cloudpickle as cloudpickle
from geneva.apply import ScanTask
from geneva.debug.entrypoint import run_udf_task_with_debug
from geneva.debug.logger import CheckpointStoreErrorLogger
from geneva.tui._screen import DismissOnQuitScreen
from geneva.tui.error import show_error


class ErrorLogsScreen(DismissOnQuitScreen):
    def __init__(
        self,
        *args,
        error_logger: CheckpointStoreErrorLogger,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.title = "Error Logs"
        self.error_logger = error_logger

    def compose(self) -> ComposeResult:
        yield Header(name=self.title)
        yield Footer()
        message = ""
        buttons = Vertical(
            Button("Connect to Debugger", id="debug"),
            Button("Run in Profiler", id="profile"),
            id="buttons",
        )

        self.table = get_error_table(self.error_logger)
        self.table.id = "error_table"

        yield Vertical(
            self.table,
            Horizontal(
                buttons,
                VerticalScroll(Static(message)),
            ),
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """An action to select the cursor."""

        row = self.table.cursor_row
        row = self.table.get_row_at(row)
        key = row[0]

        try:
            error_row = self.error_logger.get_error_row(key)
            task_json = error_row["task"][0].as_py()
            udf_data = error_row["udf"][0].as_py()

            task_dict = json.loads(task_json)
            task = ScanTask(**task_dict)
            udf = cloudpickle.loads(udf_data)
        except Exception as e:
            show_error(self.app, ex=e)
            return

        with self.app.suspend():
            run_udf_task_with_debug(task, udf)

    CSS = """
    #buttons {
        width: 10vw;
    }
    #error_table {
        height: 80vh;
        width: 100vw;
    }
    """


def get_error_table(
    error_logger: CheckpointStoreErrorLogger,
) -> DataTable:
    error_keys = list(error_logger.list_errors())

    table = DataTable(cursor_type="row")
    table.add_columns(
        "ID",
        "URI",
        "Input Columns",
        "Frament ID",
        "Offset",
        "Limit",
        "Batch Size",
        "Error",
    )

    for key in error_keys:
        error_row = error_logger.get_error_row(key)
        task_json = error_row["task"][0].as_py()
        task_dict = json.loads(task_json)
        error = error_row["error"][0].as_py()

        table.add_row(
            key,
            task_dict["uri"],
            task_dict["columns"],
            task_dict["frag_id"],
            task_dict["offset"],
            task_dict["limit"],
            task_dict["batch_size"],
            error,
        )

    return table
