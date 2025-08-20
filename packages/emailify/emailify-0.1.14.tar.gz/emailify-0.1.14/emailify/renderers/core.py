import importlib.resources as pkg_resources
from functools import lru_cache
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

import emailify.resources as rsc


@lru_cache
def get_env() -> Environment:
    resources_path = Path(str(pkg_resources.files(rsc)))
    templates_path = resources_path / "templates"
    return Environment(
        loader=FileSystemLoader(templates_path),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def _render(template_name: str, **context) -> str:
    template_name = f"{Path(template_name).stem}.mjml"
    env = get_env()
    return env.get_template(template_name).render(**context)
