import datetime
import json
from dataclasses import dataclass
from importlib.abc import Traversable
from operator import itemgetter
from pathlib import Path
from typing import Any


def to_local_time(datetime_: datetime.datetime) -> datetime.datetime:
    # Convert the datetime to the local time zone.
    return datetime_.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)


def format_datetime(datetime_: datetime.datetime) -> str:
    return datetime_.strftime("%d-%m-%Y %H:%M:%S")


def format_timedelta(timedelta_: datetime.timedelta) -> str:
    days = timedelta_.days
    hours = timedelta_.seconds // 3600
    minutes = (timedelta_.seconds // 60) % 60
    seconds = timedelta_.seconds % 60

    return f'{days} day{"s" if days != 1 else ""}, {hours}h:{minutes}m:{seconds}s'


def format_filesize(size):
    if size < 1024:
        return f"{size} bytes"
    elif size < 1024 * 1024:
        return "{:.2f} KiB".format(size / 1024)
    elif size < 1024 * 1024 * 1024:
        return "{:.2f} MiB".format(size / (1024 * 1024))
    else:
        return "{:.2f} GiB".format(size / (1024 * 1024 * 1024))


def is_match(search: str, target: str) -> bool:
    case_sensitive = any(c.isupper() for c in search)

    if case_sensitive:
        return search in target
    else:
        return search.casefold() in target.casefold()


def read_json(path: Path | Traversable):
    return json.loads(path.read_text(encoding="utf-8"))


class TablePrinter:
    """Minimal pretty printer for ASCII tables"""

    ALIGN_LEFT = "<"
    ALIGN_RIGHT = ">"
    ALIGN_CENTER = "^"
    ALIGN_AUTO = "?"

    @dataclass
    class Column:
        name: str
        width: int
        column_align: str
        row_align: str

    def __init__(self):
        """Construct a new table printer without any columns or rows."""
        self.columns: list[TablePrinter.Column] = []
        self.rows: list[list[str]] = []

    def add_column(
        self, name: str, column_align: str = ALIGN_CENTER, row_align: str = ALIGN_AUTO
    ):
        """Add a new column to the table printer.

        :param name: The name of the column.
        :param column_align: The alignment of the column header.
        :param row_align: The alignment of the row cells.
        :raises AssertionError: If the rows are not empty.
        """
        assert len(self.rows) == 0, "rows must be empty"
        assert (
            column_align != TablePrinter.ALIGN_AUTO
        ), "column align cannot be ALIGN_AUTO"
        self.columns.append(
            TablePrinter.Column(name, len(name), column_align, row_align)
        )

    def add_row(self, data: list[Any]):
        """Add a new row to the table printer.

        :param data: The list of row cell data.
        :raises AssertionError: If the number of columns does not match the number of cells in the given row.
        """
        assert len(data) == len(self.columns), "incorrect number of data columns"

        str_data = [cell if isinstance(cell, str) else str(cell) for cell in data]

        self.rows.append(str_data)
        for i, cell in enumerate(str_data):
            self.columns[i].width = max(self.columns[i].width, len(cell))
        for i, cell in enumerate(data):
            if self.columns[i].row_align == TablePrinter.ALIGN_AUTO:
                if isinstance(cell, int | float) and not isinstance(cell, bool):
                    self.columns[i].row_align = TablePrinter.ALIGN_RIGHT
                else:
                    self.columns[i].row_align = TablePrinter.ALIGN_LEFT

    def add_rows(self, rows: list[list[Any]]):
        """Add new rows to the table printer using `self.add_row` on each given row.

        :param rows: The rows to add.
        """
        for row in rows:
            self.add_row(row)

    def sort_rows(self, columns: list[int] = [0], reverse=False):
        assert len(columns) > 0, "columns cannot be empty"
        for column in columns:
            assert 0 <= column < len(self.columns), "invalid column index"

        self.rows.sort(key=itemgetter(*columns), reverse=reverse)

    def print(self):
        """Print the table using the specified alignment rules. The width of each column is determined by taking the
        maximum of the column name length and longest cell length of that column.
        """
        print(
            " | ".join(
                [
                    f"{column.name:{column.column_align}{column.width}}"
                    for column in self.columns
                ]
            )
        )
        print("-+-".join(["-" * column.width for column in self.columns]))
        for row in self.rows:
            print(
                " | ".join(
                    [
                        f"{cell:{self.columns[i].row_align}{self.columns[i].width}}"
                        for i, cell in enumerate(row)
                    ]
                )
            )
