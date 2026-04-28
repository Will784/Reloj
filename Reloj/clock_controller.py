import logging
import tkinter as tk
import datetime
from typing import Optional

from clock_state import ClockState
from themes import Theme
from clock_view import ClockView
from db_manager import DatabaseManager

logger = logging.getLogger(__name__)

TICK_MS: int = 50
ADJUST_RESUME_MS: int = 600


class ClockController:
    def __init__(
        self,
        root: tk.Tk,
        state: ClockState,
        view: ClockView,
        db: DatabaseManager,
    ) -> None:
        self.root  = root
        self.state = state
        self.view  = view
        self.db    = db

        self._fired_alarms: set[int] = set()
        self._timer_alert_shown: bool = False

        self._register_callbacks()
        self._load_preferences()
        self._tick()
        logger.info("ClockController started.")

    def _register_callbacks(self) -> None:
        v = self.view
        v.on_hour_adjust     = self._on_hour_adjust
        v.on_minute_adjust   = self._on_minute_adjust
        v.on_reset_time      = self._on_reset_time
        v.on_timezone_change = self._on_timezone_change
        v.on_theme_change    = self._on_theme_change
        v.on_format_change   = self._on_format_change
        v.on_add_alarm       = self._on_add_alarm
        v.on_delete_alarm    = self._on_delete_alarm
        v.on_toggle_alarm    = self._on_toggle_alarm
        v.on_stopwatch_start = self._on_stopwatch_start
        v.on_stopwatch_pause = self._on_stopwatch_pause
        v.on_stopwatch_reset = self._on_stopwatch_reset
        v.on_timer_set       = self._on_timer_set
        v.on_timer_start     = self._on_timer_start
        v.on_timer_pause     = self._on_timer_pause
        v.on_timer_reset     = self._on_timer_reset

    def _load_preferences(self) -> None:
        prefs = self.db.load_all_preferences()

        tz = "America/Bogota"  # Siempre usar Bogotá como zona horaria predeterminada
        self.state.timezone_name = tz
        self.view.set_timezone_display(tz)

        try:
            self.state.offset_seconds = int(prefs.get("offset_seconds", "0"))
        except ValueError:
            pass

        theme_name = prefs.get("theme", "Claro")
        theme = Theme.get(theme_name)
        self.view.theme = theme
        self.view.redraw_face(theme)
        if hasattr(self.view, "theme_var"):
            self.view.theme_var.set(theme_name)

        fmt_24 = prefs.get("hour_format_24", "false").lower() == "true"
        self.state.hour_format_24 = fmt_24
        if hasattr(self.view, "fmt_var"):
            self.view.fmt_var.set("24h" if fmt_24 else "12h")

        alarms = self.db.load_alarms()
        self.view.refresh_alarms(alarms)

        logger.info("Preferences loaded: tz=%s theme=%s 24h=%s", tz, theme_name, fmt_24)

    def _tick(self) -> None:
        now = self.state.current_time()

        if not self.state.adjusting:
            self.view.update_hands(
                now=now,
                adjusting=self.state.adjusting,
                offset_seconds=self.state.offset_seconds,
                hour_format_24=self.state.hour_format_24,
                timezone_name=self.state.timezone_name,
            )

        self.view.update_stopwatch(self.state.stopwatch_elapsed())

        remaining = self.state.timer_remaining()
        self.view.update_timer(remaining, self.state.timer_finished)
        if self.state.timer_finished and not self._timer_alert_shown:
            self._timer_alert_shown = True
            self.view.show_alarm_alert("¡El temporizador ha terminado!")

        self._check_alarms(now)

        self.root.after(TICK_MS, self._tick)

    def _check_alarms(self, now: "datetime.datetime") -> None:
        alarms = self.db.load_alarms()
        current_minute_key = (now.hour, now.minute)

        stale = {k for k in self._fired_alarms if k != current_minute_key}
        self._fired_alarms -= stale

        for alarm in alarms:
            aid = alarm["id"]
            if self.state.should_trigger_alarm(alarm) and aid not in self._fired_alarms:
                self._fired_alarms.add(aid)
                label = alarm.get("label", "")
                logger.info("Alarm triggered: id=%s label=%s", aid, label)
                self.view.show_alarm_alert(label)

    def _on_hour_adjust(self, delta: int) -> None:
        self.state.start_adjusting()
        self.state.adjust_hours(delta)
        self._persist_offset()
        self.root.after(ADJUST_RESUME_MS, self._resume_after_adjust)
        self._refresh_hands_now()

    def _on_minute_adjust(self, delta: int) -> None:
        self.state.start_adjusting()
        self.state.adjust_minutes(delta)
        self._persist_offset()
        self.root.after(ADJUST_RESUME_MS, self._resume_after_adjust)
        self._refresh_hands_now()

    def _resume_after_adjust(self) -> None:
        self.state.stop_adjusting()

    def _on_reset_time(self) -> None:
        self.state.reset_offset()
        self._persist_offset()
        self._refresh_hands_now()
        logger.info("Time reset to system clock.")

    def _refresh_hands_now(self) -> None:
        now = self.state.current_time()
        self.view.update_hands(
            now=now,
            adjusting=self.state.adjusting,
            offset_seconds=self.state.offset_seconds,
            hour_format_24=self.state.hour_format_24,
            timezone_name=self.state.timezone_name,
        )

    def _persist_offset(self) -> None:
        self.db.save_preference("offset_seconds", str(self.state.offset_seconds))

    def _on_timezone_change(self, tz_name: str) -> None:
        self.state.timezone_name = tz_name
        self.db.save_preference("timezone", tz_name)
        logger.info("Timezone changed to %s", tz_name)

    def _on_theme_change(self, theme_name: str) -> None:
        theme = Theme.get(theme_name)
        self.view.redraw_face(theme)
        self.db.save_preference("theme", theme_name)
        logger.info("Theme changed to %s", theme_name)

    def _on_format_change(self, use_24h: bool) -> None:
        self.state.hour_format_24 = use_24h
        self.db.save_preference("hour_format_24", str(use_24h).lower())
        logger.info("Hour format changed: 24h=%s", use_24h)
        self._refresh_hands_now()

    def _on_add_alarm(self, hour: int, minute: int, label: str) -> None:
        self.db.add_alarm(hour, minute, label)
        self.view.refresh_alarms(self.db.load_alarms())

    def _on_delete_alarm(self, alarm_id: int) -> None:
        self.db.delete_alarm(alarm_id)
        self.view.refresh_alarms(self.db.load_alarms())

    def _on_toggle_alarm(self, alarm_id: int, enabled: bool) -> None:
        self.db.toggle_alarm(alarm_id, enabled)

    def _on_stopwatch_start(self) -> None:
        self.state.stopwatch_start()

    def _on_stopwatch_pause(self) -> None:
        self.state.stopwatch_pause()

    def _on_stopwatch_reset(self) -> None:
        self.state.stopwatch_reset()
        self.view.update_stopwatch(0.0)

    def _on_timer_set(self, total_seconds: int) -> None:
        self.state.timer_set(total_seconds)
        self._timer_alert_shown = False
        self.view.update_timer(float(total_seconds), False)

    def _on_timer_start(self) -> None:
        self.state.timer_start()
        self._timer_alert_shown = False

    def _on_timer_pause(self) -> None:
        self.state.timer_pause()

    def _on_timer_reset(self) -> None:
        self.state.timer_reset()
        self._timer_alert_shown = False
        self.view.update_timer(float(self.state._timer_total_seconds), False)