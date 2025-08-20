(function () {
    var exp = (module && module.exports) ? module.exports : undefined;
    if (exp && exp.default && typeof exp.default === "function") {
        exp = exp.default;
    }
    if (!exp && typeof window.mjml2html === "function") {
        exp = window.mjml2html;
    }
    if (!exp) { throw new Error("mjml2html export not found"); }
    globalThis.__mjml2html = exp;
})();


