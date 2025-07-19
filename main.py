from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Header, Footer, Input, Button, DataTable, Static, Label
from textual.reactive import reactive
from textual import on
import pandas as pd

from pkg.ui import ui_button
from pkg.util import get_option_dates, get_option_chain, bsm_option_price


class BSMDisplay(Vertical):
    def compose(self) -> ComposeResult:
        with Horizontal(id="input-row"):
            yield Label("Ticker:")
            yield Input(value="AAPL", placeholder="AAPL", id="ticker")
            yield ui_button.ToggleButton(id="toggle_direction")


class OptionsApp(App):
    CSS_PATH = "styles.css"

    ticker_value = reactive("")
    date_value = reactive("")
    option_selected = reactive(False)

    def __init__(self, **kwargs):
        self.df: pd.DataFrame | None = None
        self.option_chain: pd.DataFrame | None = None
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        with VerticalScroll():
            yield BSMDisplay()
            yield DataTable(
                zebra_stripes=True,
                cursor_type="row",
                id="results_table",
                show_header=True,
            )
            yield ui_button.DynamicButton(id="dynamic_fetch", disabled=True)
            yield Static("", id="calculated_value")

    @on(Input.Changed)
    def on_ticker_changed(self, event: Input.Changed):
        self.ticker_value = event.value.strip()
        button = self.query_one("#dynamic_fetch", ui_button.DynamicButton)
        button.update_disabled_state(
            self.ticker_value, self.date_value, self.option_selected
        )

    @on(Button.Pressed, "#dynamic_fetch")
    def on_dynamic_button_pressed(self):
        button = self.query_one("#dynamic_fetch", ui_button.DynamicButton)
        if (button.state - 1) % 3 == button.states.FETCH_DATES:
            """Fetch dates, update state of button and then diable it until selection"""
            df = get_option_dates(self.ticker_value)
            self.update_table(df)
            button.update_disabled_state(
                self.ticker_value, self.date_value, self.option_selected
            )
        elif (button.state - 1) % 3 == button.states.FETCH_OPTION_CHAIN:
            """Fetch option chain, overwirte the dates table, reset the selected value"""
            self.update_table(self.option_chain)
            button.update_disabled_state(
                self.ticker_value, self.date_value, self.option_selected
            )
        elif (button.state - 1) % 3 == button.states.RESET:
            self.reset_state()
        else:
            raise Exception("This shouldn't happen")

    def update_table(self, df: pd.DataFrame) -> None:
        table = self.query_one("#results_table", DataTable)
        table.clear(columns=True)
        for col in df.columns:
            table.add_column(col, key=col)
        for idx, row in df.iterrows():
            table.add_row(*[str(val) for val in row.values], key=str(idx))
        self.df = df

    @on(DataTable.RowSelected)
    def on_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection in the DataTable"""
        button = self.query_one("#dynamic_fetch", ui_button.DynamicButton)
        if event.row_key is None:
            return
        if button.state == button.states.FETCH_DATES:
            return
        direction_button = self.query_one("#toggle_direction", ui_button.ToggleButton)
        row_index = int(event.row_key.value)
        if button.state == button.states.FETCH_OPTION_CHAIN:
            self.date_value = self.df.iloc[row_index]["Expiration Date"]
            df = get_option_chain(
                ticker=self.ticker_value,
                date=self.date_value,
                direction=direction_button.get_direction(),
            )
            self.option_chain = df
        elif button.state == button.states.RESET:
            option = self.df.iloc[row_index]
            val = bsm_option_price(
                self.ticker_value,
                self.date_value,
                direction=direction_button.get_direction(),
                selected_option=option,
            )
            self.option_selected = True
            self.update_bsm_value(val)
        else:
            raise Exception("(on_row_selected) Should not happen!!")
        button.update_disabled_state(
            self.ticker_value, self.date_value, self.option_selected
        )

    def update_bsm_value(self, calculated_price: float):
        self.query_one("#calculated_value", Static).update(
            f"BSM Price: ${calculated_price:.2f}"
        )

    def reset_state(self):
        self.date_value = ""
        self.option_selected = False
        self.df = None
        self.option_chain = None
        self.query_one("#results_table", DataTable).clear(columns=True)
        self.query_one("#calculated_value", Static).update("")
        self.query_one("#dynamic_fetch", ui_button.DynamicButton).update_disabled_state(
            self.ticker_value, self.date_value, self.option_selected
        )


if __name__ == "__main__":
    app = OptionsApp()
    app.run()
