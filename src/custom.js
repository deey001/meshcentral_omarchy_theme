/* OMARCHY-THEMES-BEGIN */
/*
 * Omarchy themes for MeshCentral (modern UI).
 * Adds the Omarchy palettes to MeshCentral's own "Switch theme" dialog
 * (My Account -> Switch theme) and themes the login page to match.
 *
 * Generated from src/custom.js by build/build.py. Everything between the
 * OMARCHY-THEMES-BEGIN / END markers is managed by the installer; put your own
 * custom.js code outside the markers.
 */
(function () {
  "use strict";
  var THEMES = /*@THEMES@*/[];
  // Theme for browsers that have never picked one, e.g. "tokyo-night". Empty = MeshCentral default.
  var DEFAULT_THEME = "";
  var PREFIX = "omarchy-";

  function find(key) {
    if (typeof key !== "string" || key.indexOf(PREFIX) !== 0) return null;
    var id = key.slice(PREFIX.length);
    for (var i = 0; i < THEMES.length; i++) { if (THEMES[i].id === id) return THEMES[i]; }
    return null;
  }
  function stored() { try { return localStorage.getItem("theme") || ""; } catch (e) { return ""; } }
  function active() { return find(stored()); }

  if (DEFAULT_THEME && !stored() && find(PREFIX + DEFAULT_THEME)) {
    try { localStorage.setItem("theme", PREFIX + DEFAULT_THEME); } catch (e) { }
  }

  function markRoot() {
    var t = active(), html = document.documentElement;
    if (t) { html.setAttribute("data-omarchy", t.id); } else { html.removeAttribute("data-omarchy"); }
  }

  // ------------------------------------------------------------ modern UI (default3)
  if (typeof MeshCentralTheme !== "undefined") {
    // Dark Omarchy palettes force Bootstrap dark mode, like MeshCentral does for Darkly/Cyborg.
    var origIsDark = MeshCentralTheme.isDarkBaseTheme;
    MeshCentralTheme.isDarkBaseTheme = function (theme) {
      var t = find(theme);
      return t ? t.dark : origIsDark(theme);
    };

    // Swap the stylesheet now, before the body paints, to avoid a flash of stock Bootstrap.
    if (active()) { MeshCentralTheme.applyTheme(stored()); }
    markRoot();

    // Light Omarchy palettes stay light even when MeshCentral's night mode is on.
    var html = document.documentElement, fixing = false;
    new MutationObserver(function () {
      if (fixing) return;
      markRoot();
      var t = active();
      if (!t) return;
      var want = t.dark ? "dark" : "light";
      if (html.getAttribute("data-bs-theme") !== want) {
        fixing = true;
        html.setAttribute("data-bs-theme", want);
        if (document.body) { document.body.classList.toggle("night", t.dark); }
        fixing = false;
      }
    }).observe(html, { attributes: true, attributeFilter: ["data-bs-theme"] });

    document.addEventListener("DOMContentLoaded", function () {
      var origShow = window.account_showThemesSwitcher;
      if (typeof origShow !== "function") return;
      window.account_showThemesSwitcher = function () {
        var r = origShow.apply(this, arguments);
        try { addOmarchyOptions(); } catch (e) { }
        return r;
      };
    });
  }

  function addOmarchyOptions() {
    var sel = document.getElementById("theme-switcher");
    if (!sel || sel.querySelector("optgroup[data-omarchy]")) return;
    var current = stored(), seen = {};
    // Friendlier labels for Omarchy entries in the "Recent Themes" group.
    for (var i = 0; i < sel.options.length; i++) {
      var t = find(sel.options[i].value);
      if (t) { sel.options[i].textContent = "Omarchy · " + t.label; seen[sel.options[i].value] = true; }
    }
    var group = document.createElement("optgroup");
    group.label = "Omarchy";
    group.setAttribute("data-omarchy", "1");
    THEMES.forEach(function (t) {
      var key = PREFIX + t.id;
      if (seen[key]) return;
      var o = document.createElement("option");
      o.value = key;
      o.textContent = t.label + (t.dark ? "" : " (light)");
      if (key === current) o.selected = true;
      group.appendChild(o);
    });
    // Put the Omarchy group right after "Recent Themes" so it is easy to find.
    var groups = sel.getElementsByTagName("optgroup");
    var recent = (groups.length > 1) ? groups[0] : null;
    if (recent && recent.nextSibling) { sel.insertBefore(group, recent.nextSibling); } else { sel.appendChild(group); }
  }

  // ------------------------------------------------------------ login page and other pages
  if (typeof MeshCentralTheme === "undefined") {
    var t = active();
    if (t) {
      markRoot();
      ["styles/omarchy/palettes/" + t.id + ".css", "styles/omarchy/login.css"].forEach(function (href) {
        var l = document.createElement("link");
        l.rel = "stylesheet"; l.type = "text/css"; l.href = href;
        l.setAttribute("keeplink", "1");
        document.head.appendChild(l);
      });
    }
  }
})();
/* OMARCHY-THEMES-END */
