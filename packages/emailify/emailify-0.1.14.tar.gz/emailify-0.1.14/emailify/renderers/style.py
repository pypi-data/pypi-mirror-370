import importlib.resources as pkg_resources
from functools import lru_cache, reduce
from pathlib import Path
from typing import Any, Dict, Optional

from pandas.io.parquet import json

import emailify.resources as rsc
from emailify.models import Style, StyleProperty


def merge_styles(*styles: Style) -> Style:
    return reduce(lambda a, b: a.merge(b), filter(None, styles), Style())


@lru_cache
def style_map() -> Dict[str, StyleProperty]:
    resources_path = Path(str(pkg_resources.files(rsc)))
    styles_path = resources_path / "styles.json"
    style_map = json.loads(styles_path.read_text())
    return {style["name"]: StyleProperty.model_validate(style) for style in style_map}


def is_numeric_only(value: Any) -> bool:
    try:
        float(str(value))
        return True
    except ValueError:
        return False


def render_prop(
    prop: str,
    value: Any,
    value_template: str,
) -> str:
    if is_numeric_only(value):
        value = f"{value}px"

    return value_template.format(prop=prop, value=value)


def map_style(
    prop: str,
    value: Any,
    prev_prop: Optional[str] = None,
    template: str = "{prop}:{value};",
    no_value_template: str = "{prop};",
) -> str:
    style_properties = style_map()
    value = str(value)
    if not prev_prop:
        prev_prop = prop

    if prev_prop in style_properties:
        cur = style_properties[prev_prop]
        if value in cur.value_map:
            value = cur.value_map[value]
        prop = cur.display
    prop = prop.replace("_", "-")
    rendered = render_prop(prop, value, template)
    return rendered


def render_style(style: Style) -> str:
    style_dict = style.model_dump(exclude_none=True)
    rendered = ""
    for prop, value in style_dict.items():
        rendered += map_style(prop, value)
    return rendered


@lru_cache
def extra_props() -> Dict[str, Dict[str, str]]:
    resources_path = Path(str(pkg_resources.files(rsc)))
    mjml_path = resources_path / "mjml.json"
    return json.loads(mjml_path.read_text())


def render_extra_props(
    component_name: str, style: Style, extra_dict: Dict[str, Any] = {}
) -> str:
    extra_props_map = extra_props()
    style_dict = style.model_dump(exclude_none=True)
    cur_props = extra_props_map[component_name]
    rendered = ""
    for prop, value in {**style_dict, **extra_dict}.items():
        if prop is None or value is None:
            continue
        if prop in cur_props:
            _cur = cur_props[prop]
            rendered += map_style(
                prop=_cur,
                value=value,
                prev_prop=prop,
                template='{prop}="{value}" ',
            )
    return rendered
