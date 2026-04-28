import math
import tkinter as tk
from tkinter import font as tkfont, ttk, messagebox, colorchooser
import datetime
import logging
from typing import Callable, Optional

from themes import Theme
from clock_state import COUNTRY_TIMEZONES, COUNTRY_CAPITALS

logger = logging.getLogger(__name__)

CANVAS_SIZE: int = 520
CENTER: int = CANVAS_SIZE // 2
CLOCK_RADIUS: int = 220


def polar_to_xy(
    angle_deg: float,
    radius: float,
    cx: float = CENTER,
    cy: float = CENTER,
) -> tuple[float, float]:
    angle_rad = math.radians(angle_deg - 90)
    x = cx + radius * math.cos(angle_rad)
    y = cy + radius * math.sin(angle_rad)
    return x, y


def hand_polygon(
    angle_deg: float,
    length: float,
    width: float,
    tail: float = 0.0,
    cx: float = CENTER,
    cy: float = CENTER,
) -> list[float]:
    tip_x,   tip_y   = polar_to_xy(angle_deg,       length, cx, cy)
    tail_x,  tail_y  = polar_to_xy(angle_deg + 180, tail,   cx, cy)
    left_x,  left_y  = polar_to_xy(angle_deg + 90,  width,  cx, cy)
    right_x, right_y = polar_to_xy(angle_deg - 90,  width,  cx, cy)
    return [left_x, left_y, tip_x, tip_y, right_x, right_y, tail_x, tail_y]


class ClockView:
    def __init__(self, root: tk.Tk, theme: Theme) -> None:
        self.root = root
        self.theme = theme

        self._font_title   = tkfont.Font(family="Georgia", size=14, weight="bold")
        self._font_readout = tkfont.Font(family="Courier", size=19, weight="bold")
        self._font_small   = tkfont.Font(family="Helvetica", size=10)
        self._font_btn     = tkfont.Font(family="Helvetica", size=11, weight="bold")
        self._font_tab     = tkfont.Font(family="Helvetica", size=10, weight="bold")
        self._font_mono    = tkfont.Font(family="Courier", size=22, weight="bold")

        self.on_hour_adjust:      Optional[Callable[[int], None]] = None
        self.on_minute_adjust:    Optional[Callable[[int], None]] = None
        self.on_reset_time:       Optional[Callable[[], None]]    = None
        self.on_timezone_change:  Optional[Callable[[str], None]] = None
        self.on_theme_change:     Optional[Callable[[str], None]] = None
        self.on_format_change:    Optional[Callable[[bool], None]]= None
        self.on_add_alarm:        Optional[Callable[[int, int, str], None]] = None
        self.on_delete_alarm:     Optional[Callable[[int], None]] = None
        self.on_toggle_alarm:     Optional[Callable[[int, bool], None]] = None
        self.on_stopwatch_start:  Optional[Callable[[], None]]    = None
        self.on_stopwatch_pause:  Optional[Callable[[], None]]    = None
        self.on_stopwatch_reset:  Optional[Callable[[], None]]    = None
        self.on_timer_set:        Optional[Callable[[int], None]] = None
        self.on_timer_start:      Optional[Callable[[], None]]    = None
        self.on_timer_pause:      Optional[Callable[[], None]]    = None
        self.on_timer_reset:      Optional[Callable[[], None]]    = None

        self._build_window()
        self._build_notebook()
        self._draw_static_face()

    def _build_window(self) -> None:
        self.root.title("Reloj Analógico")
        self.root.resizable(False, False)
        self.root.configure(bg=self.theme.bg_window)

    def _btn_style(self, bg: Optional[str] = None, fg: Optional[str] = None) -> dict:
        return dict(
            bg=bg or self.theme.ui_btn_bg,
            fg=fg or self.theme.ui_btn_fg,
            relief="flat",
            font=self._font_btn,
            cursor="hand2",
            bd=0,
            padx=8,
            pady=4,
            activebackground=self.theme.ui_btn_active,
            activeforeground="white",
        )

    def _build_notebook(self) -> None:
        t = self.theme

        self.lbl_title = tk.Label(
            self.root, text="Reloj Analógico",
            font=self._font_title, bg=t.bg_window, fg=t.text_title
        )
        self.lbl_title.pack(pady=(14, 2))

        self._clock_container = tk.Frame(self.root, bg=t.bg_canvas)
        self._clock_container.pack(padx=20)

        self.canvas = tk.Canvas(
            self._clock_container, width=CANVAS_SIZE, height=CANVAS_SIZE,
            bg=t.bg_canvas, highlightthickness=0
        )
        self.canvas.pack()

        self.lbl_readout = tk.Label(
            self.root, text="", font=self._font_readout,
            bg=t.bg_window, fg=t.text_readout
        )
        self.lbl_readout.pack(pady=(4, 0))

        self.lbl_status = tk.Label(
            self.root, text="", font=self._font_small,
            bg=t.bg_window, fg=t.text_label
        )
        self.lbl_status.pack()

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.TNotebook", background=t.bg_window, borderwidth=0)
        style.configure(
            "Custom.TNotebook.Tab",
            background=t.ui_btn_bg,
            foreground=t.ui_btn_fg,
            padding=[10, 4],
            font=("Helvetica", 10, "bold"),
        )
        style.map(
            "Custom.TNotebook.Tab",
            background=[("selected", t.ui_btn_active)],
            foreground=[("selected", "white")],
        )

        self.notebook = ttk.Notebook(self.root, style="Custom.TNotebook")
        self.notebook.pack(fill="x", padx=20, pady=(6, 14))

        self._build_tab_clock()
        self._build_tab_settings()
        self._build_tab_alarms()
        self._build_tab_stopwatch()
        self._build_tab_timer()

    def _build_tab_clock(self) -> None:
        t = self.theme
        frame = tk.Frame(self.notebook, bg=t.bg_window, pady=8)
        self.notebook.add(frame, text="Reloj")

        crown = tk.Frame(frame, bg=t.bg_window)
        crown.pack()

        tk.Label(
            crown, text="Ajustar hora:", font=self._font_small,
            bg=t.bg_window, fg=t.text_label
        ).pack(side="left", padx=(0, 6))

        tk.Label(crown, text="H:", bg=t.bg_window, fg=t.text_label,
                 font=self._font_small).pack(side="left")

        self.btn_hour_back = tk.Button(
            crown, text="-", width=3, **self._btn_style(),
            command=lambda: self.on_hour_adjust and self.on_hour_adjust(-1)
        )
        self.btn_hour_back.pack(side="left", padx=2)

        self.btn_hour_fwd = tk.Button(
            crown, text="+", width=3, **self._btn_style(),
            command=lambda: self.on_hour_adjust and self.on_hour_adjust(+1)
        )
        self.btn_hour_fwd.pack(side="left", padx=(2, 10))

        tk.Label(crown, text="M:", bg=t.bg_window, fg=t.text_label,
                 font=self._font_small).pack(side="left")

        self.btn_min_back = tk.Button(
            crown, text="-", width=3, **self._btn_style(),
            command=lambda: self.on_minute_adjust and self.on_minute_adjust(-1)
        )
        self.btn_min_back.pack(side="left", padx=2)

        self.btn_min_fwd = tk.Button(
            crown, text="+", width=3, **self._btn_style(),
            command=lambda: self.on_minute_adjust and self.on_minute_adjust(+1)
        )
        self.btn_min_fwd.pack(side="left", padx=2)

        tk.Button(
            crown, text="Reset", width=6,
            bg="#888", fg="white", relief="flat", bd=0, cursor="hand2",
            font=self._font_btn, padx=8, pady=4,
            activebackground="#555", activeforeground="white",
            command=lambda: self.on_reset_time and self.on_reset_time()
        ).pack(side="left", padx=(10, 0))

        tz_row = tk.Frame(frame, bg=t.bg_window)
        tz_row.pack(pady=(10, 0))

        tk.Label(
            tz_row, text="País:", font=self._font_small,
            bg=t.bg_window, fg=t.text_label
        ).pack(side="left", padx=(0, 4))

        self._country_var = tk.StringVar()
        self._country_combo = ttk.Combobox(
            tz_row, textvariable=self._country_var,
            values=sorted(COUNTRY_TIMEZONES.keys()),
            state="normal", width=22
        )
        self._country_combo.pack(side="left", padx=(0, 12))
        self._country_combo.bind("<<ComboboxSelected>>", self._on_country_selected)
        self._country_combo.bind("<KeyRelease>", self._filter_countries)

        tk.Label(
            tz_row, text="Capital:", font=self._font_small,
            bg=t.bg_window, fg=t.text_label
        ).pack(side="left", padx=(0, 4))

        self._city_label = tk.Label(
            tz_row, text="Bogotá", font=self._font_small,
            bg=t.bg_window, fg=t.text_readout, width=16, anchor="w"
        )
        self._city_label.pack(side="left")

        self._pending_tz: str = "America/Bogota"
        self._country_var.set("Colombia")  # Establecer Colombia como predeterminado

        self.btn_set_tz = tk.Button(
            tz_row, text="Establecer", **self._btn_style(),
            command=self._on_apply_timezone
        )
        self.btn_set_tz.pack(side="left", padx=(10, 0))

        self.tz_var = tk.StringVar(value="America/Bogota")

        self.lbl_tz_display = tk.Label(
            frame, text="", font=self._font_small,
            bg=t.bg_window, fg=t.text_label
        )
        self.lbl_tz_display.pack(pady=(4, 0))

    def _filter_countries(self, event=None) -> None:
        typed = self._country_var.get().lower()
        all_countries = sorted(COUNTRY_TIMEZONES.keys())
        filtered = [c for c in all_countries if c.lower().startswith(typed)] if typed else all_countries
        self._country_combo["values"] = filtered

    def _on_country_selected(self, event=None) -> None:
        """Al escoger un pais solo actualiza el label y guarda el tz pendiente.
        El cambio real se aplica al pulsar el boton Establecer."""
        country = self._country_var.get()
        capital = COUNTRY_CAPITALS.get(country)
        if not capital:
            cities = sorted(COUNTRY_TIMEZONES.get(country, {}).keys())
            capital = cities[0] if cities else None

        if capital:
            self._city_label.config(text=capital)
            tz = COUNTRY_TIMEZONES.get(country, {}).get(capital)
            if tz:
                self._pending_tz = tz
                logger.debug("Country previewed: %s capital=%s tz=%s", country, capital, tz)

    def _on_apply_timezone(self) -> None:
        """Aplica el timezone pendiente al hacer clic en Establecer."""
        tz = getattr(self, "_pending_tz", None)
        if tz:
            self.tz_var.set(tz)
            if self.on_timezone_change:
                self.on_timezone_change(tz)
            logger.info("Timezone applied: %s", tz)

    def set_timezone_display(self, tz_name: str) -> None:
        self.tz_var.set(tz_name)
        # Buscar y establecer el país y capital correspondientes
        for country, cities in COUNTRY_TIMEZONES.items():
            for city, tz in cities.items():
                if tz == tz_name:
                    self._country_var.set(country)
                    if hasattr(self, "_city_label"):
                        self._city_label.config(text=city)
                    return
        self._country_var.set("")
        if hasattr(self, "_city_label"):
            self._city_label.config(text=tz_name)

    def _build_tab_settings(self) -> None:
        t = self.theme
        frame = tk.Frame(self.notebook, bg=t.bg_window, pady=8)
        self.notebook.add(frame, text="Ajustes")

        theme_row = tk.Frame(frame, bg=t.bg_window)
        theme_row.pack(pady=4)

        tk.Label(
            theme_row, text="Tema:", font=self._font_small,
            bg=t.bg_window, fg=t.text_label
        ).pack(side="left", padx=(0, 8))

        self.theme_var = tk.StringVar(value=t.name)
        self.theme_combo = ttk.Combobox(
            theme_row, textvariable=self.theme_var,
            values=Theme.preset_names(), state="readonly", width=12
        )
        self.theme_combo.pack(side="left")
        self.theme_combo.bind(
            "<<ComboboxSelected>>",
            lambda e: self.on_theme_change and self.on_theme_change(self.theme_var.get())
        )

        fmt_row = tk.Frame(frame, bg=t.bg_window)
        fmt_row.pack(pady=4)

        tk.Label(
            fmt_row, text="Formato de hora:", font=self._font_small,
            bg=t.bg_window, fg=t.text_label
        ).pack(side="left", padx=(0, 8))

        self.fmt_var = tk.StringVar(value="12h")
        for label, val in [("12 horas", "12h"), ("24 horas", "24h")]:
            tk.Radiobutton(
                fmt_row, text=label, variable=self.fmt_var, value=val,
                bg=t.bg_window, fg=t.text_label,
                activebackground=t.bg_window,
                selectcolor=t.bg_window,
                command=self._on_format_radio
            ).pack(side="left", padx=4)

        separator = tk.Frame(frame, bg=t.text_label, height=1)
        separator.pack(fill="x", padx=10, pady=(8, 4))

        tk.Label(
            frame, text="Personalización de colores",
            font=self._font_small, bg=t.bg_window, fg=t.text_title
        ).pack()

        colors_frame = tk.Frame(frame, bg=t.bg_window)
        colors_frame.pack(pady=4)
        self._color_fields = [
            ("Fondo ventana",     "bg_window"),
            ("Fondo reloj",       "bg_canvas"),
            ("Cara reloj",        "face_fill"),
            ("Aro exterior",      "face_rim"),
            ("Manecilla hora",    "hand_hour"),
            ("Manecilla minuto",  "hand_minute"),
            ("Manecilla segundo", "hand_second"),
            ("Números",           "number_color"),
            ("Lectura digital",   "text_readout"),
        ]

        self._color_swatches: dict[str, tk.Label] = {}

        for i, (label_text, field_name) in enumerate(self._color_fields):
            row = i // 2
            col = i % 2
            cell = tk.Frame(colors_frame, bg=t.bg_window)
            cell.grid(row=row, column=col, padx=6, pady=2, sticky="w")

            current_color = getattr(self.theme, field_name)
            swatch = tk.Label(
                cell, bg=current_color, width=2, relief="solid", bd=1
            )
            swatch.pack(side="left", padx=(0, 4))
            self._color_swatches[field_name] = swatch

            tk.Label(
                cell, text=label_text, font=self._font_small,
                bg=t.bg_window, fg=t.text_label, width=16, anchor="w"
            ).pack(side="left")

            tk.Button(
                cell, text="Cambiar", font=self._font_small,
                bg=t.ui_btn_bg, fg=t.ui_btn_fg, relief="flat", cursor="hand2",
                command=lambda fn=field_name, sw=swatch: self._pick_color(fn, sw)
            ).pack(side="left", padx=(2, 0))

    def _pick_color(self, field_name: str, swatch: tk.Label) -> None:
        current = getattr(self.theme, field_name)
        result = colorchooser.askcolor(color=current, title=f"Seleccionar color: {field_name}")
        if result and result[1]:
            new_color = result[1]
            import dataclasses
            new_theme = dataclasses.replace(self.theme, name="Personalizado", **{field_name: new_color})
            swatch.config(bg=new_color)
            self.redraw_face(new_theme)

    def _on_format_radio(self) -> None:
        if self.on_format_change:
            self.on_format_change(self.fmt_var.get() == "24h")

    def _build_tab_alarms(self) -> None:
        t = self.theme
        frame = tk.Frame(self.notebook, bg=t.bg_window, pady=8)
        self.notebook.add(frame, text="Alarmas")

        add_row = tk.Frame(frame, bg=t.bg_window)
        add_row.pack()

        tk.Label(add_row, text="Hora:", font=self._font_small,
                 bg=t.bg_window, fg=t.text_label).pack(side="left")
        self.alarm_hour_var = tk.StringVar(value="07")
        tk.Spinbox(
            add_row, from_=0, to=23, textvariable=self.alarm_hour_var,
            width=3, format="%02.0f"
        ).pack(side="left", padx=2)

        tk.Label(add_row, text=":", font=self._font_small,
                 bg=t.bg_window, fg=t.text_label).pack(side="left")
        self.alarm_min_var = tk.StringVar(value="00")
        tk.Spinbox(
            add_row, from_=0, to=59, textvariable=self.alarm_min_var,
            width=3, format="%02.0f"
        ).pack(side="left", padx=2)

        tk.Label(add_row, text="Etiqueta:", font=self._font_small,
                 bg=t.bg_window, fg=t.text_label).pack(side="left", padx=(8, 2))
        self.alarm_label_var = tk.StringVar()
        tk.Entry(add_row, textvariable=self.alarm_label_var, width=12).pack(side="left", padx=2)

        tk.Button(
            add_row, text="Agregar", **self._btn_style(),
            command=self._add_alarm_clicked
        ).pack(side="left", padx=(8, 0))

        self.alarm_listbox_frame = tk.Frame(frame, bg=t.bg_window)
        self.alarm_listbox_frame.pack(fill="both", expand=True, pady=(8, 0), padx=10)

        self.lbl_no_alarms = tk.Label(
            self.alarm_listbox_frame,
            text="No hay alarmas configuradas.",
            font=self._font_small, bg=t.bg_window, fg=t.text_label
        )
        self.lbl_no_alarms.pack()

        self._alarm_rows: dict[int, tk.Frame] = {}

    def _add_alarm_clicked(self) -> None:
        try:
            h = int(self.alarm_hour_var.get())
            m = int(self.alarm_min_var.get())
            label = self.alarm_label_var.get().strip()
            if not (0 <= h <= 23 and 0 <= m <= 59):
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Hora o minuto inválidos.")
            return
        if self.on_add_alarm:
            self.on_add_alarm(h, m, label)

    def refresh_alarms(self, alarms: list[dict]) -> None:
        for widget in self.alarm_listbox_frame.winfo_children():
            widget.destroy()
        self._alarm_rows = {}

        if not alarms:
            tk.Label(
                self.alarm_listbox_frame,
                text="No hay alarmas configuradas.",
                font=self._font_small, bg=self.theme.bg_window, fg=self.theme.text_label
            ).pack()
            return

        for alarm in alarms:
            aid = alarm["id"]
            row = tk.Frame(self.alarm_listbox_frame, bg=self.theme.bg_window)
            row.pack(fill="x", pady=2)

            enabled_var = tk.BooleanVar(value=bool(alarm["enabled"]))
            tk.Checkbutton(
                row, variable=enabled_var, bg=self.theme.bg_window,
                activebackground=self.theme.bg_window,
                command=lambda v=enabled_var, i=aid: (
                    self.on_toggle_alarm and self.on_toggle_alarm(i, v.get())
                )
            ).pack(side="left")

            label_text = f"{alarm['hour']:02d}:{alarm['minute']:02d}"
            if alarm["label"]:
                label_text += f"  —  {alarm['label']}"

            tk.Label(
                row, text=label_text, font=self._font_small,
                bg=self.theme.bg_window, fg=self.theme.text_label, width=28, anchor="w"
            ).pack(side="left")

            tk.Button(
                row, text="Eliminar", relief="flat", bd=0, cursor="hand2",
                bg=self.theme.bg_window, fg="#CC3333",
                font=self._font_small,
                command=lambda i=aid: self.on_delete_alarm and self.on_delete_alarm(i)
            ).pack(side="left", padx=4)

            self._alarm_rows[aid] = row

    def show_alarm_alert(self, label: str) -> None:
        msg = f"¡Alarma activada!\n{label}" if label else "¡Alarma activada!"
        messagebox.showinfo("🔔 Alarma", msg)

    def _build_tab_stopwatch(self) -> None:
        t = self.theme
        frame = tk.Frame(self.notebook, bg=t.bg_window, pady=8)
        self.notebook.add(frame, text="Cronómetro")

        self.lbl_stopwatch = tk.Label(
            frame, text="00:00.00", font=self._font_mono,
            bg=t.bg_window, fg=t.text_readout
        )
        self.lbl_stopwatch.pack(pady=(4, 8))

        btn_row = tk.Frame(frame, bg=t.bg_window)
        btn_row.pack()

        self.btn_sw_start = tk.Button(
            btn_row, text="Iniciar", width=8, **self._btn_style(),
            command=lambda: self.on_stopwatch_start and self.on_stopwatch_start()
        )
        self.btn_sw_start.pack(side="left", padx=4)

        self.btn_sw_pause = tk.Button(
            btn_row, text="Pausar", width=8, **self._btn_style(),
            command=lambda: self.on_stopwatch_pause and self.on_stopwatch_pause()
        )
        self.btn_sw_pause.pack(side="left", padx=4)

        self.btn_sw_reset = tk.Button(
            btn_row, text="Reiniciar", width=8, **self._btn_style(),
            command=lambda: self.on_stopwatch_reset and self.on_stopwatch_reset()
        )
        self.btn_sw_reset.pack(side="left", padx=4)

    def update_stopwatch(self, elapsed: float) -> None:
        total_cs = int(elapsed * 100)
        minutes  = total_cs // 6000
        seconds  = (total_cs % 6000) // 100
        centis   = total_cs % 100
        self.lbl_stopwatch.config(text=f"{minutes:02d}:{seconds:02d}.{centis:02d}")

    def _build_tab_timer(self) -> None:
        t = self.theme
        frame = tk.Frame(self.notebook, bg=t.bg_window, pady=8)
        self.notebook.add(frame, text="Temporizador")

        set_row = tk.Frame(frame, bg=t.bg_window)
        set_row.pack()

        for label, var_name, max_val in [
            ("h", "_timer_h_var", 23),
            ("m", "_timer_m_var", 59),
            ("s", "_timer_s_var", 59),
        ]:
            setattr(self, var_name, tk.StringVar(value="00"))
            tk.Spinbox(
                set_row, from_=0, to=max_val,
                textvariable=getattr(self, var_name),
                width=3, format="%02.0f"
            ).pack(side="left", padx=1)
            tk.Label(set_row, text=label, font=self._font_small,
                     bg=t.bg_window, fg=t.text_label).pack(side="left", padx=(0, 6))

        tk.Button(
            set_row, text="Establecer", **self._btn_style(),
            command=self._set_timer_clicked
        ).pack(side="left", padx=(8, 0))

        self.lbl_timer = tk.Label(
            frame, text="00:00:00", font=self._font_mono,
            bg=t.bg_window, fg=t.text_readout
        )
        self.lbl_timer.pack(pady=(8, 6))

        btn_row = tk.Frame(frame, bg=t.bg_window)
        btn_row.pack()

        self.btn_timer_start = tk.Button(
            btn_row, text="Iniciar", width=8, **self._btn_style(),
            command=lambda: self.on_timer_start and self.on_timer_start()
        )
        self.btn_timer_start.pack(side="left", padx=4)

        self.btn_timer_pause = tk.Button(
            btn_row, text="Pausar", width=8, **self._btn_style(),
            command=lambda: self.on_timer_pause and self.on_timer_pause()
        )
        self.btn_timer_pause.pack(side="left", padx=4)

        self.btn_timer_reset = tk.Button(
            btn_row, text="Reiniciar", width=8, **self._btn_style(),
            command=lambda: self.on_timer_reset and self.on_timer_reset()
        )
        self.btn_timer_reset.pack(side="left", padx=4)

    def _set_timer_clicked(self) -> None:
        try:
            h = int(self._timer_h_var.get())
            m = int(self._timer_m_var.get())
            s = int(self._timer_s_var.get())
            total = h * 3600 + m * 60 + s
        except ValueError:
            messagebox.showerror("Error", "Valores de temporizador inválidos.")
            return
        if self.on_timer_set:
            self.on_timer_set(total)

    def update_timer(self, remaining: float, finished: bool) -> None:
        total_s = int(remaining)
        h = total_s // 3600
        m = (total_s % 3600) // 60
        s = total_s % 60
        color = self.theme.ui_status_adj if finished else self.theme.text_readout
        self.lbl_timer.config(text=f"{h:02d}:{m:02d}:{s:02d}", fg=color)
        if finished:
            self.lbl_timer.config(text="¡TIEMPO!")

    def _draw_static_face(self) -> None:
        c  = self.canvas
        cx = cy = CENTER
        r  = CLOCK_RADIUS
        t  = self.theme

        c.create_oval(
            cx - r + 6, cy - r + 6, cx + r + 6, cy + r + 6,
            fill=t.face_shadow, outline=""
        )
        c.create_oval(cx - r, cy - r, cx + r, cy + r,
                      fill=t.face_rim, outline="", width=0)
        c.create_oval(cx - r + 8, cy - r + 8, cx + r - 8, cy + r - 8,
                      fill=t.face_rim_inner, outline="", width=0)
        face_r = r - 14
        c.create_oval(cx - face_r, cy - face_r, cx + face_r, cy + face_r,
                      fill=t.face_fill, outline="", width=0)

        for hour in range(12):
            angle = hour * 30
            ox, oy = polar_to_xy(angle, face_r - 4,  cx, cy)
            ix, iy = polar_to_xy(angle, face_r - 22, cx, cy)
            c.create_line(ox, oy, ix, iy, fill=t.tick_major, width=3, capstyle="round")

        for minute in range(60):
            if minute % 5 == 0:
                continue
            angle = minute * 6
            ox, oy = polar_to_xy(angle, face_r - 4,  cx, cy)
            ix, iy = polar_to_xy(angle, face_r - 12, cx, cy)
            c.create_line(ox, oy, ix, iy, fill=t.tick_minor, width=1)

        num_font = tkfont.Font(family="Georgia", size=16, weight="bold")
        for hour in range(1, 13):
            angle = hour * 30
            nx, ny = polar_to_xy(angle, face_r - 38, cx, cy)
            c.create_text(nx, ny, text=str(hour), font=num_font, fill=t.number_color)

    def redraw_face(self, new_theme: Theme) -> None:
        self.theme = new_theme
        self.canvas.configure(bg=new_theme.bg_canvas)
        self._clock_container.configure(bg=new_theme.bg_canvas)
        self.root.configure(bg=new_theme.bg_window)
        self.canvas.delete("all")
        self._draw_static_face()
        self._apply_theme_to_widgets(new_theme)

    def _apply_theme_to_widgets(self, t: Theme) -> None:
        self.lbl_title.config(bg=t.bg_window, fg=t.text_title)
        self.lbl_readout.config(bg=t.bg_window, fg=t.text_readout)
        self.lbl_status.config(bg=t.bg_window, fg=t.text_label)
        if hasattr(self, "lbl_tz_display"):
            self.lbl_tz_display.config(bg=t.bg_window, fg=t.text_label)
        if hasattr(self, "_city_label"):
            self._city_label.config(bg=t.bg_window, fg=t.text_readout)
        if hasattr(self, "_color_swatches"):
            for field_name, swatch in self._color_swatches.items():
                swatch.config(bg=getattr(t, field_name))

    def update_hands(
        self,
        now: "datetime.datetime",
        adjusting: bool,
        offset_seconds: int,
        hour_format_24: bool,
        timezone_name: str,
    ) -> None:
        fmt = "%H:%M:%S" if hour_format_24 else "%I:%M:%S %p"
        time_str = now.strftime(fmt)

        h = now.hour % 12
        m = now.minute
        s = now.second

        second_angle = s * 6
        minute_angle = (m + s / 60) * 6
        hour_angle   = (h + m / 60) * 30

        c  = self.canvas
        cx = cy = CENTER
        t  = self.theme
        fr = CLOCK_RADIUS - 14

        c.delete("hand")

        h_poly = hand_polygon(hour_angle, fr * 0.55, 7, tail=15, cx=cx, cy=cy)
        c.create_polygon(h_poly, fill=t.hand_hour, outline="", smooth=False, tags="hand")

        m_poly = hand_polygon(minute_angle, fr * 0.82, 5, tail=20, cx=cx, cy=cy)
        c.create_polygon(m_poly, fill=t.hand_minute, outline="", smooth=False, tags="hand")

        s_tip_x,  s_tip_y  = polar_to_xy(second_angle,       fr * 0.90, cx, cy)
        s_tail_x, s_tail_y = polar_to_xy(second_angle + 180, fr * 0.18, cx, cy)
        c.create_line(
            s_tail_x, s_tail_y, s_tip_x, s_tip_y,
            fill=t.hand_second, width=2, capstyle="round", tags="hand"
        )

        jewel_r = 7
        c.create_oval(
            cx - jewel_r, cy - jewel_r, cx + jewel_r, cy + jewel_r,
            fill=t.center_dot, outline=t.face_rim, width=2, tags="hand"
        )

        self.lbl_readout.config(
            text=time_str,
            fg=self.theme.ui_status_adj if adjusting else self.theme.text_readout,
        )

        if adjusting:
            self.lbl_status.config(
                text="Ajustando manecillas - reloj en pausa",
                fg=self.theme.ui_status_adj
            )
        elif offset_seconds == 0:
            self.lbl_status.config(
                text=f"Sincronizado con reloj del sistema  |  {timezone_name}",
                fg=self.theme.ui_status_ok
            )
        else:
            sign  = "+" if offset_seconds > 0 else ""
            h_off = offset_seconds // 3600
            m_off = (abs(offset_seconds) % 3600) // 60
            self.lbl_status.config(
                text=f"Hora personalizada: {sign}{h_off}h {abs(m_off):02d}m  |  {timezone_name}",
                fg=self.theme.ui_status_warn
            )

        if hasattr(self, "tz_var"):
            self.tz_var.set(timezone_name)