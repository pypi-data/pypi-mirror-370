from .types import StrsType, LIST_TYPES
from .maths import chars_len
from .fills import add_fills
from .colors import colored

from typing import Literal

HEAD_COLOR = "light_cyan"
CELL_COLOR = "light_blue"
SEPR_COLOR = "dark_grey"
VERT_COLOR = "dark_grey"

SEPR = "-"
CSEPR = colored(SEPR, SEPR_COLOR)
VERT = "|"
CVERT = colored(VERT, VERT_COLOR)
WERT = f" | "


def is_listable(val) -> bool:
    return isinstance(val, LIST_TYPES)


def norm_any_to_str_list(val) -> list[str]:
    if is_listable(val):
        return [str(v) for v in val]
    else:
        return [str(val)]


def norm_any_to_type_list(val) -> list[str]:
    if is_listable(val):
        return [type(v).__name__ for v in val]
    else:
        return [type(val).__name__]


def add_bounds(line: str, is_colored: bool = False) -> str:
    if not is_colored:
        return f"{VERT} {line} {VERT}"
    else:
        return f"{CVERT} {line} {CVERT}"


def align_to_fill_side(align: str) -> Literal["left", "right", "both"]:
    if align[0].lower() == "l":
        return "right"
    elif align[0].lower() == "r":
        return "left"
    else:
        return "both"


def dict_to_table_str(
    d: dict,
    key_headers: StrsType = None,
    val_headers: StrsType = None,
    capitalize_headers: bool = True,
    aligns: StrsType = None,
    default_align: Literal["left", "right"] = "right",
    is_colored: bool = False,
) -> str:
    if not d:
        return ""

    if not key_headers or not val_headers:
        k1, v1 = next(iter(d.items()))
        if not key_headers:
            key_headers = norm_any_to_str_list(k1)
        if not val_headers:
            val_headers = norm_any_to_str_list(v1)

    table_headers: list[str] = key_headers + val_headers
    if capitalize_headers:
        table_headers = [h.capitalize() for h in table_headers]

    table_rows: list[list[str]] = []
    for key, val in d.items():
        key_strs = norm_any_to_str_list(key)
        val_strs = norm_any_to_str_list(val)
        row = key_strs + val_strs
        table_rows.append(row)

    cols = len(table_headers)

    col_widths = [
        max(
            chars_len(row[i]) if i < len(row) else 0
            for row in table_rows + [table_headers]
        )
        for i in range(cols)
    ]

    sep_lines = [SEPR * col_widths[i] for i in range(cols)]
    wert = WERT

    if is_colored:
        table_headers = [colored(h, HEAD_COLOR) for h in table_headers]
        table_rows = [[colored(cell, CELL_COLOR) for cell in row] for row in table_rows]
        sep_lines = [colored(s, SEPR_COLOR) for s in sep_lines]
        wert = colored(WERT, VERT_COLOR)

    if not aligns:
        aligns = [default_align] * cols
    if len(aligns) < cols:
        aligns += [default_align] * (cols - len(aligns))

    header_line_str = wert.join(
        add_fills(
            text=table_headers[i],
            filler=" ",
            fill_side=align_to_fill_side(aligns[i]),
            is_text_colored=is_colored,
            total_width=col_widths[i],
        )
        for i in range(cols)
    )
    header_line_str = add_bounds(header_line_str, is_colored=is_colored)

    sep_line_str = wert.join(sep_lines)
    sep_line_str = add_bounds(sep_line_str, is_colored=is_colored)

    rows_lines = []
    for row in table_rows:
        row_line = wert.join(
            add_fills(
                text=row[i],
                filler=" ",
                fill_side=align_to_fill_side(aligns[i]),
                is_text_colored=is_colored,
                total_width=col_widths[i],
            )
            for i in range(cols)
        )
        row_line = add_bounds(row_line, is_colored=is_colored)
        rows_lines.append(row_line)
    row_lines_str = "\n".join(rows_lines)

    table_str = f"{header_line_str}\n{sep_line_str}\n{row_lines_str}"
    return table_str
