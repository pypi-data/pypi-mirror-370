from __future__ import annotations

import os
from typing import Any, Dict, List, Mapping, Optional, Callable

import streamlit as st
import streamlit.components.v1 as components

# -------- Component declaration (single invisible manager iframe) --------

_BUILD_DIR = os.path.join(os.path.dirname(__file__), "component")
_hotkeys_manager = components.declare_component("manager", path=_BUILD_DIR)


# -------- Session-state keys --------

def _css_flag_key() -> str:
    return "__hk_css_injected__"


def _bindings_key(manager_key: str) -> str:
    return f"__hk_bindings__::{manager_key}"


def _last_event_key(manager_key: str) -> str:
    return f"__hk_last_event__::{manager_key}"


def _per_id_seq_key(manager_key: str) -> str:
    return f"__hk_last_seq_by_id__::{manager_key}"


def _commit_next_key(manager_key: str) -> str:
    return f"__hk_commit_next__::{manager_key}"


def _callbacks_key(manager_key: str) -> str:
    return f"__hk_callbacks__::{manager_key}"


def _callbacks_seq_key(manager_key: str) -> str:
    return f"__hk_last_cb_seq_by_id__::{manager_key}"


def preload_css(*, key: str = "global") -> None:
    """
    Inject CSS that collapses the manager *by its widget key class*.
    Call this at the very top of your app/page, BEFORE `activate(...)`.

    For key="global", Streamlit gives the container class:
      .st-key-hotkeys-manager--global
    """
    css_class = f"st-key-hotkeys-manager--{key}"
    st.markdown(
        f"""
<style>
/* Collapse the specific manager container and its iframe immediately on mount */
.{css_class},
.{css_class} > div {{
  margin:0 !important; padding:0 !important;
  height:0 !important; min-height:0 !important;
  border:0 !important; overflow:hidden !important; line-height:0 !important;
}}
.{css_class} iframe {{
  width:0 !important; height:0 !important; border:0 !important;
  position:absolute !important; opacity:0 !important; pointer-events:none !important;
}}
</style>
""",
        unsafe_allow_html=True,
    )


# -------- Public helper to define a binding --------

def hk(
        id: str,
        key: Optional[str] = None,
        *,
        code: Optional[str] = None,
        alt: Optional[bool] = False,
        ctrl: Optional[bool] = False,
        shift: Optional[bool] = False,
        meta: Optional[bool] = False,
        ignore_repeat: bool = True,
        prevent_default: bool = False,
        help: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a hotkey binding for the manager.

    Args:
        id: Identifier string used with pressed(id). You may reuse the same id across multiple bindings.
        key: KeyboardEvent.key (e.g., "k", "Enter", "ArrowDown").
        code: KeyboardEvent.code (e.g., "KeyK"). If provided, 'key' is ignored.
        alt/ctrl/shift/meta:
            True=require pressed, False=forbid, None=ignore.
        ignore_repeat: Ignore held-key repeats.
        prevent_default: Prevent browser default on match (e.g., Ctrl/Cmd+S).
        help: Optional human-readable description to show in the legend.
    """
    if not id:
        raise ValueError("hk(): 'id' is required and must be non-empty")
    if key is None and code is None:
        raise ValueError("hk(): provide either 'key' or 'code'")
    return {
        "id": str(id),
        "key": key,
        "code": code,
        "alt": alt,
        "ctrl": ctrl,
        "shift": shift,
        "meta": meta,
        "ignoreRepeat": bool(ignore_repeat),
        "preventDefault": bool(prevent_default),
        "help": help,
    }


# -------- Event view used internally for edge-triggered checks --------

class _EventView:
    def __init__(self, payload: Optional[Dict[str, Any]], manager_key: str):
        self.payload = payload or {"seq": 0, "id": None}
        self.manager_key = manager_key
        seq_store = _per_id_seq_key(manager_key)
        if seq_store not in st.session_state:
            st.session_state[seq_store] = {}

    @property
    def id(self) -> Optional[str]:
        return self.payload.get("id")

    @property
    def seq(self) -> int:
        return int(self.payload.get("seq") or 0)

    def pressed(self, binding_id: str) -> bool:
        if not binding_id or self.payload.get("id") != binding_id:
            return False
        store = st.session_state[_per_id_seq_key(self.manager_key)]
        last_seen = int(store.get(binding_id, 0))
        current = self.seq
        if current > last_seen:
            return True
        return False


# -------- Internal: normalize bindings passed to activate() --------

def _normalize_bindings_args(
        *bindings: Any,
        mapping: Optional[Mapping[str, Mapping[str, Any]]] = None
) -> List[Dict[str, Any]]:
    """
    Accepts:
      - activate(hk(...), hk(...))
      - activate([hk(...), hk(...)] )
      - activate({"save": {...}, "open": {...}})  # mapping id -> spec
    """
    out: List[Dict[str, Any]] = []

    # If a single argument is provided and it's a list/tuple: flatten it
    if len(bindings) == 1 and isinstance(bindings[0], (list, tuple)):
        bindings = tuple(bindings[0])

    # If a single argument is provided and it's a dict:
    #   - Either a single hk-dict with "id" in it
    #   - Or a mapping id -> partial spec
    if len(bindings) == 1 and isinstance(bindings[0], dict):
        d = bindings[0]
        if "id" in d:
            out.append(d)  # a single hk(...) dict
        else:
            mapping = d  # treat as mapping
            bindings = tuple()  # and ignore positional

    # Positional hk(...) dicts
    for b in bindings:
        if not isinstance(b, dict) or "id" not in b:
            raise ValueError("activate(): positional args must be hk(...) dicts")
        out.append(b)

    # Mapping id -> spec
    # Mapping id -> spec OR id -> [spec, spec, ...]
    if mapping:
        for _id, spec in mapping.items():
            if isinstance(spec, Mapping):
                out.append(
                    hk(
                        id=_id,
                        key=spec.get("key"),
                        code=spec.get("code"),
                        alt=spec.get("alt", False),
                        ctrl=spec.get("ctrl", False),
                        shift=spec.get("shift", False),
                        meta=spec.get("meta", False),
                        ignore_repeat=spec.get("ignore_repeat", True),
                        prevent_default=spec.get("prevent_default", False),
                        help=spec.get("help"),
                    )
                )
            elif isinstance(spec, (list, tuple)):
                for s in spec:
                    if not isinstance(s, Mapping):
                        raise ValueError("activate(): each item in list must be a dict-like spec")
                    out.append(
                        hk(
                            id=_id,
                            key=s.get("key"),
                            code=s.get("code"),
                            alt=s.get("alt", False),
                            ctrl=s.get("ctrl", False),
                            shift=s.get("shift", False),
                            meta=s.get("meta", False),
                            ignore_repeat=s.get("ignore_repeat", True),
                            prevent_default=s.get("prevent_default", False),
                            help=s.get("help"),
                        )
                    )
            else:
                raise ValueError("activate(): mapping values must be a dict or a list of dicts")
    return out


# -------- Core: render manager + store last payload for pressed() --------

def _render_manager(bindings: List[Dict[str, Any]], *, key: str, debug: bool) -> _EventView:
    payload = _hotkeys_manager(
        bindings=bindings,
        debug=bool(debug),
        default={"seq": 0},
        key=f"hotkeys-manager::{key}",
    )
    # Store last payload for pressed()
    st.session_state[_last_event_key(key)] = payload
    return _EventView(payload, manager_key=key)


def _run_callbacks(manager_key: str) -> None:
    """Dispatch registered callbacks for the id that fired (if any),
    without consuming the event for pressed()."""
    payload = st.session_state.get(_last_event_key(manager_key))
    if not isinstance(payload, dict):
        return

    event_id = payload.get("id")
    seq = int(payload.get("seq") or 0)
    if not event_id:
        return

    callbacks = st.session_state.get(_callbacks_key(manager_key), {})
    if not callbacks or event_id not in callbacks:
        return

    # Ensure we run each callback set ONCE per seq, but don't affect pressed()
    cb_store = st.session_state.setdefault(_callbacks_seq_key(manager_key), {})
    last_run = int(cb_store.get(event_id, 0))
    if seq > last_run:
        for fn, args, kwargs in callbacks[event_id]:
            fn(*args, **(kwargs or {}))
        cb_store[event_id] = seq


# -------- Public API -----------------------------------------------------

def activate(
        *bindings: Any,
        key: str = "global",
        debug: bool = False,
) -> None:
    """Configure and activate the hotkeys manager (render the single invisible iframe).

    Call this **as early as possible** on the page or inside a `@st.fragment`. Once a
    registered shortcut is pressed, the manager updates its value and **Streamlit
    reruns** (the whole script, or only that fragment if the manager lives there).

    You can pass bindings as:
    - positional `hk(...)` dicts,
    - a single list/tuple of `hk(...)` dicts, or
    - a mapping: `id -> spec` or `id -> [spec, spec, ...]`.

    Each *spec* may contain:
    `key`, `code`, `alt`, `ctrl`, `shift`, `meta`, `ignore_repeat`,
    `prevent_default`, `help`.
    Duplicate `id`s are allowed (e.g., `Cmd+K` **or** `Ctrl+K` both map to `"palette"`).

    Args:
        *bindings: One or more `hk(...)` dicts, a single list/tuple of them,
            or a mapping of `id -> spec` (or `id -> [spec, ...]`). See examples.
        key (str): Manager namespace. Events/callbacks are isolated per key.
            Place the manager inside a fragment with a unique `key` if you want
            **partial reruns** of that fragment only. Default: `"global"`.
        debug (bool): If `True`, the frontend logs matches to the browser console.
            Useful while authoring shortcuts. Default: `False`.

    Example:
    ```python
    import streamlit as st
    import streamlit_hotkeys as hotkeys

    # Page-level manager: the whole script reruns on a press
    hotkeys.activate([
        hotkeys.hk("palette", "k", meta=True, help="Open palette (mac)"),
        hotkeys.hk("palette", "k", ctrl=True, help="Open palette (win/linux)"),
        hotkeys.hk("save", "s", ctrl=True, prevent_default=True, help="Save"),
    ], key="global")

    if hotkeys.pressed("palette"):
        st.info("Palette opened")

    # Fragment-level manager: only this fragment reruns on Ctrl+S
    @st.fragment
    def editor():
        hotkeys.activate([hotkeys.hk("save", "s", ctrl=True)], key="editor")
        if hotkeys.pressed("save", key="editor"):
            st.success("Saved (fragment)")

    editor()
    ```
    """
    preload_css(key=key)

    # Commit any pending seq from the previous run so old events stop firing
    committed = st.session_state.setdefault(_per_id_seq_key(key), {})
    pending = st.session_state.get(_commit_next_key(key), {})
    if isinstance(pending, dict) and pending:
        for _id, s in pending.items():
            try:
                s_int = int(s or 0)
            except ValueError:
                s_int = 0
            if s_int > int(committed.get(_id, 0)):
                committed[_id] = s_int
        st.session_state[_commit_next_key(key)] = {}

    normalized = _normalize_bindings_args(*bindings)
    st.session_state[_bindings_key(key)] = normalized
    _render_manager(normalized, key=key, debug=debug)

    # Queue the current event for commit on the next run
    payload = st.session_state.get(_last_event_key(key))
    if isinstance(payload, dict):
        _id = payload.get("id")
        if _id:
            seq = int(payload.get("seq") or 0)
            pend = st.session_state.setdefault(_commit_next_key(key), {})
            prev = int(pend.get(_id, 0))
            if seq > prev:
                pend[_id] = seq

    _run_callbacks(key)


def pressed(binding_id: str, *, key: str = "global") -> bool:
    """Return True exactly once **per new key press**, without being consumed within the same rerun.

    Behavior:
    - Within a single rerun, you can call `pressed(id)` **multiple times** in
      different places and each call will see `True` for the same event.
    - On the **next rerun**, the event is committed and `pressed(id)` returns
      `False` until the user presses the shortcut again.
    - Requires that `activate(...)` has already run (on this page or fragment).

    Args:
        binding_id (str): The `id` used when registering the binding(s), e.g. `"save"`.
            You can map multiple combos to the same `id`.
        key (str): Manager key used in `activate(...)`. Default: `"global"`.

    Returns:
        bool: `True` for a new event, otherwise `False`.

    Example:
        ```python
        # Both branches run on the same press (same rerun):
        if hotkeys.pressed("save"):
            st.info("Thanks for saving")

        if hotkeys.pressed("save"):
            st.info("Follow-up message")
        ```
    """

    # Ensure the per-id seq store exists
    seq_store = _per_id_seq_key(key)
    if seq_store not in st.session_state:
        st.session_state[seq_store] = {}

    payload = st.session_state.get(_last_event_key(key))
    if not isinstance(payload, dict):
        # Try to render with stored bindings so the manager is present
        bindings = st.session_state.get(_bindings_key(key), [])
        if not isinstance(bindings, list):
            bindings = []
        view = _render_manager(bindings, key=key, debug=False)
    else:
        view = _EventView(payload, manager_key=key)

    return view.pressed(binding_id)


def _cb_sig(fn: Callable) -> tuple:
    code = getattr(fn, "__code__", None)
    return (
        getattr(fn, "__module__", None),
        getattr(fn, "__qualname__", getattr(fn, "__name__", None)),
        getattr(code, "co_firstlineno", None),
        getattr(code, "co_filename", None),
    )


def on_pressed(
    binding_id: str,
    callback: Optional[Callable] = None,
    *,
    key: str = "global",
    args: tuple = (),
    kwargs: Optional[dict] = None,
):
    """Register a callback to run **once per key press** for the given `binding_id`.

    You can register multiple callbacks for the same `id`; they all run (in
    registration order) once per event. Registrations are **deduped across reruns**
    by function identity + args/kwargs. Works alongside `pressed()` checks in the
    same rerun—callbacks run first, then your `pressed()` branches execute.

    Args:
        binding_id (str): The `id` used by the binding(s), e.g. `"save"`.
        callback (Callable | None): Function to run when the event fires. If omitted,
            the function can be supplied via decorator style (see example).
        key (str): Manager key used in `activate(...)`. Default: `"global"`.
        args (tuple): Positional args passed to the callback. Default: `()`.
        kwargs (dict | None): Keyword args passed to the callback. Default: `None`.

    Example:
        ```python
        def do_save():
            st.success("Saved!")

        # direct registration
        hotkeys.on_pressed("save", do_save)

        # decorator registration (second callback on same id)
        @hotkeys.on_pressed("save")
        def toast():
            st.toast("Save complete")

        # You can still branch with pressed() in the same rerun
        if hotkeys.pressed("save"):
            st.info("Thank you for saving")
        ```
    """
    if not binding_id:
        raise ValueError("on_pressed(): 'binding_id' is required")

    store = st.session_state.setdefault(_callbacks_key(key), {})
    if kwargs is None:
        kwargs = {}

    def _register(fn: Callable):
        lst = store.setdefault(binding_id, [])
        sig = (_cb_sig(fn), args, tuple(sorted(kwargs.items())))
        # dedupe: if same fn/args/kwargs already registered, REPLACE the old entry
        for i, (f_existing, a_existing, kw_existing) in enumerate(lst):
            sig_existing = (
                _cb_sig(f_existing),
                a_existing,
                tuple(sorted((kw_existing or {}).items())),
            )
            if sig_existing == sig:
                lst[i] = (fn, args, kwargs)  # update with the new function object
                # If you want latest registration to affect order, move to end:
                # lst.append(lst.pop(i))
                return fn
        lst.append((fn, args, kwargs))
        return fn

    if callback is None:
        return _register  # decorator form
    else:
        return _register(callback)


def legend(*, key: str = "global") -> None:
    """Render a grouped legend of the active shortcuts for this manager key.

    Shortcuts that share the same `id` (e.g., `Cmd+K` and `Ctrl+K` both mapped to
    `"palette"`) are merged onto one line. If a binding was created with
    `help="..."`, the first non-empty help text for that `id` is shown.

    Args:
        key (str): Manager key used in `activate(...)`. Default: `"global"`.

    Example:
        ```python
        import streamlit as st
        import streamlit_hotkeys as hotkeys

        hotkeys.activate({
            "palette": [
                {"key": "k", "meta": True,  "help": "Open command palette"},
                {"key": "k", "ctrl": True},  # same id, second combo
            ],
            "save": {"key": "s", "ctrl": True, "prevent_default": True, "help": "Save document"},
        }, key="global")

        @st.dialog("Keyboard Shortcuts")
        def show_shortcuts():
            hotkeys.legend()

        if hotkeys.pressed("palette"):
            show_shortcuts()
        ```
    """
    bindings = st.session_state.get(_bindings_key(key), [])
    if not bindings:
        st.info("No hotkeys configured.")
        return

    def _fmt_keyname(b: Dict[str, Any]) -> str:
        # Prefer .key label; fall back to .code for physical keys
        key = b.get("key")
        code = b.get("code")

        def sym(k: str) -> str:
            if k == " " or k == "Space":
                return "Space"
            if k == "Escape":
                return "Esc"
            if k == "ArrowLeft":
                return "←"
            if k == "ArrowRight":
                return "→"
            if k == "ArrowUp":
                return "↑"
            if k == "ArrowDown":
                return "↓"
            return k

        if key:
            k = key.upper() if len(key) == 1 else key
            return sym(k)
        if code:
            # Turn KeyK -> K, Digit1 -> 1; else show raw code
            if code.startswith("Key") and len(code) == 4:
                return code[-1]
            if code.startswith("Digit") and len(code) == 6:
                return code[-1]
            return code
        return "?"

    def _combo_label(b: Dict[str, Any]) -> str:
        parts = []
        if b.get("ctrl"):  parts.append("Ctrl")
        if b.get("alt"):   parts.append("Alt")
        if b.get("shift"): parts.append("Shift")
        if b.get("meta"):  parts.append("Cmd")  # shown as Cmd for familiarity
        parts.append(_fmt_keyname(b))
        return "+".join(parts)

    # Group combos by id
    grouped: Dict[str, Dict[str, Any]] = {}
    for b in bindings:
        _id = b.get("id")
        if not _id:
            continue
        item = grouped.setdefault(_id, {"combos": [], "help": None})
        item["combos"].append(f"`{_combo_label(b)}`")
        if not item["help"]:
            h = b.get("help")
            if isinstance(h, str) and h.strip():
                item["help"] = h.strip()

    # Render a compact table
    import pandas as pd
    rows = []
    for _id, info in grouped.items():
        rows.append({
            "Shortcut": " / ".join(info["combos"]),
            "Help": info["help"] or "",
        })
    df = pd.DataFrame(rows, columns=["Shortcut", "Help"]).set_index("Shortcut")

    st.table(df)
