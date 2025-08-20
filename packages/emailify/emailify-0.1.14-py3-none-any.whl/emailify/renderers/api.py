from email.mime.application import MIMEApplication

from emailify.models import Component
from emailify.renderers.core import _render
from emailify.renderers.render import render_component
from emailify.renderers.render_mjml import mjml2html


def render(
    *components: Component,
) -> tuple[str, list[MIMEApplication]]:
    parts: list[str] = []
    attachments: list[MIMEApplication] = []
    for component in components:
        body, cur_attachments = render_component(component)
        parts.append(body)
        attachments.extend(cur_attachments)
    body_str = _render(
        "index",
        content="".join(parts),
    )
    html = mjml2html(body_str)
    return html, attachments
