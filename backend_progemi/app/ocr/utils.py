"""Utils functions for OCR processing."""

from __future__ import annotations

import io

import re

from math import sqrt

from itertools import cycle

from typing import Dict, List, Optional, Sequence, Any, Tuple

from app.ocr.schemas import SEP, Cell, LineStyle, TableRow, Table

from azure.ai.documentintelligence.models import (
    DocumentParagraph,
    DocumentStyle,
    DocumentWord,
    DocumentPage,
    DocumentTable,
)


from config.logger_config import logger

ICONS = [
    "-",
    "_",
    "#",
    "•",
    "◦",
    "▪",
    "▫",
    "►",
    "▸",
    "‣",
    "➤",
    "→",
    "⇒",
    "★",
    "☆",
    "✓",
    "✗",
    "■",
    "□",
    "◆",
]

_METRIC = "bbox"

MULT = 10


def _hex_to_rgb(hex_code: str) -> Optional[Tuple[int, int, int]]:
    """'#a1b2c3' -> (161, 178, 195) ; no case sensitivity."""

    hex_code = hex_code.strip().lstrip("#")

    if len(hex_code) != 6:
        return None

    r, g, b = (int(hex_code[i : i + 2], 16) for i in (0, 2, 4))

    return r, g, b


def _rgb_distance(c1: Tuple[int, int, int], c2: Tuple[int, int, int]) -> float:
    """Eclidean distance in RGB space (0-255)."""

    return sqrt(sum((a - b) ** 2 for a, b in zip(c1, c2)))


def _assign_icons(colors: set[str], threshold: float = 10.0) -> dict[str, str]:
    """
    Associate each color in `colors` with an icon from `ICONS` based on its RGB value.
    """

    icon_pool = cycle(ICONS)

    groups: List[Tuple[Tuple[int, int, int], str]] = []

    mapping: Dict[str, str] = {}

    for hex_code in colors:
        rgb = _hex_to_rgb(hex_code)

        if rgb is None:
            continue

        for ref_rgb, icon in groups:
            if _rgb_distance(rgb, ref_rgb) <= threshold:
                mapping[hex_code] = icon

                break
        else:
            icon = next(icon_pool)

            groups.append((rgb, icon))

            mapping[hex_code] = icon

    return mapping


def _round05(x: float) -> float:
    """Round a float to the nearest 0.5."""

    return round(x * 2) / 2


def _decorate(text: str, *, bold: bool, italic: bool) -> str:
    """Add Markdown formatting to the text."""

    if bold:
        text = f"**{text}**"

    if italic:
        text = f"__{text}__"

    return text


def _first_cell_text(
    row: TableRow,
    raw: str,
    icon_map: Dict[str, str] | None = None,
) -> str:
    """Get the first cell text with optional icon and formatting."""

    icon = ""

    if icon_map:
        for st in row.line_styles:
            if st.background_color in icon_map:
                icon = icon_map[st.background_color] + " "

                break

    bold = any(s.is_bold for s in row.line_styles)

    italic = any(s.is_italic for s in row.line_styles)

    return icon + _decorate(raw, bold=bold, italic=italic)


def _assign_h_levels(tables: List[Table]) -> None:
    """
    Assigns a hierarchical level to each row in the tables based on font size.
    """

    rows: List[TableRow] = [r for t in tables for r in t.table_rows]

    for r in rows:
        fs = next((s.font_size for s in r.line_styles if s.font_size), 0.0)

        r._fs_rounded = _round05(fs)

    sizes_desc = sorted({r._fs_rounded for r in rows}, reverse=True)

    size2level = {sz: idx + 1 for idx, sz in enumerate(sizes_desc[:5])}

    for r in rows:
        r.level_h = size2level.get(r._fs_rounded, 5)

    for r in rows:
        del r._fs_rounded


def _poly_height_px(
    polygon: Sequence[float], unit: str, *, dpi: int = 96, method: str = _METRIC
) -> float:
    """Returns the height of the polygon in pixels."""

    ys = polygon[1::2]

    if not ys:
        return 0.0

    if method == "bbox":
        h_raw = max(ys) - min(ys)

    elif method == "mini":
        ys_sorted = sorted(ys)

        if len(ys_sorted) < 2:
            h_raw = 0.0

        else:
            h_raw = ys_sorted[1] - ys_sorted[0]

    else:
        raise ValueError(f"Unknown method: {method}")

    if unit == "pixel":
        return h_raw

    if unit == "inch":
        return h_raw * dpi

    raise ValueError(f"Unknown unit: {unit!r}")


def _intersects(a: Tuple[int, int], b: Tuple[int, int]) -> bool:
    """Do two character intervals overlap?"""

    return not (a[1] <= b[0] or a[0] >= b[1])


def _estimate_row_height_px(
    row: TableRow,
    pages: List[DocumentPage],
    *,
    dpi: int = 96,
) -> float:
    """
    Estimates the height of a row in pixels.
    """

    max_h_px = 0.0

    for cell in row.cells[:1]:
        for page in pages:
            if not page.words:
                continue

            for word in page.words:
                if not word.polygon:
                    continue

                if _intersects(
                    (word.span.offset, word.span.offset + word.span.length),
                    (cell.offset_span, cell.offset_span + cell.span_len),
                ):
                    h_px = _poly_height_px(word.polygon, unit="inch", dpi=dpi)

                    max_h_px = max(max_h_px, h_px)

                    if h_px == max_h_px:
                        cell.polygon = word.polygon

                        cell.word_used_for_size = word.content

                        return max_h_px

    return 0.0


def _to_line_style(s: DocumentStyle) -> LineStyle:
    """Converts a DocumentStyle to a LineStyle."""

    return LineStyle(
        font_size=getattr(s, "font_size", None),
        font_weight=getattr(s, "font_weight", None),
        font_style=getattr(s, "font_style", None)
        or getattr(s, "font_style_name", None),
        color=getattr(s, "color", None) or getattr(s, "font_color", None),
        font_family=getattr(s, "similar_font_family", None)
        or getattr(s, "font_family", None),
        background_color=getattr(s, "backgroundColor", None)
        or getattr(s, "background_color", None),
    )


def _styles_for_row(row: TableRow, styles: List[DocumentStyle]) -> List[LineStyle]:
    """
    Returns a list of LineStyle objects for the given row based on the styles
    that intersect with the cell spans in the row.
    """

    ranges = [(c.offset_span, c.offset_span + c.span_len) for c in row.cells]

    out: List[LineStyle] = []

    for st in styles:
        for sp in st.spans or []:
            span_rng = (sp.offset, sp.offset + sp.length)

            if any(_intersects(span_rng, r) for r in ranges):
                out.append(_to_line_style(st))

                break

    return out


def _first_point_x_pixels(
    polygon: Sequence[float], *, unit: str, dpi: int = 96
) -> Optional[float]:
    """
    Returns the x-coordinate of the first point in the polygon in pixels,
    inches, or millimeters.
    Raises ValueError if the polygon is invalid or the unit is unknown.
    """

    if not polygon or len(polygon) < 2:
        logger.warning("Invalid polygon: %s", polygon)

        return None

    x_raw = min(polygon[::2])

    if unit == "pixel":
        return x_raw

    if unit == "inch":
        return x_raw * dpi

    if unit == "millimeter":
        return x_raw * dpi / 25.4

    logger.warning("Unknown unit: %s", unit)

    return None


def _span_offset(span: Any) -> int:
    """
    Returns the offset of a span.
    If the span is None, returns -1.
    If the span has an 'offset' attribute, returns that.
    If the span is a dictionary, checks for 'offset' or 'span.offset'.
    Raises ValueError if the span is not recognized.
    """

    if span is None:
        return -1

    if hasattr(span, "offset"):
        return span.offset

    if isinstance(span, dict):
        if "offset" in span:
            return span["offset"]

        if "span" in span and "offset" in span["span"]:
            return span["span"]["offset"]

    raise ValueError("Span not recognized: " + str(span))


def _table_col_widths(
    table: Table, col_off: List[float], bg2icon: Dict[str, str] | None
) -> List[int]:
    """
    Returns the widths of each column in the table based on the content and offsets.
    The widths are calculated as the maximum of the content length and the offset
    multiplied by a constant factor (MULT).
    """

    w = [0] * len(col_off)

    for row in table.table_rows:
        for c in row.cells:
            i = c.column_index

            txt = (
                _first_cell_text(row, c.content, icon_map=bg2icon)
                if i == 0
                else c.content
            )

            indent = (
                int(c.offset_px * MULT)
                if i == 0
                else int(max(0, c.offset_px - col_off[i - 1]) * MULT)
            )

            w[i] = max(w[i], indent + len(txt))

    return w


def _find_word_after_span(
    pages: List[DocumentPage],
    offset_min: int,
    target: str,
) -> Optional[DocumentWord]:
    """
    Finds the first word in the pages that matches the target string
    and is located after the specified offset.
    The search is case-insensitive and ignores words before the offset_min.
    If no matching word is found, returns None.
    The target string is converted to lowercase for case-insensitive comparison.
    The function assumes that the pages contain words with spans that have an 'offset' attribute.
    If a page has no words, it is skipped.
    If a word's span offset is less than offset_min, it is skipped.
    If a word's content matches the target string (case-insensitive), that word is returned.
    If no matching word is found after checking all pages, None is returned.
    """

    target = target.lower()

    for page in pages:
        if not page.words:
            continue

        words: List[DocumentWord] = page.words

        words_sorted = sorted(
            words,
            key=lambda w: _span_offset(w.span),
        )

        for w in words_sorted:
            if w.span.offset < offset_min:
                continue

            if w.content.lower() == target:
                return w

    return None


def _first_token(text: str) -> str:
    """
    Returns the first token in the text that contains at least one alphanumeric character.
    """

    for m in re.finditer(r"\S+", text):
        chunk = m.group(0)

        if not any(ch.isalnum() for ch in chunk):
            continue

        start = m.start()

        end = m.end()

        i = end

        while i < len(text) and text[i].isspace():
            i += 1

        if i < len(text) and text[i] in "€$":
            return text[start : i + 1]

        return chunk

    return ""


def _overlaps(start: int, length: int, ranges: List[Tuple[int, int]]) -> bool:
    """
    Checks if the range defined by (start, start + length) overlaps with any of the
    ranges provided in the list of tuples (lo, hi).
    The function returns True if there is an overlap, otherwise False.
    """

    end = start + length

    return any(not (end <= lo or start >= hi) for lo, hi in ranges)


def _rebuilt_tables(
    tables: List[DocumentTable], pages: List[DocumentPage], styles: List[DocumentStyle]
) -> Tuple[List[Table], List[Tuple[int, int]], Dict[str, str]]:
    """Rebuilds tables from the document pages and styles."""

    logger.debug("# FOUNDING TABLES SPANS")

    logger.info("There are %d tables", len(tables))

    tables_rebuilt: List[Table] = []

    ranges: List[Tuple[int, int]] = []

    for table in tables or []:
        table_rebuilt = Table(
            table_rows=[],
            offset_span=table.spans[0].offset if table.spans else 0,
            len_span=table.spans[0].length if table.spans else 0,
        )

        for sp in table.spans:
            ranges.append((sp.offset, sp.offset + sp.length))

        if getattr(table, "spans", None):
            for span in table.spans:
                first_table_word = table.cells[0].content if table.cells else "No cells"

                logger.info(
                    "Table spans: %d - %d [%s]",
                    span.offset,
                    span.offset + span.length,
                    first_table_word,
                )

        logger.info("\t- Nombre lignes: %d", table.row_count)

        logger.info("\t- Nombre colonnes: %d", table.column_count)

        for cell in table.cells:
            if cell.column_index == 0:
                table_row = TableRow(
                    row_index=cell.row_index,
                    cells=[],
                )

                table_rebuilt.table_rows.append(table_row)

            if cell.content:
                first_cell_word_text: str = _first_token(cell.content)

                first_cell_word_object: Optional[DocumentWord] = _find_word_after_span(
                    pages,
                    offset_min=cell.spans[0].offset,
                    target=first_cell_word_text,
                )

                if not first_cell_word_object:
                    logger.info(
                        "\t\t- %d: %s [NONE px] (%s, span %d)",
                        cell.row_index,
                        cell.content,
                        first_cell_word_text,
                        cell.spans[0].offset,
                    )

                    if not cell.bounding_regions:
                        logger.warning(
                            "\t\t\t- No bounding regions for cell %d, row %d",
                            cell.column_index,
                            cell.row_index,
                        )

                        continue

                    first_cell_polygon = cell.bounding_regions[0].polygon

                    first_position_x: Optional[float] = _first_point_x_pixels(
                        first_cell_polygon, unit="pixel", dpi=96
                    )

                    if first_position_x is None:
                        logger.warning(
                            "\t\t\t- No first position X for cell %d, row %d",
                            cell.column_index,
                            cell.row_index,
                        )

                        continue

                    table_rebuilt.table_rows[-1].cells.append(
                        Cell(
                            row_index=cell.row_index,
                            column_index=cell.column_index,
                            content=cell.content,
                            offset_span=cell.spans[0].offset,
                            span_len=cell.spans[0].length,
                            offset_px=first_position_x,
                            polygon=first_cell_polygon,
                        )
                    )

                    continue

                if not first_cell_word_object.polygon:
                    logger.warning(
                        "\t\t- %d: %s [NO POLYGON px] (%s, span %d)",
                        cell.row_index,
                        cell.content,
                        first_cell_word_text,
                        cell.spans[0].offset,
                    )

                    continue

                if not table.cells:
                    logger.warning(
                        "\t\t- %d: %s [NO CELLS px] (%s, span %d)",
                        cell.row_index,
                        cell.content,
                        first_cell_word_text,
                        cell.spans[0].offset,
                    )

                    continue

                first_position_x: Optional[float] = _first_point_x_pixels(
                    first_cell_word_object.polygon, unit="pixel", dpi=96
                )

                if first_position_x is None:
                    logger.warning(
                        "\t\t- %d: %s [NO FIRST POSITION X px] (%s, span %d)",
                        cell.row_index,
                        cell.content,
                        first_cell_word_text,
                        cell.spans[0].offset,
                    )

                    continue

                logger.info(
                    "\t\t- %d: %s [%d px] (%s, span %d)",
                    cell.row_index,
                    cell.content,
                    first_position_x,
                    first_cell_word_text,
                    cell.spans[0].offset,
                )

                if not cell.bounding_regions:
                    logger.warning(
                        "\t\t\t- No bounding regions for cell %d, row %d",
                        cell.column_index,
                        cell.row_index,
                    )

                    continue

                table_rebuilt.table_rows[-1].cells.append(
                    Cell(
                        row_index=cell.row_index,
                        column_index=cell.column_index,
                        content=cell.content,
                        offset_span=cell.spans[0].offset if cell.spans else 0,
                        span_len=cell.spans[0].length if cell.spans else 0,
                        offset_px=first_position_x,
                        polygon=cell.bounding_regions[0].polygon,
                    )
                )

        table_row.line_styles = _styles_for_row(table_row, styles)

        for row in table_rebuilt.table_rows:
            row.line_styles = _styles_for_row(row, styles)

        if table_rebuilt.table_rows:
            tables_rebuilt.append(table_rebuilt)

    for table_rebuilt in tables_rebuilt:
        for row in table_rebuilt.table_rows:
            row_font_pt = _estimate_row_height_px(row=row, pages=pages)

            row.line_styles.append(LineStyle(font_size=row_font_pt))

    all_font_size = set()

    all_bg_color = set()

    all_color = set()

    all_font_family = set()

    all_font_weight = set()

    all_font_style = set()

    for table_rebuilt in tables_rebuilt:
        for row in table_rebuilt.table_rows:
            for cell in row.cells:
                for style in row.line_styles:
                    if style.font_size is not None:
                        all_font_size.add(style.font_size)

                    if style.color is not None:
                        all_color.add(style.color)

                    if style.font_family is not None:
                        all_font_family.add(style.font_family)

                    if style.font_weight is not None:
                        all_font_weight.add(style.font_weight)

                    if style.font_style is not None:
                        all_font_style.add(style.font_style)

                    if style.background_color is not None:
                        all_bg_color.add(style.background_color)

    logger.info("\n# FOUNDING TABLES STYLES\n")

    logger.info("## Font Sizes: %s", all_font_size)

    logger.info("## Background Colors: %s", all_bg_color)

    logger.info("## Text Colors: %s", all_color)

    logger.info("## Font Families: %s", all_font_family)

    logger.info("## Font Weights: %s", all_font_weight)

    logger.info("## Font Styles: %s", all_font_style)

    bg2icon = _assign_icons(all_bg_color, threshold=10.0)

    logger.info("## BG → icon mapping : %s", bg2icon)

    return tables_rebuilt, ranges, bg2icon


def build_document_text(
    paragraphs: List[DocumentParagraph],
    tables: List[DocumentTable],
    pages: List[DocumentPage],
    styles: List[DocumentStyle],
) -> str:
    """
    Builds a unified text representation of the document, including paragraphs and tables.
    The text is formatted with appropriate spacing and alignment for tables.
    Paragraphs are separated by newlines, and tables are formatted with columns aligned.
    Each table row is represented with its cells aligned according to their column indices.
    The function also handles the assignment of hierarchical levels to table rows based on font size.
    It reconstructs tables from the provided data, calculates column widths, and formats the output.
    The output is a string that can be used for further processing or display.
    The function assumes that the input data is well-formed and that the necessary styles
    and spans are provided for the tables and paragraphs.
    """

    tables_built, tbl_ranges, bg2icon = _rebuilt_tables(tables, pages, styles)

    _assign_h_levels(tables_built)

    logger.info("\nDEBUG – First cell text and font sizes in tables\n")

    for t in tables_built:
        for row in t.table_rows:
            fs = next((s.font_size for s in row.line_styles if s.font_size), 0.0)

            first_txt = row.cells[0].content.strip() if row.cells else ""

            logger.info(
                "  h %f | %f pt | %s | polygone %s | word use for size %s",
                row.level_h,
                fs,
                first_txt[:60],
                row.cells[0].polygon if row.cells else "None",
                row.cells[0].word_used_for_size if row.cells else "None",
            )

    logger.info("--- end debug ---\n")

    items: List[Tuple[int, DocumentParagraph | Table]] = []

    for p in paragraphs:
        if p.spans and _overlaps(p.spans[0].offset, p.spans[0].length, tbl_ranges):
            continue

        # items.append((_para_offset(p), p))

    for t in tables_built:
        items.append((t.offset_span, t))

    items.sort(key=lambda x: x[0])

    buf = io.StringIO()

    for _, obj in items:
        if isinstance(obj, DocumentParagraph):
            buf.write(obj.content.strip() + "\n")

        elif isinstance(obj, Table):
            col_off = obj._col_offset_max()

            col_w = _table_col_widths(obj, col_off, bg2icon)

            for row in obj.table_rows:
                parts = [" " * col_w[i] for i in range(len(col_w))]

                for c in row.cells:
                    i = c.column_index

                    indent = (
                        int(c.offset_px * MULT)
                        if i == 0
                        else int(max(0, c.offset_px - col_off[i - 1]) * MULT)
                    )

                    cell_txt = (
                        _first_cell_text(row, c.content, bg2icon)
                        if i == 0
                        else c.content
                    )

                    parts[i] = (" " * indent + cell_txt).ljust(col_w[i])

                buf.write(SEP.join(parts).rstrip() + "\n")

            buf.write("\n")

    return buf.getvalue()
