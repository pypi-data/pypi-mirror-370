# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import Reactive, reactive
from textual.widgets import (
    DataTable,
    Footer,
    Header,
    Static,
    TabbedContent,
    TabPane,
    Tree,
)

from geneva.db import Connection
from geneva.table import Table
from geneva.tui._screen import DismissOnQuitScreen, nested
from geneva.tui.error import show_error
from geneva.tui.info import show_info
from geneva.tui.jobs import JobsScreen

if TYPE_CHECKING:
    import pyarrow as pa


class SchemaTable(DataTable):
    BINDINGS = [
        ("ctrl+r", "run", "Run Job"),
    ]

    def __init__(self, *args, table: Table, **kwargs) -> None:
        super().__init__(*args, cursor_type="row", **kwargs)
        self.table = table
        self.add_columns("Name", "Type", "Nullable", "UDF", "Docker")
        for field in self.table.schema:
            udf, docker = "", ""
            field: pa.Field = field
            if (
                field.metadata is not None
                and b"virtual_column.udf_name" in field.metadata
            ):
                udf = field.metadata[b"virtual_column.udf_name"].decode("utf-8")
                docker = field.metadata[b"virtual_column.image"].decode("utf-8")
            self.add_row(field.name, field.type, field.nullable, udf, docker)

    def action_run(self) -> None:
        row = self.cursor_row
        row = self.get_row_at(row)
        name, _, _, udf, docker = row
        if not udf or not docker:
            show_error(self.app, msg="Not a virtual column")
            return
        self.table._conn.jobs.start(table=self.table.name, column=name)
        show_info(self.app, msg="Job started")


class TableDetailsScreen(DismissOnQuitScreen):
    def __init__(
        self,
        *args,
        table: Table,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.title = table.name
        self.table = table

    def compose(self) -> ComposeResult:
        yield Header(name=self.title)
        yield Footer()

        schema = SchemaTable(table=self.table, id="schema_table")

        schema_group = Vertical(
            Static("Schema", id="schema_label"),
            schema,
        )

        indices = list(self.table.list_indices())
        table_info = DataTable(id="table_info_table")
        table_info.add_columns("", "")
        table_info.add_row("Version", self.table.version)
        table_info.add_row("Row Count", self.table.count_rows())
        table_info.add_row("Column Count", len(self.table.schema))
        table_info.add_row("Indices Count", len(indices))

        table_info_group = Vertical(
            Static("Table Info", id="table_info_label"),
            table_info,
        )

        table_detail_group = Horizontal(
            table_info_group,
            schema_group,
        )

        sample = self.table.search().limit(10).to_arrow().to_pylist()

        sample_data = DataTable()
        if sample:
            sample_data.add_columns(*sample[0].keys())
            for row in sample:
                sample_data.add_row(*row.values())

        sample_data_group = Vertical(
            Static("Sample Data", id="sample_data_label"),
            sample_data,
        )

        all_groups = Vertical(
            table_detail_group,
            sample_data_group,
        )

        yield all_groups

    CSS = """
    #schema_table {
        align: center middle;
        width: 100%;
        height: 100%;
    }
    #table_info_table {
        align: center middle;
        width: 100%;
        height: 100%;
    }
    #schema_label {
        text-align: center;
    }
    #table_info_label {
        text-align: center;
    }
    #sample_data_label {
        text-align: center;
    }
    """


class MultiTabTableDetailsScreen(DismissOnQuitScreen):
    BINDINGS = {("r", "refresh", "Refresh")}

    def __init__(
        self,
        *args,
        table: Table,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.title = "Tables"
        self.table = table

    def compose(self) -> ComposeResult:
        yield Header(name=self.title)
        yield Footer()

        with TabbedContent():
            with TabPane("Info", name="Info"):
                # display screen in screen but trim the header and footer
                yield from nested(TableDetailsScreen(table=self.table))
            with TabPane("Job History", name="Job History"):
                yield from nested(
                    JobsScreen(client=self.table._conn.jobs, table_name=self.table.name)
                )

    CSS = """
    #job_history_label {
        text-align: center;
    }
    """
    # Bring in the CSS from the TableDetailsScreen
    CSS += TableDetailsScreen.CSS

    def action_refresh(self) -> None:
        # make sure the connection is still alive
        self.table._conn.table_names()
        self.refresh(recompose=True)


class TablesList(Tree):
    db_conn: Reactive[Connection | None] = reactive(None)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, label="catalog (NOT CONNECTED)", **kwargs)

    def set_connection(self, db_conn: Connection | None) -> None:
        self.db_conn = db_conn
        if self.db_conn is not None:
            self.root.label = "catalog"
            self.root.remove_children()
            self.db = self.root.add_leaf(self.db_conn._uri)
            for table in self.db_conn.table_names():
                self.db.add_leaf(table)
            self.root.expand_all()
        else:
            self.root.label = "catalog (NOT CONNECTED)"
            self.root.remove_children()

    def action_select_cursor(self) -> None:
        super().action_select_cursor()
        node = self.cursor_node
        # don't do anything if the cursor is on the root or the db node
        if node is self.root or node is self.db:
            return

        assert self.db_conn is not None, (
            "if you can select a table, the connection should not be None"
        )

        if node is not None and node.label is not None:
            table = self.db_conn.open_table(str(node.label))
            self.app.push_screen(MultiTabTableDetailsScreen(table=table))
