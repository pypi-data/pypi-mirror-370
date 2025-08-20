(function () {
    var fn = globalThis.__mjml2html;
    if (typeof fn !== "function") throw new Error("mjml2html not found");
    var out = fn(__MJML__, __OPTIONS__);
    if (out && out.errors && out.errors.length) {
        throw new Error("MJML errors: " + JSON.stringify(out.errors));
    }
    return out.html;
})();


