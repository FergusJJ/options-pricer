from textual.containers import Horizontal, Vertical
from textual.widgets import DataTable, Input, Button, Static
from textual.app import App, ComposeResult
from textual import on
import pandas as pd


class DataFrameViewer(App):
    def compose(self) -> ComposeResult:
        yield DataTable(zebra_stripes=True, cursor_type="row")

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        df = pd.read_csv("data.csv")

        # Add columns with keys for easy reference
        for col in df.columns:
            table.add_column(col, key=col)

        # Add rows with styling
        for idx, row in df.iterrows():
            table.add_row(*row.values, key=str(idx))


class InteractiveDataFrameBrowser(App):
    def __init__(self, df: pd.DataFrame):
        super().__init__()
        self.df = df
        self.filtered_df = df.copy()

    def compose(self) -> ComposeResult:
        with Vertical():
            with Horizontal():
                yield Input(placeholder="Search...", id="search")
                yield Button("Clear", id="clear")
            yield DataTable(id="table", zebra_stripes=True)
            yield Static("", id="status")

    @on(Input.Changed, "#search")
    def on_search_changed(self, event: Input.Changed) -> None:
        search_term = event.value.lower()
        if search_term:
            mask = self.df.astype(str).str.lower().str.contains(search_term).any(axis=1)
            self.filtered_df = self.df[mask]
        else:
            self.filtered_df = self.df.copy()
        self.refresh_table()

    def refresh_table(self) -> None:
        table = self.query_one(DataTable)
        table.clear()
        table.add_columns(*self.filtered_df.columns)

        for idx, row in self.filtered_df.iterrows():
            table.add_row(*row.values, key=str(idx))

        self.update_status()
