from __future__ import annotations

import io
import re
from itertools import repeat
from typing import TYPE_CHECKING, Any, cast

import ch5mpy as ch
import numpy as np
import rich.box
from rich.console import Console
from rich.highlighter import RegexHighlighter
from rich.table import Table
from rich.theme import Theme

if TYPE_CHECKING:
    from hdfq.evaluation import EVAL_OBJECT


class H5Highlighter(RegexHighlighter):
    base_style: str = "h5."
    highlights: list[str] = [
        r"(?P<bool_true>True)",
        r"(?P<bool_false>False)",
        r"(?P<builtin>(?<!\w)(object|None|int\d*|float\d*|[><\|][USB]\d+))",
        r"(?P<number>(?<!\w)[+-]?\d+(?:\.\d*)?(?:e(?:[+-](?:\d+)?)?)?…?(?!\w))",
        r"(?P<str>[b]?[\"'].*?[\"'…])",
        r"(?P<identifier>\.[a-zA-Z_]\w*(?=(?:\[.*\])?:))",
        r"(?P<attribute>#[a-zA-Z_]\w*(?=:))",
        r"(?P<value>\.[a-zA-Z_]\w*?(?==))",
    ]


theme = Theme(
    {
        "h5.bool_true": "bold green",
        "h5.bool_false": "bold red",
        "h5.builtin": "orchid",
        "h5.number": "cyan",
        "h5.str": "green",
        "h5.identifier": "bold yellow",
        "h5.attribute": "italic grey70",
        "h5.value": "blue",
    }
)
console = Console(highlighter=H5Highlighter(), theme=theme)


def get_tabs(offset: int) -> str:
    return "  " * offset


def repr_dict(obj: dict[str, Any] | ch.AttributeManager | ch.H5Dict[Any], offset: int) -> str:
    prefix = "." if isinstance(obj, (dict, ch.H5Dict)) else "#"
    tabs = get_tabs(offset)
    return (
        f"{tabs}"
        + f",\n{tabs}".join(map(lambda kv: f"{prefix}{kv[0]}: {repr_object(kv[1], offset=offset)}", obj.items()))
        + ",\n"
    )


def repr_array_1d(obj: ch.H5Array[Any], table: Table) -> None:
    if len(obj) <= 6:
        table.add_row(*map(repr, obj))

    else:
        table.add_row(*map(repr, obj[:3]), "...", *map(repr, obj[-3:]))


def repr_array_2d(obj: ch.H5Array[Any], table: Table) -> None:
    if obj.shape[0] <= 6:
        for row in range(obj.shape[0]):
            repr_array_1d(obj[row], table)

    else:
        n_cols = obj.shape[1]
        repr_array_1d(obj[0], table)
        repr_array_1d(obj[1], table)
        repr_array_1d(obj[2], table)
        table.add_row(*repeat("...", n_cols if n_cols <= 6 else 7))
        repr_array_1d(obj[obj.shape[0] - 3], table)
        repr_array_1d(obj[obj.shape[0] - 2], table)
        repr_array_1d(obj[obj.shape[0] - 1], table)


def repr_object(obj: EVAL_OBJECT, offset: int) -> str:
    if isinstance(obj, (ch.H5Dict, ch.H5List)):
        if len(obj) + len(obj.attributes) == 0:
            return "{}"

        if len(obj.attributes):
            attributes = repr_dict(obj.attributes, offset=offset + 1)
        else:
            attributes = ""

        if len(obj):
            if isinstance(obj, ch.H5List):
                body = repr_dict(obj.to_dict(), offset=offset + 1)
            else:
                body = repr_dict(obj, offset=offset + 1)
        else:
            body = ""

        tabs = get_tabs(offset)

        return f"{{\n{attributes}{body}{tabs}}}"

    elif isinstance(obj, (dict, ch.AttributeManager)):
        if offset > 0:
            tabs = get_tabs(offset)
            return f"{{\n{repr_dict(obj, offset=offset + 1)}{tabs}}}"

        return f"{{\n{repr_dict(obj, offset=offset + 1)}}}"

    elif isinstance(obj, list):
        tabs = get_tabs(offset + 1)
        content_repr = f",\n{tabs}".join(map(repr, obj))
        return f"[\n{tabs}{content_repr}\n]"

    elif isinstance(obj, ch.H5Array):
        if obj.size == 0:
            return "[]"

        if obj.ndim == 0:
            return str(obj)

        table = Table(show_header=False, show_lines=False, box=rich.box.ROUNDED)
        if obj.ndim == 1:
            repr_array_1d(obj, table)

        elif obj.ndim == 2:
            repr_array_2d(obj, table)

        else:
            table.add_row("...")

        tabs = get_tabs(offset)

        table_console = Console(file=io.StringIO(), width=console.width - 1 - len(tabs))
        table_console.print(f".shape={obj.shape}  .dtype={obj.dtype}", table)
        table_repr = cast(str, table_console.file.getvalue()).rstrip()  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
        table_repr = re.sub("\n", f"\n{tabs}", table_repr)

        return table_repr

    elif isinstance(obj, np.void):
        return re.sub(
            r"\.$", "", re.sub(r"\.+", ".", "".join(chr(c) if 32 <= c < 128 else "." for c in bytes(obj)[13:]))
        )

    else:
        return repr(obj)


def display(obj: EVAL_OBJECT) -> None:
    console.print(repr_object(obj, offset=0))


def nice_size_format(size: int) -> str:
    if size < 1e3:
        return f"{size}B"

    elif size < 1e6:
        return f"{size / 1e3:.2f}kB"

    elif size < 1e9:
        return f"{size / 1e6:.2f}MB"

    else:
        return f"{size / 1e9:.2f}GB"
