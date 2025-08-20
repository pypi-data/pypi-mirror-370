from email.mime.application import MIMEApplication
from urllib.parse import urlparse

from emailify.models import Link
from emailify.renderers.core import _render
from emailify.renderers.style import render_extra_props


def render_link(link: Link) -> tuple[str, list[MIMEApplication]]:
    parsed_url = urlparse(link.href)
    if parsed_url.scheme == "":
        link.href = f"https://{link.href}"

    body = _render(
        "link",
        link=link,
        extra_props=render_extra_props("link", link.style),
    )
    return body, []
