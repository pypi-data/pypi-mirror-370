(() => {
  // ---- Minimal manager: no layout manipulation, CSS will hide iframe ----

  let bindings = [];
  let debug = false;
  let seq = 0;

  const rootDoc = (typeof window !== "undefined" && window.parent && window.parent.document)
    ? window.parent.document
    : document;

  function log(...args) { if (debug) console.log("[streamlit-hotkeys]", ...args); }

  // Normalize human-friendly key names to KeyboardEvent.key values
  function normalizeKey(k) {
    if (k == null) return null;
    const s = String(k);
    const lower = s.toLowerCase();
    const map = {
      esc: "Escape", escape: "Escape",
      " ": " ", space: " ",
      enter: "Enter", return: "Enter",
      tab: "Tab",
      up: "ArrowUp", down: "ArrowDown", left: "ArrowLeft", right: "ArrowRight",
      cmd: "Meta", command: "Meta", win: "Meta", meta: "Meta",
      control: "Control", ctrl: "Control",
      alt: "Alt", option: "Alt",
      shift: "Shift"
    };
    if (Object.prototype.hasOwnProperty.call(map, lower)) return map[lower];
    if (s.length === 1) return lower; // single chars: compare case-insensitively
    return s;
  }

  function modOk(need, have) {
    // True=require pressed, False=forbid, null/undefined=ignore
    if (need === null || need === undefined) return true;
    return (!!have) === (!!need);
  }

  // Precompute matching strategy for a binding
  function prepareBinding(b) {
    const prepared = {
      id: String(b.id ?? ""),
      preventDefault: !!b.preventDefault,
      ignoreRepeat: b.ignoreRepeat === false ? false : true,
      ctrl: b.ctrl ?? false,
      alt: b.alt ?? false,
      shift: b.shift ?? false,
      meta: b.meta ?? false,
      byCode: false,
      wantCode: null,
      wantKey: null
    };

    const code = b.code != null ? String(b.code) : null;
    const key  = b.key  != null ? String(b.key)  : null;

    if (code) {
      prepared.byCode = true;
      prepared.wantCode = code; // match e.code exactly
    } else if (key) {
      prepared.wantKey = normalizeKey(key);
    } else {
      prepared.id = ""; // disable invalid binding
    }
    return prepared;
  }

  // Return the first binding that matches KeyboardEvent (or null)
  function matchEvent(e) {
    for (let i = 0; i < bindings.length; i++) {
      const b = bindings[i];
      if (!b.id) continue;
      if (b.ignoreRepeat && e.repeat) continue;

      if (!modOk(b.ctrl, e.ctrlKey))  continue;
      if (!modOk(b.alt, e.altKey))    continue;
      if (!modOk(b.shift, e.shiftKey))continue;
      if (!modOk(b.meta, e.metaKey))  continue;

      if (b.byCode) {
        if (e.code === b.wantCode) return b;
      } else if (b.wantKey != null) {
        const actual = e.key;
        if (b.wantKey.length === 1) {
          if (typeof actual === "string" && actual.length === 1 && actual.toLowerCase() === b.wantKey) {
            return b;
          }
        } else {
          if (normalizeKey(actual) === b.wantKey) return b;
        }
      }
    }
    return null;
  }

  function onKeyDown(e) {
    const b = matchEvent(e);
    if (!b) return;

    if (b.preventDefault) {
      e.preventDefault();
      e.stopPropagation();
    }

    seq += 1;
    const payload = {
      seq,
      id: b.id,
      key: e.key,
      code: e.code,
      ctrl: !!e.ctrlKey,
      alt: !!e.altKey,
      shift: !!e.shiftKey,
      meta: !!e.metaKey,
      ts: Date.now()
    };
    log("emit", payload);
    Streamlit.setComponentValue(payload);
  }

  // ---- Streamlit lifecycle ----

  window.addEventListener("load", () => {
    rootDoc.addEventListener("keydown", onKeyDown, { passive: false });
    Streamlit.setComponentReady();
    Streamlit.setFrameHeight(0); // harmless; CSS will handle visibility
  });

  Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, (event) => {
    const args = (event && event.detail && event.detail.args) || {};
    const rawBindings = Array.isArray(args.bindings) ? args.bindings : [];
    debug = !!args.debug;
    bindings = rawBindings.map(prepareBinding).filter(b => b.id);
    Streamlit.setFrameHeight(0);
  });

  window.addEventListener("beforeunload", () => {
    rootDoc.removeEventListener("keydown", onKeyDown, { passive: false });
  });
})();
