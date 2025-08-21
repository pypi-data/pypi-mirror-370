from calendar import Calendar
import calendar
import os
from datetime import date, timedelta
from pathlib import Path
from typing import override
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.driver import Driver
from textual.types import CSSPathType
from textual.widgets import DataTable, Label


def get_style_path() -> str:
    xdg_path = os.getenv("XDG_CONFIG_HOME", None) or "~/.config"
    style_path = Path(xdg_path) / "tscal" / "style.tcss"
    if style_path.exists():
        return str(style_path)
    else:
        return "style.tcss"


class CalendarInTerminal(App[str]):
    ENABLE_COMMAND_PALETTE = False
    CSS_PATH = get_style_path()
    BINDINGS = [
        Binding("ctrl+f", "next_month", "Next Month"),
        Binding("ctrl+b", "prev_month", "Previous Month"),
        Binding("ctrl+n", "next_year", "Next Year"),
        Binding("ctrl+p", "prev_year", "Previous Year", priority=True),
        Binding("ctrl+t", "today", "Today"),
        Binding("q,escape", "quit", "Quit"),
    ]

    def action_today(self):
        self.selected_month = self.today.month
        self.selected_year = self.today.year
        self.refresh_calendar()

    def action_next_month(self):
        self.selected_month += 1
        if self.selected_month > 12:
            self.selected_month = 1
            self.selected_year += 1
        self.refresh_calendar()
            

    def action_prev_month(self):
        self.selected_month -= 1
        if self.selected_month < 1:
            self.selected_month = 12
            self.selected_year -= 1
        self.refresh_calendar()

    def action_next_year(self):
        self.selected_year += 1
        self.refresh_calendar()

    def action_prev_year(self):
        self.selected_year -= 1
        self.refresh_calendar()


    def refresh_calendar(self):
        month_name = calendar.month_name[self.selected_month]
        self.label.update(f"{month_name} {self.selected_year}")
        
        _ = self.table.clear()
        month_matrix = self.__get_selected_month()
        if coord := self.__populate_table(month_matrix):
            today = date.today()
            if self.selected_year == today.year and self.selected_month == today.month:
                self.table.cursor_coordinate = coord  # pyright: ignore[reportAttributeAccessIssue]
                self.table.action_select_cursor()

    
    def __init__(self, driver_class: type[Driver] | None = None, css_path: CSSPathType | None = None, watch_css: bool = False, ansi_color: bool = False):
        super().__init__(driver_class, css_path, watch_css, ansi_color)
        self._calendar: Calendar = Calendar(firstweekday=0)
        
        self.today: date = date.today()
        self.selected_year: int = self.today.year
        self.selected_month: int = self.today.month
        self.table: DataTable[str] = DataTable[str]()

        self.label: Label = Label(f"{calendar.month_name[self.selected_month]} {self.selected_year}", id="month-label")


    def __get_selected_month(self) -> list[list[date]]:
        dates = list(self._calendar.itermonthdates(self.selected_year, self.selected_month))
        
        while len(dates) < 42:
            last_date = dates[-1]
            next_date = date(last_date.year, last_date.month, last_date.day) + timedelta(days=1)
            dates.append(next_date)
        
        return [dates[i:i+7] for i in range(0, len(dates), 7)]

    def __populate_table(self, month_matrix: list[list[date]]) -> tuple[int, int] | None:
        today_coord = None
        for row_index, week in enumerate(month_matrix):
            row: list[str] = []
            for col_index, date_obj in enumerate(week):
                day_str = str(date_obj.day)
                if date_obj.month != self.selected_month:
                    day_str = f"[dim]{day_str}[/dim]"
                row.append(day_str)
                if date_obj == self.today:
                    today_coord = (row_index, col_index)
            _ = self.table.add_row(*row)
        return today_coord


    @override
    def compose(self) -> ComposeResult:
        _ = self.table.add_columns(*calendar.day_abbr)
        self.refresh_calendar()
        yield self.label
        yield self.table

def run():
    _ = CalendarInTerminal().run()


if __name__ == "__main__":
    run()
