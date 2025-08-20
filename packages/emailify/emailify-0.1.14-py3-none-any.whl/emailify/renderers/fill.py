from email.mime.application import MIMEApplication

from emailify.models import Fill
from emailify.renderers.core import _render
from emailify.renderers.style import render_extra_props


def render_fill(fill: Fill) -> tuple[str, list[MIMEApplication]]:
    body = _render(
        "fill",
        fill=fill,
        extra_props=render_extra_props("fill", fill.style),
    )
    return body, []
