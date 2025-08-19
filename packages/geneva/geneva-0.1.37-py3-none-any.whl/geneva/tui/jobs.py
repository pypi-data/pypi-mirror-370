# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

from more_itertools import peekable
from textual.app import ComposeResult
from textual.widgets import DataTable, Footer, Header, Static
from textual.widgets.data_table import ColumnKey

from geneva.checkpoint import LanceCheckpointStore
from geneva.debug.logger import CheckpointStoreErrorLogger
from geneva.job.client import JobClient
from geneva.tui._screen import DismissOnQuitScreen
from geneva.tui.error import show_error
from geneva.tui.error_logs import ErrorLogsScreen


class JobsTable(DataTable):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, cursor_type="row", **kwargs)

    def action_select_cursor(self) -> None:
        row = self.cursor_row
        row = self.get_row_at(row)

        job_id_column_idx = self._column_locations.get(ColumnKey(value="id"))
        store_column_idx = self._column_locations.get(
            ColumnKey(value="checkpoint_store")
        )

        if job_id_column_idx is None:
            show_error(self.app, msg="No job id column found, this is not expected")
            return

        if store_column_idx is None:
            show_error(
                self.app, msg="No checkpoint store column found, this is not expected"
            )
            return

        store_name = row[store_column_idx]
        job_id = row[job_id_column_idx]

        checkpoint_store = LanceCheckpointStore(store_name)
        error_logger = CheckpointStoreErrorLogger(
            job_id=job_id, checkpoint_store=checkpoint_store
        )

        error_log_screen = ErrorLogsScreen(error_logger=error_logger)
        self.app.push_screen(error_log_screen)


class JobsScreen(DismissOnQuitScreen):
    def __init__(
        self, *args, client: JobClient, table_name: str | None = None, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.title = "Jobs"
        self.table_name = table_name
        self.client = client

    def compose(self) -> ComposeResult:
        yield Header(name=self.title)
        yield Footer()
        yield Static("Job History", id="job_history_label")

        table = JobsTable()

        try:
            first_job = peekable(self.client.list(table=self.table_name))
            for key in first_job.peek():
                table.add_column(label=key, key=key)

            # TODO(rmeng): make the UI partially load before the data is fetched
            for job in first_job:
                table.add_row(*job.values())

            yield table
        except StopIteration:
            yield Static("No jobs found")
