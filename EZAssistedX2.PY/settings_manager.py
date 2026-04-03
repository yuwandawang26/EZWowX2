import json
from pathlib import Path


class SettingsManager:
    """设置管理器"""

    SETTINGS_FILE = "settings.json"

    def __init__(self):
        self.settings = self._load()

    def _load(self):
        if Path(self.SETTINGS_FILE).exists():
            try:
                with open(self.SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return self._default()
        return self._default()

    def _default(self):
        return {
            "hotkey": "q",
            "window_position": None,
            "window_expanded": False,
            "selected_window": None,
        }

    def save(self):
        try:
            with open(self.SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"保存设置失败: {e}")

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value
        self.save()