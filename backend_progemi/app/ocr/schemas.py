"""Schemas for OCR processing and table representation."""

from typing import List, Optional, Sequence

from pydantic import BaseModel


MULT = 10

SEP = " | "


class LineStyle(BaseModel):
    """Line style properties for text in a table cell."""

    font_weight: Optional[str] = None

    font_style: Optional[str] = None

    font_size: Optional[float] = None

    color: Optional[str] = None

    font_family: Optional[str] = None

    background_color: Optional[str] = None

    @property
    def is_bold(self) -> bool:
        """Check if the font weight indicates bold text."""

        return (self.font_weight or "").lower() == "bold"

    @property
    def is_italic(self) -> bool:
        """Check if the font style indicates italic text."""

        return (self.font_style or "").lower() == "italic"


class Cell(BaseModel):
    """Cell of a table with its properties."""

    row_index: int

    column_index: int

    content: str

    offset_px: float

    offset_span: int

    span_len: int

    polygon: Sequence[float]

    word_used_for_size: Optional[str] = None


class TableRow(BaseModel):
    """Row of a table containing multiple cells."""

    row_index: int

    cells: List[Cell]

    level_h: int = 5

    line_styles: List[LineStyle] = []


class Table(BaseModel):
    """Table representation with rows and columns."""

    offset_span: int

    len_span: int

    table_rows: List[TableRow]

    def _col_offset_max(self) -> List[float]:
        """Calculate the maximum offset for each column."""

        mx: List[float] = []

        for row in self.table_rows:
            for c in row.cells:
                i = c.column_index

                if i >= len(mx):
                    mx.append(c.offset_px)

                else:
                    mx[i] = max(mx[i], c.offset_px)
        return mx

    def _col_width(self, col_offset_max: List[float]) -> List[int]:
        """Calculate the width of each column based on offsets and content length."""

        w: List[int] = [0] * len(col_offset_max)

        for row in self.table_rows:
            for c in row.cells:
                i = c.column_index

                if i == 0:
                    indent = int(c.offset_px * MULT)
                else:
                    indent = int(max(0, (c.offset_px - col_offset_max[i - 1])) * MULT)

                w[i] = max(w[i], indent + len(c.content))

        return w

    def print_table(self) -> None:
        """Print the table in a formatted way."""

        col_off = self._col_offset_max()

        col_w = self._col_width(col_off)

        for row in self.table_rows:
            parts = [" " * col_w[i] for i in range(len(col_w))]

            for c in row.cells:
                i = c.column_index

                if i == 0:
                    indent = int(c.offset_px * MULT)

                else:
                    indent = int(max(0, (c.offset_px - col_off[i - 1])) * MULT)

                cell_txt = (" " * indent + c.content).ljust(col_w[i])

                parts[i] = cell_txt

            print(SEP.join(parts).rstrip())
