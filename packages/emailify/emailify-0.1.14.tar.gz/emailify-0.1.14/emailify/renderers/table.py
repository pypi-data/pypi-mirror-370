import re
from email.mime.application import MIMEApplication
from html.parser import HTMLParser
from io import StringIO
from typing import Any, Dict, List, Optional, Tuple, Union

from PIL import ImageFont

from emailify.models import Component, Fill, Image, Link, Style, Table, Text
from emailify.renderers.core import _render
from emailify.renderers.fill import render_fill
from emailify.renderers.image import render_image
from emailify.renderers.link import render_link
from emailify.renderers.render_mjml import mjml2html
from emailify.renderers.style import merge_styles, render_style
from emailify.renderers.text import render_text
from emailify.styles.table_default import COL_STYLE, HEADER_STYLE

DEFAULT_FONT_FAMILY = "Arial"
DEFAULT_FONT_SIZE = 11

TABLE_RENDER_MAP = {
    Text: render_text,
    Fill: render_fill,
    Image: render_image,
    Link: render_link,
}

EXTRACT_RE = re.compile(r"__BEG__.*?<div\b[^>]*>(.*?)<\/div>.*?__END__", re.DOTALL)


def _render_component(
    component: Component,
) -> tuple[str, list[MIMEApplication]]:
    parts: list[str] = []
    attachments: list[MIMEApplication] = []

    components = [
        Text(text="__BEG__"),
        component,
        Text(text="__END__"),
    ]
    for component in components:
        body, cur_attachments = TABLE_RENDER_MAP[type(component)](component)
        parts.append(body)
        attachments.extend(cur_attachments)

    body_str = _render(
        "index",
        content="".join(parts),
    )
    html = mjml2html(body_str)

    match = EXTRACT_RE.search(html)
    if match:
        html = match.group(1).strip()

    return html, attachments


class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        return self.text.getvalue()


def strip_tags(html: str) -> str:
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def _get_text_size(
    text: str, font_size: Optional[int], font_family: Optional[str]
) -> float:
    text = strip_tags(text)
    size = font_size or DEFAULT_FONT_SIZE
    family = (font_family or DEFAULT_FONT_FAMILY).lower()
    try:
        font = ImageFont.truetype(f"{family}.ttf", size)
    except Exception:
        font = ImageFont.load_default()
    return float(font.getlength(str(text)))


def _compute_header_merge_spans(
    columns: List[str],
) -> Tuple[Dict[int, int], Dict[int, List[int]]]:
    indices_by_header: Dict[str, List[int]] = {}
    for idx, header in enumerate(columns):
        if header not in indices_by_header:
            indices_by_header[header] = [idx]
        else:
            if indices_by_header[header][-1] == idx - 1:
                indices_by_header[header].append(idx)
            else:
                indices_by_header[header] = [idx]

    span_by_start: Dict[int, int] = {}
    contiguous_only: Dict[int, List[int]] = {}
    for header, indices in list(indices_by_header.items()):
        if len(indices) >= 2:
            start = indices[0]
            span = len(indices)
            span_by_start[start] = span
            contiguous_only[start] = indices
    return span_by_start, contiguous_only


def render_style_dict(style_dict: Dict[Union[str, int], Style]) -> Dict[str, str]:
    return {
        c: render_style(cur)
        for c in style_dict.keys()
        if (cur := style_dict.get(c)) is not None
    }


def render_table(table: Table) -> tuple[str, list[MIMEApplication]]:
    extra_attachments = []

    def maybe_render_nested(cell: Any) -> Any:
        if not isinstance(cell, Component):
            return cell
        body, attachments = _render_component(cell)
        extra_attachments.extend(attachments)
        return body

    table.data = table.data.map(maybe_render_nested)

    header_styles: Dict[str, Style] = {}
    col_styles: Dict[str, Style] = {}
    col_widths: Dict[str, int] = {}
    header_spans_by_start: Dict[int, int] = {}
    skip_header_indices: set[int] = set()
    header_wraps: Dict[str, bool] = {}
    body_nowrap_cols: set[str] = set()

    for header in table.data.columns:
        cur_header_style = table.header_style.get(header)
        header_styles[header] = merge_styles(HEADER_STYLE, cur_header_style)

    for col in table.data.columns:
        cur_col_style = table.column_style.get(col)
        if callable(cur_col_style):
            col_styles[col] = merge_styles(COL_STYLE, None)
        else:
            col_styles[col] = merge_styles(COL_STYLE, cur_col_style)

    if table.merge_equal_headers:
        spans_by_start, groups = _compute_header_merge_spans(list(table.data.columns))
        header_spans_by_start = spans_by_start
        for _, indices in groups.items():
            skip_header_indices.update(indices[1:])

    if table.data is not None and table.data.shape[1] > 0:
        max_cap = table.max_col_width if table.max_col_width is not None else 10**9
        for col_idx, col_name in enumerate(table.data.columns):
            set_width = table.column_widths.get(col_name)
            if set_width is not None:
                col_widths[col_name] = int(set_width)
                continue
            series = table.data.iloc[:, col_idx]
            cur_skip = col_idx in skip_header_indices
            cur_header_style = header_styles.get(col_name)

            header_font_size = cur_header_style.font_size
            header_font_family = cur_header_style.font_family
            header_px = _get_text_size(col_name, header_font_size, header_font_family)

            header_longest_word_px = 0.0
            for word in filter(None, re.split(r"[\s/()_-]+", str(col_name))):
                header_longest_word_px = max(
                    header_longest_word_px,
                    _get_text_size(word, header_font_size, header_font_family),
                )

            cur_col_style = col_styles.get(col_name)
            col_font_size = cur_col_style.font_size
            col_font_family = cur_col_style.font_family

            body_max_px = float(
                series.astype(str)
                .map(lambda it: _get_text_size(it, col_font_size, col_font_family))
                .max()
            )

            small_body_threshold = 90.0
            wrap_factor = 1.6

            should_wrap_header = (
                header_px > max(body_max_px, 40.0) * wrap_factor
                and body_max_px <= small_body_threshold
            ) and not cur_skip

            header_wraps[col_name] = should_wrap_header

            base_px = max(body_max_px, 10.0) + (table.auto_width_padding or 0)
            if should_wrap_header:
                base_px = max(
                    base_px, header_longest_word_px + (table.auto_width_padding or 0)
                )
            else:
                base_px = max(base_px, header_px + (table.auto_width_padding or 0))

            est_px = int(min(base_px, max_cap))
            est_px = min(est_px, max_cap)
            col_widths[col_name] = int(est_px)

            sample = series.astype(str).head(400)
            digit_count = int(sum(ch.isdigit() for s in sample for ch in s))
            alnum_count = int(sum(ch.isalnum() for s in sample for ch in s))
            if alnum_count > 0 and digit_count / alnum_count >= 0.5:
                body_nowrap_cols.add(col_name)

    cell_styles_render: Dict[int, Dict[int, str]] = {}
    for col_idx, col_name in enumerate(table.data.columns):
        maybe_callable = table.column_style.get(col_name)
        if not callable(maybe_callable):
            continue
        num_rows = table.data.shape[0]
        for row_pos in range(num_rows):
            value = table.data.iat[row_pos, col_idx]
            style_obj = maybe_callable(value)
            if style_obj is None:
                continue
            if row_pos not in cell_styles_render:
                cell_styles_render[row_pos] = {}
            cell_styles_render[row_pos][col_idx] = render_style(style_obj)

    headers_render: List[Dict[str, object]] = []
    for idx, header in enumerate(table.data.columns):
        if idx in skip_header_indices:
            continue
        span = header_spans_by_start.get(idx, 1)
        span_width = 0
        for j in range(idx, idx + span):
            name = table.data.columns[j]
            span_width += col_widths.get(name, 0)

        headers_render.append(
            {
                "text": header,
                "span": span,
                "width": span_width,
                "wrap": header_wraps.get(header, False),
            }
        )

    body = _render(
        "table",
        table=table,
        header_styles=render_style_dict(header_styles),
        col_styles=render_style_dict(col_styles),
        row_styles=render_style_dict(table.row_style),
        body_style=render_style(table.body_style),
        col_widths=col_widths,
        headers_render=headers_render,
        body_nowrap_cols=body_nowrap_cols,
        cell_styles=cell_styles_render,
    )
    return body, extra_attachments
