- In Python, prefixing a function or method name with a single underscore (_) is a naming convention that signals the function is "private" or "internal" — meaning it's intended for use only within the module or class, not as part of the public API.
- In Python, prefixing a function or method name with a single underscore (_) is a naming convention that signals the function is "private" or "internal" — meaning it's intended for use only within the module or class, not as part of the public API.

## `_apply_page_bg` — why a module-level private function?

`_apply_page_bg` is kept as a module-level private function (prefixed with `_`) because:
- It is a UI rendering helper — it does not belong on `Topic`, since `Topic` should not know about `ui` rendering
- It follows the same pattern as the other `build_*` helpers in `base.py`
- The `_` prefix already signals "internal, not public API"
- Wrapping it in a class (e.g. `PageBuilder`) would add boilerplate with no real benefit at current scale