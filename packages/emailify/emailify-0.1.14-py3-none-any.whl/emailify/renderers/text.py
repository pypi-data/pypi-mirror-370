from email.mime.application import MIMEApplication

from emailify.models import Text
from emailify.renderers.core import _render
from emailify.renderers.style import render_extra_props


def render_text(text: Text) -> tuple[str, list[MIMEApplication]]:
    body = _render(
        "text",
        text=text,
        extra_props=render_extra_props("text", text.style),
    )
    return body, []
