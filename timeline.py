import sqlite3
from textual_slider import Slider
from textual.widgets import Static, Button
from textual.containers import Horizontal, Vertical


class TimelineWidget(Vertical):
    """
    Orchestrates the time-scrubbing interface.

    Layout matching reference PyChronicle design:
      Row 1: Header "EXECUTION TIMELINE" (left) + Step label "Step X / Y" (right)
      Row 2: Scrubbing progress slider
      Row 3: Control buttons (‹ Prev / Next › / ▶ Play / ↻ Replay)

    All controls update the parent app's current_event_id reactive,
    which triggers refresh_ui() via watch_current_event_id.
    """

    def __init__(self, db_path: str, **kwargs):
        super().__init__(**kwargs)
        self.db_path = db_path
        self.max_events = self._get_total_events()
        self._play_timer = None
        self._is_playing = False

    def _get_total_events(self) -> int:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM events")
            res = cursor.fetchone()
            conn.close()
            return res[0] if res and res[0] > 0 else 1
        except Exception:
            return 1

    def compose(self):
        # Row 1: Section header (left) + Step indicator (right)
        with Horizontal(id="timeline-top-row"):
            yield Static("EXECUTION TIMELINE", id="timeline-header")
            yield Static(
                f"Step 1 / {self.max_events}",
                id="timeline-step-label",
            )

        # Row 2: Progress slider
        yield Slider(
            min=1,
            max=self.max_events,
            step=1,
            value=1,
            id="timeline-slider",
        )

        # Row 3: Control buttons (centered)
        with Horizontal(id="timeline-controls-row"):
            yield Button("‹ Prev",    id="btn-prev",   variant="default")
            yield Button("Next ›",    id="btn-next",   variant="default")
            yield Button("▶  Play",   id="btn-play",   variant="success")
            yield Button("↻  Replay", id="btn-replay", variant="primary")

    # ── Button handlers ───────────────────────────────────────────────────────

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        app = self.app

        if btn_id == "btn-prev":
            self._stop_play()
            self._set_step(max(1, app.current_event_id - 1))

        elif btn_id == "btn-next":
            self._stop_play()
            self._set_step(min(self.max_events, app.current_event_id + 1))

        elif btn_id == "btn-play":
            if self._is_playing:
                self._stop_play()
            else:
                self._start_play()

        elif btn_id == "btn-replay":
            self._stop_play()
            self._set_step(1)

    # ── Play / Stop ───────────────────────────────────────────────────────────

    def _start_play(self) -> None:
        self._is_playing = True
        btn = self.query_one("#btn-play", Button)
        btn.label = "■  Stop"
        btn.add_class("-playing")
        self._play_timer = self.set_interval(0.6, self._advance_step)

    def _stop_play(self) -> None:
        if self._play_timer is not None:
            self._play_timer.stop()
            self._play_timer = None
        self._is_playing = False
        try:
            btn = self.query_one("#btn-play", Button)
            btn.label = "▶  Play"
            btn.remove_class("-playing")
        except Exception:
            pass

    def _advance_step(self) -> None:
        app = self.app
        if app.current_event_id >= self.max_events:
            self._stop_play()
            return
        self._set_step(app.current_event_id + 1)

    # ── Shared step setter ────────────────────────────────────────────────────

    def _set_step(self, step: int) -> None:
        """Update app reactive, slider position, and step label."""
        app = self.app
        app.current_event_id = step
        try:
            self.query_one("#timeline-slider", Slider).value = step
        except Exception:
            pass
        self._update_step_label(step)

    def _update_step_label(self, step: int) -> None:
        try:
            self.query_one("#timeline-step-label", Static).update(
                f"Step {step} / {self.max_events}"
            )
        except Exception:
            pass

    # ── Slider sync ───────────────────────────────────────────────────────────

    def on_slider_changed(self, event: Slider.Changed) -> None:
        """Keep the step label in sync when the slider is dragged directly."""
        self._update_step_label(int(event.value))
        # Parent app.on_slider_changed handles updating current_event_id