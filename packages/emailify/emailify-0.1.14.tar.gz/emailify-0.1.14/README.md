# Emailify

[![codecov](https://codecov.io/gh/choinhet/emailify/graph/badge.svg?token=${CODECOV_TOKEN})](https://codecov.io/gh/choinhet/emailify)

Create beautiful HTML emails with tables, text, images and more. Built on MJML for consistent rendering across all email clients. Images are embedded as proper email attachments with Content-ID references.

## Installation

```bash
pip install emailify
```

## Usage

### Example

```python
import pandas as pd
import emailify as ef

# The render function now returns both HTML and attachments
html, attachments = ef.render(
    ef.Text(
        text="Hello, this is a table with merged headers",
        style=ef.Style(background_color="#cbf4c9", padding_left="5px"),
    ),
    ef.Table(
        data=df,
        merge_equal_headers=True,
        header_style={
            "hello": ef.Style(background_color="#000000", font_color="#ffffff"),
        },
        column_style={
            "hello3": ef.Style(background_color="#0d0d0", bold=True),
        },
        row_style={
            1: ef.Style(background_color="#cbf4c9", bold=True),
        },
    ),
    ef.Fill(style=ef.Style(background_color="#cbf4c9")),
    ef.Image(data=buf, format="png", width="600px"),
)

# html: ready-to-send HTML string
# attachments: list of email.mime.application.MIMEApplication objects for images
```

#### Result

![image.png](static/image.png)


### Basic Table

#### Extra

Tables can also handle nested components.


```python
import pandas as pd
import emailify as ef

df = pd.DataFrame({"Name": ["Alice", "Bob"], "Score": [95, 87]})
table = ef.Table(data=df)
html, attachments = ef.render(table)
# attachments will be empty since tables don't produce attachments
```

### Text and Styling
```python
text = ef.Text(
    text="Hello, this is a styled header",
    style=ef.Style(background_color="#cbf4c9", padding_left="5px")
)
html, attachments = ef.render(text)
```

### Tables with Custom Styles
```python
table = ef.Table(
    data=df,
    header_style={"Name": ef.Style(background_color="#000", font_color="#fff")},
    column_style={"Score": ef.Style(background_color="#f0f0f0", bold=True)},
    row_style={0: ef.Style(background_color="#e6ffe6")}
)
```

### Images and Charts
```python
import io
import matplotlib.pyplot as plt

# Create a chart
buf = io.BytesIO()
plt.plot([1, 2, 3], [2, 4, 1])
plt.savefig(buf, format="png", dpi=150)
plt.close()
buf.seek(0)

# Render with image - note that images produce attachments
image = ef.Image(data=buf, format="png", width="600px")
html, attachments = ef.render(image)

# attachments contains MIMEApplication objects with proper Content-ID headers
# The HTML references images via cid: URLs that match the Content-ID
print(f"Generated {len(attachments)} attachment(s)")
```

## Key Features

- **Responsive Design**: Built on MJML for consistent rendering across Gmail, Outlook, Apple Mail, and other clients
- **Proper Image Attachments**: Images are embedded as email attachments with Content-ID references, not base64 data URIs
- **Rich Components**: Tables, text, images, and fills with extensive styling options
- **Pandas Integration**: Direct DataFrame rendering with customizable styles
- **Type Safety**: Full type hints and Pydantic models for robust development

## Email Integration

The `render()` function returns a tuple of `(html, attachments)`:

- `html`: Ready-to-send HTML string with `cid:` references for images
- `attachments`: List of `MIMEApplication` objects with proper headers for inline display

Use with your email library:
```python
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

html, attachments = ef.render(your_components)

msg = MIMEMultipart('related')
msg.attach(MIMEText(html, 'html'))
for attachment in attachments:
    msg.attach(attachment)
```