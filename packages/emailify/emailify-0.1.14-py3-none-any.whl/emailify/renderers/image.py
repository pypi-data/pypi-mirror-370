from email.mime.application import MIMEApplication
from io import BytesIO
from pathlib import Path
from uuid import uuid4

from emailify.models import Image
from emailify.renderers.core import _render
from emailify.renderers.style import merge_styles, render_extra_props
from emailify.styles.image_default import IMAGE_STYLE


def render_image(image: Image) -> tuple[str, list[MIMEApplication]]:
    ext = "jpeg" if image.format in ("jpg", "jpeg") else image.format
    mime = "image/svg+xml" if ext == "svg" else f"image/{ext}"
    content = image.data
    if isinstance(image.data, BytesIO):
        content = image.data.getvalue()
    elif not isinstance(image.data, (bytearray, bytes)):
        content = Path(image.data).read_bytes()
    content_id = f"image-{uuid4().hex}"
    src = f"cid:{content_id}"

    cur_style = merge_styles(IMAGE_STYLE, image.style)
    body = _render(
        "image",
        image=image,
        src=src,
        extra_props=render_extra_props(
            "image", cur_style, {"width": image.width, "height": image.height}
        ),
    )
    attachment = MIMEApplication(content)
    del attachment["Content-Type"]
    attachment.add_header("Content-Type", mime)
    attachment.add_header("Content-ID", f"<{content_id}>")
    attachment.add_header(
        "Content-Disposition", "inline", filename=f"{content_id}.{ext}"
    )
    return body, [attachment]
