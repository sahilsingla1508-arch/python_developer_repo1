"""
pipeline/delta.py — Delta-compression utilities for the PyChronicle replay pipeline.

Delta compression in this context means: given a raw, ordered list of trace
events (each recording a variable change), produce a *compressed* sequence
that contains only the events where a variable's value actually differs from
its immediately preceding recorded value for that variable.

Because the tracer callback in pipeline/runner.py already applies delta
tracking at *capture* time (it skips writes when the serialized value has
not changed), the events already stored in SQLite are delta-compressed in
practice.  However, when the same database is reused across multiple pipeline
runs the table accumulates rows from all runs, so cross-run duplicates can
appear.  This module provides a clean, explicit compression pass that works
on any ordered event list, regardless of how the data was collected.

Public API
----------
compress_events(events) -> list[dict]
    Remove consecutive duplicate values per variable.  Input and output are
    lists of event dicts with keys:
        id, timestamp, line_number, variable_name, serialized_value

replay_compressed(events, index, source_lines) -> dict
    Convenience wrapper: apply compress_events then call timeline_select so
    callers never have to wire the two steps together manually.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass  # avoid circular imports — ui.app is imported lazily below


# ---------------------------------------------------------------------------
# Core compression
# ---------------------------------------------------------------------------

def compress_events(events: list) -> list:
    """
    Return a delta-compressed copy of *events*.

    Only the first occurrence of each (variable_name, serialized_value) pair
    is kept for each variable.  Subsequent events for a variable are included
    only when the value differs from the most-recently kept value for that
    variable.

    The relative ordering of events is preserved.

    Parameters
    ----------
    events : list[dict]
        Ordered sequence of event dicts, each with at least the keys
        ``variable_name`` and ``serialized_value``.

    Returns
    -------
    list[dict]
        A new list containing only the events that represent genuine value
        changes.  The original dicts are not mutated.

    Examples
    --------
    >>> evs = [
    ...     {"id": 1, "variable_name": "x", "serialized_value": "1", "line_number": 1, "timestamp": "t"},
    ...     {"id": 2, "variable_name": "x", "serialized_value": "1", "line_number": 2, "timestamp": "t"},
    ...     {"id": 3, "variable_name": "x", "serialized_value": "2", "line_number": 3, "timestamp": "t"},
    ... ]
    >>> compressed = compress_events(evs)
    >>> len(compressed)
    2
    >>> [e["id"] for e in compressed]
    [1, 3]
    """
    last_seen: dict[str, str] = {}
    compressed: list = []

    for event in events:
        var = event["variable_name"]
        val = event["serialized_value"]

        if last_seen.get(var) == val:
            # Value unchanged since last recorded event for this variable
            continue

        last_seen[var] = val
        compressed.append(event)

    return compressed


# ---------------------------------------------------------------------------
# Replay helper
# ---------------------------------------------------------------------------

def replay_compressed(events: list, index: int, source_lines: list) -> dict:
    """
    Apply delta compression to *events* then delegate to
    ``ui.app.timeline_select`` for index-to-state mapping.

    This is the single integration point that connects the delta-compression
    layer to the replay pipeline.  Callers (UI layer, tests) can use this
    function without having to manually call both ``compress_events`` and
    ``timeline_select``.

    Parameters
    ----------
    events : list[dict]
        Raw ordered event list (e.g. from ChronicleDataAdapter.get_events()).
    index : int
        0-based position in the *compressed* event timeline.
    source_lines : list[str]
        Source-code lines for the traced script (from _load_source_lines).

    Returns
    -------
    dict with keys:
        compressed_events  : list[dict]  — the compressed event sequence
        event              : dict | None — event at *index* in compressed list
        source_line        : str         — highlighted source line
        variable_state     : dict        — accumulated variable state
        compression_ratio  : float       — len(raw) / len(compressed) or 1.0
    """
    # Lazy import avoids circular dependency (ui.app imports pipeline.runner)
    from ui.app import timeline_select  # noqa: PLC0415

    compressed = compress_events(events)

    raw_count = len(events)
    comp_count = len(compressed)
    ratio = raw_count / comp_count if comp_count > 0 else 1.0

    state = timeline_select(compressed, index, source_lines)

    return {
        "compressed_events": compressed,
        "event": state["event"],
        "source_line": state["source_line"],
        "variable_state": state["variable_state"],
        "compression_ratio": ratio,
    }
