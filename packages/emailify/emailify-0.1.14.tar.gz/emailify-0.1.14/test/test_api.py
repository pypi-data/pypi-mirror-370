import io
import shutil
from pathlib import Path

import pandas as pd
import pytest
from PIL import Image as PILImage

import emailify as ef
from emailify.renderers.render_mjml import mjml2html


def test_api():
    buf = io.BytesIO()
    # Create a simple 10x10 red image using Pillow
    pil_img = PILImage.new("RGB", (10, 10), color=(255, 0, 0))
    pil_img.save(buf, format="PNG")
    temp_path = Path("temp")
    temp_path.mkdir(exist_ok=True)
    img = temp_path / "image.png"
    pil_img.save(img, format="PNG")
    buf.seek(0)

    df = pd.DataFrame(
        {
            "hello2": [1, 2, 3],
            "hello": [
                "My",
                ef.Link(text="Google", href="https://www.google.com"),
                "Is",
            ],
            "hello3": ["My", "Name", "Is"],
            "Really long column name": [1, 2, 3],
            "hello4": ["This is a long column name"] * 3,
        }
    )
    df.rename(columns={"hello2": "hello"}, inplace=True)
    sec_df = df.rename(columns={"hello4": "hello"})
    html, attachments = ef.render(
        ef.Text(
            text="Hello, this is a table with merged headers",
            style=ef.Style(background_color="#cbf4c9", padding_left="5"),
        ),
        ef.Link(text="Hello", href="https://www.google.com"),
        ef.Link(text="Hello", href="www.google.com"),
        ef.Table(
            data=df,
            merge_equal_headers=True,
            header_style={
                "hello": ef.Style(
                    background_color="#000000",
                    font_color="#ffffff",
                ),
                "hello3": ef.Style(
                    font_family="unknown",
                ),
            },
            column_style={
                "hello3": ef.Style(background_color="#0d0d0", bold=True),
            },
            row_style={
                1: ef.Style(background_color="#cbf4c9", bold=True),
            },
            column_widths={
                "hello": 100,
            },
        ),
        ef.Fill(style=ef.Style(background_color="#cbf4c9")),
        ef.Image(data=img, format="png", width="600px"),
        ef.Image(data=buf, format="png", width="600px"),
        ef.Table(data=df).with_stripes(),
        ef.Table(
            data=sec_df,
            column_style={
                "hello": lambda x: (
                    ef.Style(background_color="#000000", font_color="#ffffff")
                    if x == "My"
                    else None
                ),
            },
        ),
    )
    shutil.rmtree(temp_path, ignore_errors=True)
    assert html is not None
    # Two images added above should yield two attachments
    assert len(attachments) == 2


def test_invalid_mjml():
    with pytest.raises(RuntimeError):
        mjml2html("invalid")


if __name__ == "__main__":
    pytest.main([__file__])
