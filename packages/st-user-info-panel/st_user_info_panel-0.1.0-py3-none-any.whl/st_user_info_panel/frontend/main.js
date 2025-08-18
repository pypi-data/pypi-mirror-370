/* st_user_sidebar_panel/frontend/main.js */
/* eslint-disable no-var */
(function () {
  // =========================
  // Styles
  // =========================
  var STYLES = `
.stusp-root{position:fixed;z-index:2147483000;left:0;width:280px;bottom:16px;pointer-events:none}
.stusp-root-inside{position:sticky;bottom:0;z-index:1;width:100%;pointer-events:auto}
.stusp-panel{pointer-events:auto;border:1px solid var(--stusp-border,#e5e7eb);border-radius:var(--stusp-radius,12px);background:var(--stusp-bg,#fff);box-shadow:0 4px 12px rgba(0,0,0,.15);overflow:hidden;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Ubuntu,'Helvetica Neue',Arial,'Noto Sans',sans-serif;max-height:70vh}
.stusp-header{display:flex;align-items:center;gap:12px;padding:12px 14px;cursor:pointer}
.stusp-header:hover{background:rgba(0,0,0,.04)}
.stusp-avatar{width:40px;height:40px;border-radius:50%;display:grid;place-items:center;color:#fff;font-weight:700;font-size:16px;flex-shrink:0}
.stusp-text{flex:1;min-width:0}
.stusp-name{font-weight:600;font-size:14px;color:var(--stusp-fg,#111827);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.stusp-title{font-size:12px;color:var(--stusp-dim,#6b7280);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.stusp-arrow{color:#9ca3af;font-size:12px;margin-left:4px;transform:rotate(180deg);transition:transform .2s}
.stusp-arrow.collapsed{transform:rotate(0)}
.stusp-expanded{padding:16px}
.stusp-divider{height:1px;background:var(--stusp-divider,#f0f0f0);margin:12px 0;border:0}

/* Info card */
.stusp-info{background:var(--stusp-card,#f8f9fa);border-radius:10px;padding:10px 12px;margin-top:6px}
.stusp-info-row{display:grid;grid-template-columns:110px 1fr;align-items:start;gap:8px;padding:6px 0}
.stusp-info-row+.stusp-info-row{border-top:1px dashed var(--stusp-divider,#e5e7eb)}
.stusp-info-label{font-size:11px;color:var(--stusp-dim,#6b7280);text-transform:uppercase;letter-spacing:.02em}
.stusp-info-value{font-size:13px;font-weight:600;color:var(--stusp-fg,#111827);line-height:1.35;overflow-wrap:anywhere;word-break:break-word}

/* Stats - cards */
.stusp-stat{background:var(--stusp-card,#f8f9fa);border-radius:10px;padding:12px;margin-top:12px}
.stusp-stat-label{font-size:12px;color:var(--stusp-dim,#6b7280);margin-bottom:8px;font-weight:600;text-transform:uppercase;letter-spacing:.02em}
.stusp-stat-value{font-size:16px;font-weight:700;color:var(--stusp-fg,#111827);margin-bottom:8px}
.stusp-progress{height:6px;width:100%;background:#e5e7eb;border-radius:3px;overflow:hidden}
.stusp-progress>div{height:100%;width:0%;transition:width .3s;background:var(--stusp-bar,#9ca3af)}

/* Stats - rows (compact) */
.stusp-kpis{background:var(--stusp-card,#f8f9fa);border-radius:10px;padding:8px 10px;margin-top:10px}
.stusp-kpi{display:grid;grid-template-columns:1fr auto;gap:8px;align-items:center;padding:6px 0}
.stusp-kpi+.stusp-kpi{border-top:1px dashed var(--stusp-divider,#e5e7eb)}
.stusp-kpi-label{font-size:11px;color:var(--stusp-dim,#6b7280);text-transform:uppercase;letter-spacing:.02em}
.stusp-kpi-value{font-size:14px;font-weight:700;color:var(--stusp-fg,#111827)}
.stusp-kpi-bar{height:4px;background:#e5e7eb;border-radius:2px;overflow:hidden;grid-column:1/-1}
.stusp-kpi-bar>div{height:100%;width:0;background:var(--stusp-bar,#9ca3af)}

/* Actions */
.stusp-actions{display:grid;grid-template-columns:1fr;gap:8px;margin-top:14px;padding-top:10px;border-top:1px solid var(--stusp-divider,#f0f0f0)}
.stusp-btn{border:0;border-radius:8px;padding:12px;font-size:14px;font-weight:700;cursor:pointer}
.stusp-btn.logout{background:#ef4444;color:#fff}
.stusp-btn.logout:hover{background:#dc2626}

/* Compact mode */
.stusp-compact .stusp-header{padding:8px 10px}
.stusp-compact .stusp-avatar{width:32px;height:32px;font-size:14px}
.stusp-compact .stusp-name{font-size:13px}
.stusp-compact .stusp-title{font-size:11px}
.stusp-compact .stusp-expanded{padding:10px}
.stusp-compact .stusp-info{padding:8px 10px}
.stusp-compact .stusp-info-row{grid-template-columns:96px 1fr;padding:4px 0}
.stusp-compact .stusp-kpis{padding:8px 10px}
.stusp-compact .stusp-kpi{padding:4px 0}
.stusp-compact .stusp-kpi-value{font-size:13px}
.stusp-compact .stusp-stat{padding:10px;margin-top:10px}
.stusp-compact .stusp-stat-value{font-size:14px}
.stusp-compact .stusp-actions{margin-top:10px}

/* Collapsed chip */
.stusp-chip{
  position:fixed; left:16px; bottom:16px; width:40px; height:40px;
  border-radius:9999px; display:none; place-items:center;
  color:#fff; font-weight:800; font-size:14px; user-select:none;
  background:#4CAF50; box-shadow:0 4px 10px rgba(0,0,0,.22);
  z-index:2147483640; cursor:pointer;
  transition: transform .12s ease, opacity .12s ease;
}
.stusp-chip:hover{ transform: translateY(-1px); }
.stusp-chip:active{ transform: translateY(0); }

/* tiny sidebars */
@media (max-width:260px){.stusp-info-row{grid-template-columns:1fr;gap:4px}.stusp-info-label{margin-bottom:2px}}

@media (prefers-color-scheme:dark){
  .stusp-panel{--stusp-bg:#1f2937;--stusp-border:#374151}
  .stusp-name{--stusp-fg:#f9fafb}
  .stusp-title,.stusp-info-label,.stusp-stat-label,.stusp-kpi-label{--stusp-dim:#d1d5db}
  .stusp-info-value,.stusp-stat-value,.stusp-kpi-value{--stusp-fg:#f9fafb}
}
`;

  // =========================
  // Streamlit shim
  // =========================
  function sendMessageToStreamlitClient(type, data) {
    var out = Object.assign({ isStreamlitMessage: true, type: type }, data);
    window.parent.postMessage(out, "*");
  }
  var Streamlit = {
    setComponentReady: function () { sendMessageToStreamlitClient("streamlit:componentReady", { apiVersion: 1 }); },
    setFrameHeight: function (h) { sendMessageToStreamlitClient("streamlit:setFrameHeight", { height: h }); },
    setComponentValue: function (v) { sendMessageToStreamlitClient("streamlit:setComponentValue", { value: v }); },
    RENDER_EVENT: "streamlit:render",
    events: {
      addEventListener: function (type, cb) {
        window.addEventListener("message", function (e) {
          if (e.data.type === type) { e.detail = e.data; cb(e); }
        });
      }
    }
  };

  // =========================
  // State
  // =========================
  var portalRoot = null, wrapperEl = null, chipEl = null;
  var cleanupObservers = [];
  var expanded = false, hasMounted = false;
  var instKey = "st_user_sidebar_panel_default";
  var currentPad = 12, currentBottom = 16, attachModeVal = "portal";
  var avatarColor = "#4CAF50", initials = "U";
  var intervalId = 0, trackRafId = 0;
  var SHOW_THRESHOLD = 120; // px: only show portal when >= this width

  // =========================
  // Utils
  // =========================
  function safeParentDoc() { try { return window.parent.document; } catch (_) { return null; } }
  function getSidebarEl(doc) {
    return (
      doc.querySelector('[data-testid="stSidebar"]') ||
      doc.querySelector('aside[data-testid="stSidebar"]') ||
      doc.querySelector('section[data-testid="stSidebar"]') ||
      doc.querySelector('div[data-testid="stSidebar"]') ||
      doc.querySelector('[aria-label="Main sidebar"]') ||
      doc.querySelector('[aria-label="Sidebar"]')
    );
  }
  function ensureStylesInParent(doc) {
    if (!doc.getElementById("stusp-styles")) {
      var s = doc.createElement("style"); s.id = "stusp-styles"; s.textContent = STYLES; doc.head.appendChild(s);
    }
  }
  function sweepOrphans(doc, key) {
    if (!doc) return;
    doc.querySelectorAll('[data-stusp-inst="' + key + '"]').forEach(function (n) { try { n.remove(); } catch (_) {} });
    doc.querySelectorAll('[data-stusp-chip="' + key + '"]').forEach(function (n) { try { n.remove(); } catch (_) {} });
  }
  function findSidebarToggleButton(doc) {
    return (
      doc.querySelector('[data-testid="stSidebarCollapseButton"]') ||
      doc.querySelector('button[aria-label*="sidebar" i]') ||
      doc.querySelector('button[title*="sidebar" i]') || null
    );
  }
  function initialsOf(name) {
    if (!name) return "U";
    var w = name.trim().split(/\s+/);
    return (w.length === 1 ? w[0][0] : w[0][0] + w[w.length - 1][0]).toUpperCase();
  }
  function fmtInt(n) { try { return Number(n || 0).toLocaleString(); } catch (_) { return String(n); } }
  function fmtUSD(n) { try { return Number(n || 0).toLocaleString(undefined, { style: "currency", currency: "USD" }); } catch (_) { return "$" + String(n); } }

  // =========================
  // Geometry tracking loops
  // =========================
  function positionToSidebar(doc, bottomOffset, sidePad) {
    if (!portalRoot) return;
    var sb = getSidebarEl(doc); if (!sb) return;

    // Force layout read to avoid stale geom on some browsers
    // eslint-disable-next-line no-unused-vars
    var _ = sb.offsetWidth; // touch layout; pairs with next read
    var rect = sb.getBoundingClientRect();
    var pad = Number(sidePad || 0);

    var isCollapsed = rect.width < 1 || rect.right <= 0;
    var belowThreshold = rect.width < SHOW_THRESHOLD;

    // manage chip position
    if (attachModeVal === "portal" && chipEl) {
      chipEl.style.left = Math.max(12, rect.left + 12) + "px";
      chipEl.style.bottom = (bottomOffset || 16) + "px";
      chipEl.style.background = avatarColor;
    }

    if (isCollapsed || belowThreshold) {
      if (portalRoot) portalRoot.style.display = "none";
      if (attachModeVal === "portal" && chipEl) chipEl.style.display = "grid";
      return;
    }

    // show portal
    if (attachModeVal === "portal" && chipEl) chipEl.style.display = "none";
    if (portalRoot.style.display === "none") portalRoot.style.display = "block";

    portalRoot.style.left = (rect.left + pad) + "px";
    portalRoot.style.width = Math.max(0, rect.width - pad * 2) + "px";
    portalRoot.style.bottom = (bottomOffset || 16) + "px";
    portalRoot.style.willChange = "left, width";
  }

  // rAF monitor: run until geom stable or timeout
  function startGeometryMonitor(doc, bottomOffset, sidePad, maxMs) {
    var sb = getSidebarEl(doc); if (!sb) return;
    var deadline = performance.now() + (maxMs || 2000);
    var last = { left: 0, width: 0 }; var stableFrames = 0;

    if (trackRafId) cancelAnimationFrame(trackRafId);
    function step() {
      positionToSidebar(doc, bottomOffset, sidePad);
      var rect = sb.getBoundingClientRect();
      var dl = Math.abs(rect.left - last.left), dw = Math.abs(rect.width - last.width);
      if (dl <= 0.5 && dw <= 0.5) stableFrames++; else stableFrames = 0;
      last.left = rect.left; last.width = rect.width;

      if (stableFrames >= 8 || performance.now() > deadline) {
        trackRafId = 0;
        positionToSidebar(doc, bottomOffset, sidePad); // final snap
        return;
      }
      trackRafId = requestAnimationFrame(step);
    }
    trackRafId = requestAnimationFrame(step);
  }

  // Interval fallback: fire every 32ms for N ms
  function startForceLoop(doc, bottomOffset, sidePad, ms) {
    if (intervalId) { clearInterval(intervalId); intervalId = 0; }
    var endAt = Date.now() + (ms || 2000);
    intervalId = setInterval(function () {
      positionToSidebar(doc, bottomOffset, sidePad);
      if (Date.now() > endAt) { clearInterval(intervalId); intervalId = 0; }
    }, 32);
    cleanupObservers.push(function(){ if (intervalId) { clearInterval(intervalId); intervalId = 0; } });
  }

  function attachObservers(doc, bottomOffset, sidePad) {
    var sb = getSidebarEl(doc); if (!sb || !portalRoot) return;

    var rafId = 0;
    var onAny = function () {
      if (rafId) cancelAnimationFrame(rafId);
      rafId = requestAnimationFrame(function () {
        positionToSidebar(doc, bottomOffset, sidePad);
        rafId = 0;
      });
    };

    // window resize
    doc.defaultView.addEventListener("resize", onAny);

    // universal scroll / wheel / touchmove
    ["scroll","wheel","touchmove"].forEach(function(evt){
      doc.addEventListener(evt, onAny, true);
      try { sb.addEventListener(evt, onAny, { capture: true, passive: true }); }
      catch (_) { sb.addEventListener(evt, onAny, true); }
    });

    // size & attribute changes on sidebar
    var ro = new ResizeObserver(function () {
      onAny(); startGeometryMonitor(doc, bottomOffset, sidePad, 2000); startForceLoop(doc, bottomOffset, sidePad, 1200);
    });
    ro.observe(sb);

    var mo = new MutationObserver(function () {
      onAny(); startGeometryMonitor(doc, bottomOffset, sidePad, 2000); startForceLoop(doc, bottomOffset, sidePad, 1200);
    });
    mo.observe(sb, { attributes: true, attributeFilter: ["style", "class"] });

    // listen transition/animation on document (capture) & only react if target inside sidebar
    var onDocTrans = function (e) {
      if (!sb) return;
      if (sb === e.target || sb.contains(e.target)) {
        startGeometryMonitor(doc, bottomOffset, sidePad, 2000);
        startForceLoop(doc, bottomOffset, sidePad, 1200);
      }
    };
    ["transitionrun","transitionstart","animationstart"].forEach(function(evt){ doc.addEventListener(evt, onDocTrans, true); });
    ["transitionend","animationend"].forEach(function(evt){ doc.addEventListener(evt, onAny, true); });

    // cleanup
    cleanupObservers.push(function () {
      doc.defaultView.removeEventListener("resize", onAny);
      ["scroll","wheel","touchmove"].forEach(function(evt){
        doc.removeEventListener(evt, onAny, true);
        try { sb.removeEventListener(evt, onAny, { capture: true }); }
        catch (_) { sb.removeEventListener(evt, onAny, true); }
      });
      if (rafId) cancelAnimationFrame(rafId);
      if (trackRafId) cancelAnimationFrame(trackRafId);
      if (intervalId) { clearInterval(intervalId); intervalId = 0; }
      ro.disconnect(); mo.disconnect();
      ["transitionrun","transitionstart","animationstart","transitionend","animationend"].forEach(function(evt){
        doc.removeEventListener(evt, onDocTrans, true);
        doc.removeEventListener(evt, onAny, true);
      });
    });
  }

  function createChip(doc, key) {
    if (attachModeVal !== "portal") return null;
    var chip = doc.createElement("button");
    chip.className = "stusp-chip";
    chip.setAttribute("data-stusp-chip", key);
    chip.setAttribute("aria-label", "Open sidebar");
    chip.textContent = initials; chip.style.background = avatarColor;
    chip.addEventListener("click", function () {
      var btn = findSidebarToggleButton(doc);
      if (btn) { try { btn.click(); } catch (e) {} }
      startGeometryMonitor(doc, currentBottom, currentPad, 2200);
      startForceLoop(doc, currentBottom, currentPad, 1500);
      Streamlit.setComponentValue({ event: "chip", expanded: expanded });
    });
    doc.body.appendChild(chip);
    return chip;
  }

  // =========================
  // Build DOM
  // =========================
  function buildPanel(doc, args, rootClass, key) {
    var root = doc.createElement("div");
    root.className = rootClass;
    root.id = "stusp-portal-" + key;
    root.setAttribute("data-stusp-inst", key);
    root.style.setProperty("--stusp-radius", String(args.border_radius_px || 12) + "px");

    var panel = doc.createElement("div");
    panel.className = "stusp-panel" + (args.compact ? " stusp-compact" : "");
    root.appendChild(panel);

    if (rootClass === "stusp-root") { root.style.position = "fixed"; root.style.zIndex = "2147483000"; root.style.pointerEvents = "none"; }
    else { root.style.position = "sticky"; root.style.bottom = "0px"; root.style.width = "100%"; }

    // Header
    var header = doc.createElement("div");
    header.className = "stusp-header"; header.setAttribute("role","button"); header.setAttribute("tabindex","0");
    header.setAttribute("aria-expanded", String(expanded)); header.setAttribute("aria-label","Toggle user panel");

    var avatar = doc.createElement("div"); avatar.className = "stusp-avatar"; avatar.style.background = avatarColor; avatar.textContent = initials;
    var textWrap = doc.createElement("div"); textWrap.className = "stusp-text";
    var nameEl = doc.createElement("div"); nameEl.className = "stusp-name"; nameEl.textContent = args.name;
    var titleEl = doc.createElement("div"); titleEl.className = "stusp-title"; titleEl.textContent = args.job_title;
    textWrap.appendChild(nameEl); textWrap.appendChild(titleEl);
    var arrow = doc.createElement("div"); arrow.className = "stusp-arrow" + (expanded ? "" : " collapsed"); arrow.textContent = "▲";

    header.appendChild(avatar); header.appendChild(textWrap); header.appendChild(arrow); panel.appendChild(header);

    // Expanded area
    var expandedWrap = doc.createElement("div"); expandedWrap.className = "stusp-expanded"; expandedWrap.style.display = expanded ? "block" : "none";

    // Info card
    var infoRows = [];
    if (args.email) infoRows.push(["Email", args.email]);
    if (args.department) infoRows.push(["Department", args.department]);
    if (args.work_location) infoRows.push(["Work Location", args.work_location]);
    if (infoRows.length) {
      var infoCard = doc.createElement("div"); infoCard.className = "stusp-info";
      infoRows.forEach(function (pair) {
        var row = doc.createElement("div"); row.className = "stusp-info-row";
        var lab = doc.createElement("div"); lab.className = "stusp-info-label"; lab.textContent = pair[0];
        var val = doc.createElement("div"); val.className = "stusp-info-value"; val.textContent = pair[1]; val.setAttribute("title", pair[1]);
        row.appendChild(lab); row.appendChild(val); infoCard.appendChild(row);
      });
      expandedWrap.appendChild(infoCard);
      var hrTop = doc.createElement("div"); hrTop.className = "stusp-divider"; expandedWrap.appendChild(hrTop);
    }

    // Stats
    if (args.show_detailed_stats) {
      var hasLimit = function (v) { return Number(v || 0) > 0; };
      var addCard = function (label, valueStr, pct) {
        var stat = doc.createElement("div"); stat.className = "stusp-stat";
        var l = doc.createElement("div"); l.className = "stusp-stat-label"; l.textContent = label;
        var v = doc.createElement("div"); v.className = "stusp-stat-value"; v.textContent = valueStr;
        stat.appendChild(l); stat.appendChild(v);
        if (args.show_progress && pct != null && isFinite(pct)) {
          var prog = doc.createElement("div"); prog.className = "stusp-progress";
          var bar = doc.createElement("div"); bar.style.width = Math.max(0, Math.min(100, pct)).toFixed(1) + "%";
          prog.appendChild(bar); stat.appendChild(prog);
        }
        expandedWrap.appendChild(stat);
      };
      var addRow = function (container, label, valueStr, pct) {
        var row = doc.createElement("div"); row.className = "stusp-kpi";
        var l = doc.createElement("div"); l.className = "stusp-kpi-label"; l.textContent = label;
        var v = doc.createElement("div"); v.className = "stusp-kpi-value"; v.textContent = valueStr;
        row.appendChild(l); row.appendChild(v);
        if (args.show_progress && pct != null && isFinite(pct)) {
          var bar = doc.createElement("div"); bar.className = "stusp-kpi-bar";
          var inner = doc.createElement("div"); inner.style.width = Math.max(0, Math.min(100, pct)).toFixed(1) + "%";
          bar.appendChild(inner); row.appendChild(bar);
        }
        container.appendChild(row);
      };

      var msgPct = hasLimit(args.monthly_messages_limit) ? Math.min((args.messages_count / args.monthly_messages_limit) * 100, 100) : null;
      var msgVal = hasLimit(args.monthly_messages_limit) ? fmtInt(args.messages_count) + " / " + fmtInt(args.monthly_messages_limit) : fmtInt(args.messages_count);
      var tokPct = hasLimit(args.monthly_tokens_limit) ? Math.min((args.tokens_this_month / args.monthly_tokens_limit) * 100, 100) : null;
      var tokVal = hasLimit(args.monthly_tokens_limit) ? fmtInt(args.tokens_this_month) + " / " + fmtInt(args.monthly_tokens_limit) : fmtInt(args.tokens_this_month);
      var costPct = hasLimit(args.monthly_cost_limit) ? Math.min((args.cost_usd / args.monthly_cost_limit) * 100, 100) : null;
      var costVal = hasLimit(args.monthly_cost_limit) ? fmtUSD(args.cost_usd) + " / " + fmtUSD(args.monthly_cost_limit) : fmtUSD(args.cost_usd);

      if ((args.stats_style || "cards") === "rows") {
        var rows = doc.createElement("div"); rows.className = "stusp-kpis";
        addRow(rows, "MESSAGES THIS MONTH", msgVal, msgPct);
        addRow(rows, "TOKENS THIS MONTH", tokVal, tokPct);
        addRow(rows, "COST THIS MONTH", costVal, costPct);
        expandedWrap.appendChild(rows);
      } else {
        addCard("MESSAGES THIS MONTH", msgVal, msgPct);
        addCard("TOKENS THIS MONTH", tokVal, tokPct);
        addCard("COST THIS MONTH", costVal, costPct);
      }
    }

    // Actions
    var hr = doc.createElement("div"); hr.className = "stusp-divider"; expandedWrap.appendChild(hr);
    var actions = doc.createElement("div"); actions.className = "stusp-actions";
    var btnLogout = doc.createElement("button"); btnLogout.className = "stusp-btn logout"; btnLogout.type = "button"; btnLogout.textContent = "🚪 Logout"; btnLogout.setAttribute("aria-label", "Logout");
    actions.appendChild(btnLogout); expandedWrap.appendChild(actions);

    panel.appendChild(expandedWrap);

    // Interactions
    function setLocalExpanded(next) {
      expanded = next;
      expandedWrap.style.display = expanded ? "block" : "none";
      header.setAttribute("aria-expanded", String(expanded));
      if (expanded) arrow.classList.remove("collapsed"); else arrow.classList.add("collapsed");
    }
    function requestToggle() {
      setLocalExpanded(!expanded);
      Streamlit.setComponentValue({ event: "toggle", expanded: expanded });
    }
    header.addEventListener("click", requestToggle);
    header.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); requestToggle(); }
    });
    btnLogout.addEventListener("click", function () {
      Streamlit.setComponentValue({ event: "logout", expanded: expanded });
    });

    return root;
  }

  // =========================
  // Cleanup
  // =========================
  function removeExisting() {
    cleanupObservers.forEach(function (fn) { try { fn(); } catch (_) {} });
    cleanupObservers = [];
    if (portalRoot && portalRoot.parentNode) portalRoot.parentNode.removeChild(portalRoot);
    if (wrapperEl && wrapperEl.parentNode) wrapperEl.parentNode.removeChild(wrapperEl);
    if (chipEl && chipEl.parentNode) chipEl.parentNode.removeChild(chipEl);
    if (trackRafId) cancelAnimationFrame(trackRafId);
    if (intervalId) { clearInterval(intervalId); intervalId = 0; }
    portalRoot = null; wrapperEl = null; chipEl = null; trackRafId = 0;
  }

  // =========================
  // Render
  // =========================
  function onRender(event) {
    var args = event.detail.args || {};
    instKey = args.instance_key || "st_user_sidebar_panel_default";
    attachModeVal = args.attach_mode || "portal";
    currentPad = Number(args.side_padding_px || 8);
    currentBottom = Number(args.bottom_offset_px || 16);
    avatarColor = args.avatar_color || "#4CAF50";
    initials = initialsOf(args.name);

    var pdoc = safeParentDoc();
    sweepOrphans(pdoc, instKey); // remove previous portals/chips of this instance

    removeExisting();
    if (!pdoc) { Streamlit.setFrameHeight(1); return; }

    ensureStylesInParent(pdoc);
    var sb = getSidebarEl(pdoc);
    if (!sb) { console.warn("[st-user-sidebar-panel] Sidebar not found."); Streamlit.setFrameHeight(1); return; }

    if (!hasMounted) { expanded = !!args.expanded; hasMounted = true; }
    else if (args.controlled) { expanded = !!args.expanded; }

    if (attachModeVal === "inside") {
      portalRoot = buildPanel(pdoc, args, "stusp-root-inside", instKey);
      wrapperEl = pdoc.createElement("div");
      wrapperEl.setAttribute("data-stusp-inst", instKey);
      wrapperEl.style.padding = "8px " + currentPad + "px " + currentBottom + "px " + currentPad + "px";
      wrapperEl.appendChild(portalRoot);
      sb.appendChild(wrapperEl);
      Streamlit.setFrameHeight(1);
      return;
    }

    // portal + chip
    portalRoot = buildPanel(pdoc, args, "stusp-root", instKey);
    pdoc.body.appendChild(portalRoot);
    chipEl = createChip(pdoc, instKey);

    // initial positioning + aggressive monitoring
    positionToSidebar(pdoc, currentBottom, currentPad);
    startGeometryMonitor(pdoc, currentBottom, currentPad, 2200);
    startForceLoop(pdoc, currentBottom, currentPad, 1500);
    attachObservers(pdoc, currentBottom, currentPad);
    Streamlit.setFrameHeight(1);
  }

  window.addEventListener("beforeunload", removeExisting);
  Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender);
  Streamlit.setComponentReady();
  Streamlit.setFrameHeight(1);
})();