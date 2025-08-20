var window = globalThis;
var self = globalThis;
var navigator = { userAgent: "quickjs" };
var document = {
    createElement: function () { return { style: {}, appendChild: function () { }, setAttribute: function () { }, innerHTML: "" }; },
    createTextNode: function (t) { return t; },
    getElementsByTagName: function () { return []; },
    querySelector: function () { return null; },
    body: { appendChild: function () { } }
};
if (typeof getComputedStyle === "undefined") { globalThis.getComputedStyle = function () { return {}; }; }
var module = { exports: {} };
var exports = module.exports;
var process = { env: { NODE_ENV: "production" } };
var define = undefined;


