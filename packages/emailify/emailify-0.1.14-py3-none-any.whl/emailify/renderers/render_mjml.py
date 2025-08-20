import json
from functools import lru_cache
from importlib.resources import files

from quickjs import Context


def _read_bundle_text() -> str:
    return (
        files("emailify")
        .joinpath("resources", "js", "mjml-browser.js")
        .read_text(encoding="utf-8")
    )


def _read_js_text(name: str) -> str:
    return (
        files("emailify").joinpath("resources", "js", name).read_text(encoding="utf-8")
    )


def _build_ctx() -> Context:
    ctx = Context()
    ctx.eval(_read_js_text("setup_shim.js"))
    bundle_js = _read_bundle_text()
    ctx.eval(bundle_js)
    ctx.eval(_read_js_text("capture_export.js"))
    return ctx


@lru_cache(maxsize=1)
def _get_ctx() -> Context:
    return _build_ctx()


def mjml2html(
    mjml: str,
    **options,
) -> str:
    template = _read_js_text("call_mjml.js")
    js = template.replace("__MJML__", json.dumps(mjml)).replace(
        "__OPTIONS__", json.dumps(options or {})
    )
    try:
        return _get_ctx().eval(js)
    except Exception as e:
        raise RuntimeError(str(e)) from None
