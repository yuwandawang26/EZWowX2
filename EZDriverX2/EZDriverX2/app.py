"""Application entrypoint for running one external profile."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from .config.defaults import register_default_config
from .config.macros import MacroRegistry
from .config.registry import ConfigRegistry
from .contracts.profile import RotationProfile
from .engine.executor import ActionExecutor
from .engine.loop import RotationLoopEngine
from .input.win32_sender import Win32Sender
from .transport.bridge_client import BridgeClient
from .ui.main_window import MainWindow


def _resolve_profile_icon_path(profile: RotationProfile) -> Path | None:
    icons_dir = Path(__file__).resolve().parent / "icons"
    default_icon = icons_dir / "default.ico"

    icon_name = getattr(profile, "ICON", None)
    if isinstance(icon_name, str) and icon_name.strip():
        trimmed = icon_name.strip()
        custom_path = Path(trimmed)
        if custom_path.is_absolute() and custom_path.is_file():
            return custom_path

        packaged_custom = icons_dir / trimmed
        if packaged_custom.is_file():
            return packaged_custom

        cwd_custom = Path.cwd() / trimmed
        if cwd_custom.is_file():
            return cwd_custom

    if default_icon.is_file():
        return default_icon
    return None


def _resolve_profile_icon(profile: RotationProfile) -> QIcon | None:
    path = _resolve_profile_icon_path(profile)
    if path is None:
        return None
    icon = QIcon(str(path))
    if icon.isNull():
        return None
    return icon


def run_profile(profile: RotationProfile, api_url: str = "http://127.0.0.1:65131/api") -> int:
    config = ConfigRegistry()
    register_default_config(config)

    macros = MacroRegistry()
    profile.setup(config, macros)

    sender = Win32Sender()
    bridge_client = BridgeClient(api_url)
    executor = ActionExecutor(macros=macros, sender=sender)
    engine = RotationLoopEngine(
        profile=profile,
        config=config,
        bridge_client=bridge_client,
        executor=executor,
    )

    app_instance = QApplication.instance()
    if isinstance(app_instance, QApplication):
        app = app_instance
    else:
        app = QApplication(sys.argv)
    icon = _resolve_profile_icon(profile)
    if icon is not None:
        app.setWindowIcon(icon)

    window = MainWindow(engine=engine, config=config, window_sender=sender)
    if icon is not None:
        window.setWindowIcon(icon)
    window.show()
    return app.exec()
