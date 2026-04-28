from dataclasses import dataclass, field
from typing import ClassVar


@dataclass
class Theme:
    name: str
    bg_window: str
    bg_canvas: str
    face_fill: str
    face_rim: str
    face_rim_inner: str
    face_shadow: str
    tick_major: str
    tick_minor: str
    number_color: str
    hand_hour: str
    hand_minute: str
    hand_second: str
    center_dot: str
    text_title: str
    text_label: str
    text_readout: str
    ui_btn_bg: str
    ui_btn_fg: str
    ui_btn_active: str
    ui_status_ok: str
    ui_status_warn: str
    ui_status_adj: str

    _PRESETS: ClassVar[dict[str, "Theme"]] = {}

    @classmethod
    def register(cls, theme: "Theme") -> None:
        cls._PRESETS[theme.name] = theme

    @classmethod
    def get(cls, name: str) -> "Theme":
        return cls._PRESETS.get(name, cls._PRESETS["Claro"])

    @classmethod
    def preset_names(cls) -> list[str]:
        return sorted(cls._PRESETS.keys())

    def copy_with(self, **kwargs) -> "Theme":
        import dataclasses
        return dataclasses.replace(self, **kwargs)


Theme.register(Theme(
    name="Claro",
    bg_window="#EAEAF0",
    bg_canvas="#EAEAF0",
    face_fill="#F8F8F0",
    face_rim="#2C2C3E",
    face_rim_inner="#3E3E55",
    face_shadow="#D0D0C8",
    tick_major="#2C2C3E",
    tick_minor="#9090A8",
    number_color="#1A1A2E",
    hand_hour="#1A1A2E",
    hand_minute="#2C2C3E",
    hand_second="#E63946",
    center_dot="#E63946",
    text_title="#2C2C3E",
    text_label="#555555",
    text_readout="#2C2C3E",
    ui_btn_bg="#2C2C3E",
    ui_btn_fg="#FFFFFF",
    ui_btn_active="#E63946",
    ui_status_ok="#27AE60",
    ui_status_warn="#E67E22",
    ui_status_adj="#E63946",
))

Theme.register(Theme(
    name="Oscuro",
    bg_window="#0F0F1A",
    bg_canvas="#0F0F1A",
    face_fill="#1C1C2E",
    face_rim="#0A0A14",
    face_rim_inner="#141428",
    face_shadow="#080812",
    tick_major="#A0A0C0",
    tick_minor="#505070",
    number_color="#D0D0F0",
    hand_hour="#C8C8E8",
    hand_minute="#A0A0D0",
    hand_second="#FF4D5A",
    center_dot="#FF4D5A",
    text_title="#D0D0F0",
    text_label="#8080A0",
    text_readout="#D0D0F0",
    ui_btn_bg="#252540",
    ui_btn_fg="#D0D0F0",
    ui_btn_active="#FF4D5A",
    ui_status_ok="#2ECC71",
    ui_status_warn="#F39C12",
    ui_status_adj="#FF4D5A",
))