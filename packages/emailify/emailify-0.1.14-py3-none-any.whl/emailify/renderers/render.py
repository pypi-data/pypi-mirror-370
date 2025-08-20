from email.mime.application import MIMEApplication

from emailify.models import Component, Fill, Image, Link, Table, Text
from emailify.renderers.fill import render_fill
from emailify.renderers.image import render_image
from emailify.renderers.link import render_link
from emailify.renderers.table import render_table
from emailify.renderers.text import render_text

RENDER_MAP = {
    Table: render_table,
    Text: render_text,
    Fill: render_fill,
    Image: render_image,
    Link: render_link,
}


def render_component(
    component: Component,
) -> tuple[str, list[MIMEApplication]]:
    return RENDER_MAP[type(component)](component)
