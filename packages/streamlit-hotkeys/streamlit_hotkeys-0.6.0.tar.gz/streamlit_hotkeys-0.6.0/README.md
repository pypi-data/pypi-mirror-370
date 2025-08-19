# Streamlit Hotkeys

[![PyPI](https://img.shields.io/pypi/v/streamlit-hotkeys.svg)](https://pypi.org/project/streamlit-hotkeys/)
[![Python Versions](https://img.shields.io/pypi/pyversions/streamlit-hotkeys.svg)](https://pypi.org/project/streamlit-hotkeys/)
[![License](https://img.shields.io/pypi/l/streamlit-hotkeys.svg)](LICENSE)
[![Wheel](https://img.shields.io/pypi/wheel/streamlit-hotkeys.svg)](https://pypi.org/project/streamlit-hotkeys/)
![Streamlit Component](https://img.shields.io/badge/streamlit-component-FF4B4B?logo=streamlit\&logoColor=white)
[![Downloads](https://static.pepy.tech/badge/streamlit-hotkeys)](https://pepy.tech/project/streamlit-hotkeys)

**Streamlit Hotkeys** lets you wire up fast, app-wide keyboard shortcuts in seconds. Bind `Ctrl/Cmd/Alt/Shift + key` to actions and get **edge-triggered** events with a clean, Pythonic API (`if hotkeys.pressed("save"):` or multiple `on_pressed(...)` callbacks). It runs through a **single invisible manager**—no widget clutter, no flicker—and can scope reruns to the **whole page or just a fragment**. Reuse the same `id` across combos (e.g., Cmd+K **or** Ctrl+K → `palette`), block browser defaults like `Ctrl/Cmd+S`, and use physical key codes for layout-independent bindings.

---

## Installation

```bash
pip install streamlit-hotkeys
```

## Quick start

```python
import streamlit as st
import streamlit_hotkeys as hotkeys

# Activate early (top of the script)
hotkeys.activate([
    hotkeys.hk("palette", "k", meta=True),              # Cmd+K (mac)
    hotkeys.hk("palette", "k", ctrl=True),              # Ctrl+K (win/linux)
    hotkeys.hk("save", "s", ctrl=True, prevent_default=True),  # Ctrl+S
])

st.title("Hotkeys quick demo")

if hotkeys.pressed("palette"):
    st.write("Open palette")

if hotkeys.pressed("save"):
    st.write("Saved!")

st.caption("Try Cmd/Ctrl+K and Ctrl+S")
```

## Features

* Single invisible **manager** (one iframe per page/fragment)
* Activate early; CSS auto-collapses the iframe to avoid flicker
* **Edge-triggered across reruns**, and **non-consuming within a rerun**
  (you can call `pressed(id)` multiple times and each will see `True`)
* **Callbacks API:** register multiple `on_pressed(id, ...)` handlers (deduped, run in order)
* Each shortcut match **triggers a rerun** — whole page or just the fragment where the manager lives
* Bind single keys or combos (`ctrl`, `alt`, `shift`, `meta`)
* Reuse the **same `id`** across bindings (e.g., Cmd+K **or** Ctrl+K → `palette`)
* `prevent_default` to block browser shortcuts (e.g., Ctrl/Cmd+S)
* Layout-independent physical keys via `code="KeyK"` / `code="Digit1"`
* `ignore_repeat` to suppress repeats while a key is held
* Built-in legend: add `help="..."` in `hk(...)` and call `hotkeys.legend()`
* Multi-page / multi-manager friendly via `key=`
* Optional `debug=True` to log matches in the browser console

## API

### `hk(...)` — define a binding

```python
hk(
  id: str,
  key: str | None = None,           # e.g., "k", "Enter", "ArrowDown"
  *,
  code: str | None = None,          # e.g., "KeyK" (if set, 'key' is ignored)
  alt: bool | None = False,         # True=require, False=forbid, None=ignore
  ctrl: bool | None = False,
  shift: bool | None = False,
  meta: bool | None = False,
  ignore_repeat: bool = True,
  prevent_default: bool = False,
  help: str | None = None,          # optional text shown in legend
) -> dict
```

Defines one shortcut. You may reuse the **same `id`** across multiple bindings (e.g., Cmd+K **or** Ctrl+K → `palette`). Use `code="KeyK"` for layout-independent physical keys.

### `activate(*bindings, key="global", debug=False) -> None`

Registers bindings and renders the single invisible manager. Accepted forms:

* Positional `hk(...)` dicts
* A single list/tuple of `hk(...)` dicts
* A mapping: `id -> spec` **or** `id -> [spec, spec, ...]`

Notes: call **as early as possible** on each page/fragment. The `key` scopes events; if the manager lives inside a fragment, only that fragment reruns on a match. `debug=True` logs matches in the browser console.

### `pressed(id, *, key="global") -> bool`

Returns `True` **once per new key press** (edge-triggered across reruns). Within the **same rerun**, you can call `pressed(id)` multiple times in different places and each will see `True`.

### `on_pressed(id, callback=None, *, key="global", args=(), kwargs=None)`

Registers a callback to run **once per key press**. Multiple callbacks can be registered for the same `id` (deduped across reruns). You can use decorator or direct form. Callbacks run **before** any subsequent `pressed(...)` checks in the same rerun.

### `legend(*, key="global") -> None`

Renders a grouped list of shortcuts for the given manager key. Bindings that share the same `id` are merged; the first non-empty `help` string per `id` is shown.

## Examples

### Basic: simple hotkeys with `if ... pressed(...)`

```python
import streamlit as st
import streamlit_hotkeys as hotkeys

st.title("Basic hotkeys")

hotkeys.activate([
    hotkeys.hk("hello", "h"),     # press H
    hotkeys.hk("enter", "Enter"), # press Enter
])

if hotkeys.pressed("hello"):
    st.write("Hello 👋")

if hotkeys.pressed("enter"):
    st.write("You pressed Enter")
```

### Cross-platform binding (same `id` for Cmd+K / Ctrl+K)

```python
import streamlit as st
import streamlit_hotkeys as hotkeys

st.title("Cross-platform palette (Cmd/Ctrl+K)")

hotkeys.activate([
    hotkeys.hk("palette", "k", meta=True),  # macOS
    hotkeys.hk("palette", "k", ctrl=True),  # Windows/Linux
])

if hotkeys.pressed("palette"):
    st.success("Open command palette")
```

### Block browser default (Ctrl/Cmd+S)

```python
import streamlit as st
import streamlit_hotkeys as hotkeys

st.title("Prevent default on Ctrl/Cmd+S")

hotkeys.activate([
    hotkeys.hk("save", "s", ctrl=True, prevent_default=True),  # Ctrl+S
    hotkeys.hk("save", "s", meta=True,  prevent_default=True), # Cmd+S
])

if hotkeys.pressed("save"):
    st.success("Saved (browser Save dialog was blocked)")
```

### Shortcuts Legend (dialog)

```python
import streamlit as st
import streamlit_hotkeys as hotkeys

st.title("Legend example")

hotkeys.activate({
    "palette": [
        {"key": "k", "meta": True,  "help": "Open command palette"},
        {"key": "k", "ctrl": True},
    ],
    "save": {"key": "s", "ctrl": True, "prevent_default": True, "help": "Save document"},
}, key="global")

@st.dialog("Keyboard Shortcuts")
def _shortcuts():
    hotkeys.legend()  # grouped legend (uses help=...)

if hotkeys.pressed("palette"):
    _shortcuts()

st.caption("Press Cmd/Ctrl+K to open the legend")
```

### Fragment-local reruns (only the fragment updates)

```python
import streamlit as st
import streamlit_hotkeys as hotkeys

st.title("Fragment-local rerun")

st.write("Outside the fragment: no rerun on Ctrl+S")

@st.fragment
def editor_panel():
    hotkeys.activate([hotkeys.hk("save", "s", ctrl=True)], key="editor")
    st.text_area("Document", height=120, key="doc")
    if hotkeys.pressed("save", key="editor"):
        st.success("Saved inside fragment only")

editor_panel()
```

### Hold-to-repeat (`ignore_repeat=False`)

```python
import streamlit as st
import streamlit_hotkeys as hotkeys

st.title("Hold ArrowDown to increment")

hotkeys.activate([
    hotkeys.hk("down", "ArrowDown", ignore_repeat=False),
])

st.session_state.setdefault("count", 0)

if hotkeys.pressed("down"):
    st.session_state["count"] += 1

st.metric("Count", st.session_state["count"])
st.caption("Hold ArrowDown to spam events (ignore_repeat=False)")
```

### Multiple callbacks on the same event

```python
import streamlit as st
import streamlit_hotkeys as hotkeys

st.title("Multiple callbacks")

hotkeys.activate([
    hotkeys.hk("save", "s", ctrl=True, prevent_default=True),
])

def save_doc():
    st.write("Saving...")

def toast_saved():
    st.toast("Saved!")

# register both; each runs once per key press
hotkeys.on_pressed("save", save_doc)
hotkeys.on_pressed("save", toast_saved)

# you can still branch with pressed() afterwards
if hotkeys.pressed("save"):
    st.info("Thank you for saving")
```

## Notes and limitations

* Browsers reserve some shortcuts. Use `prevent_default=True` to keep the event for your app when allowed.
* Combos mean modifiers + one key. The platform does not treat two non-modifier keys pressed together (for example, `A+S`) as a single combo.
* The page must have focus; events are captured at the document level.

## Similar projects

* [streamlit-keypress] - Original "keypress to Python" component by Sudarsan.
* [streamlit-shortcuts] - Keyboard shortcuts for buttons and widgets; supports multiple bindings and hints.
* [streamlit-keyup] - Text input that emits on every keyup (useful for live filtering).
* [keyboard\_to\_url][keyboard_to_url] - Bind a key to open a URL in a new tab.

[streamlit-keypress]: https://pypi.org/project/streamlit-keypress/
[streamlit-shortcuts]: https://pypi.org/project/streamlit-shortcuts/
[streamlit-keyup]: https://pypi.org/project/streamlit-keyup/
[keyboard_to_url]: https://arnaudmiribel.github.io/streamlit-extras/extras/keyboard_url/

## Credits

Inspired by [streamlit-keypress] by **Sudarsan**. This implementation adds a multi-binding manager, edge-triggered events, modifier handling, `preventDefault`, `KeyboardEvent.code` and many more features.

## Contributing

Issues and PRs are welcome.

## License

MIT. See `LICENSE`.
