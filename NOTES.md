# PyChronicle — Week 1 Compatibility Notes

## AST Output vs. SQLite Storage Schema

### Schema (actual, from `storage.py` / `tracer.py`)

```sql
CREATE TABLE IF NOT EXISTS events (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp         TEXT    NOT NULL,
    line_number       INTEGER NOT NULL,
    variable_name     TEXT    NOT NULL,
    serialized_value  TEXT    NOT NULL
);
```

### AST `analyze()` output (from `ast_parser.py`)

```python
[
    {"line_number": int, "variable_name": str},
    ...
]
```

---

## Field Mapping

| Roadmap field | AST output key    | Storage column     | Compatible? |
|---------------|-------------------|--------------------|-------------|
| `line_no`     | `line_number`     | `line_number`      | ✅ Yes (name differs from roadmap alias but consistent internally) |
| `var_name`    | `variable_name`   | `variable_name`    | ✅ Yes |
| `var_value`   | *(runtime only)*  | `serialized_value` | ✅ Captured by tracer at runtime; AST is static-only |
| `var_type`    | *(not present)*   | *(not present)*    | ⚠️ Missing from both; roadmap lists it as expected but schema omits it |
| `id`          | *(N/A)*           | `id` AUTOINCREMENT | ✅ Storage-only, auto-generated |
| `timestamp`   | *(N/A)*           | `timestamp`        | ✅ Set by tracer at runtime |

---

## Compatibility Issues / Mismatches

### 1. `var_type` field absent
- **Roadmap** says expected event fields: `id, timestamp, line_no, var_name, var_value, var_type`
- **Both** `storage.py` schema and `tracer.py` insert logic omit `var_type`.
- **Decision**: Accept absence for now; `serialized_value = str(value)` encodes value only.
  Adding `var_type = type(value).__name__` is a future enhancement.

### 2. Column name aliases
- Roadmap uses shorthand `line_no`, `var_name`, `var_value` in the spec.
- Actual columns use full names: `line_number`, `variable_name`, `serialized_value`.
- **No mismatch** between AST and storage — both use the full names consistently.

### 3. `storage.py` (Varad branch) is a script, not a module
- The file runs side-effects (DB creation + insert) on import.
- `tracer.py` also opens a global DB connection at module level.
- **Fix**: `pipeline/runner.py` initialises the DB via `tracer.run_with_trace()` which handles
  both schema creation (through storage) and commit/close. No duplicate schema init needed
  as long as the DB is created before the tracer runs.

### 4. AST provides only static variable names
- `ast_parser.analyze()` returns variables visible at parse-time with their line numbers.
- Runtime values come exclusively from `tracer.trace_lines` via `sys.settrace`.
- Integration glue: pipeline cross-references AST list against tracer events to confirm
  expected variables were actually traced.

### 5. `executor.py` vs `tracer.run_with_trace()`
- `executor.py` accepts a tracer function via its constructor and calls `sys.settrace` itself.
- `tracer.run_with_trace()` is a self-contained alternative that also calls `sys.settrace`.
- The pipeline uses `tracer.run_with_trace()` directly to avoid duplication.

---

## Conclusion

AST-to-storage field mapping is **compatible** for `line_number` and `variable_name`.
The only gap is `var_type`, which is safely deferred.
The pipeline can proceed with the existing schema without breaking either teammate's code.
