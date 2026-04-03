# EZWowX2 浮窗 UI 实施指南

**文档版本**: 5.3
**创建日期**: 2026-04-03
**最后更新**: 2026-04-03 (清理与优化)
**参考文档**: UI plan.md (v7.2)
**实施目标**: EZAssistedX2.PY (Python + PySide6)

---

## 1. 实施概述

### 1.1 目标文件

| 文件 | 路径 | 说明 |
|-----|------|------|
| 主程序 | `D:\EZWowX2\EZAssistedX2.PY\EZAssistedX2.py` | 需要重构添加浮窗 |
| 依赖 | `D:\EZWowX2\EZAssistedX2.PY\requirements.txt` | 需要添加依赖 |

### 1.2 新增文件清单（当前已创建）

| 文件 | 路径 | 说明 | 状态 |
|-----|------|------|------|
| 浮窗组件 | `D:\EZWowX2\EZAssistedX2.PY\floating_window.py` | 浮窗主组件（含📝日志按钮） | ✅ 已创建 |
| 快捷键管理 | `D:\EZWowX2\EZAssistedX2.PY\hotkey_manager.py` | 混合方案（Hook+轮询） | ✅ 已创建并优化 |
| 技能名称管理 | `D:\EZWowX2\EZAssistedX2.PY\skill_name_manager.py` | 技能名称映射管理 | ✅ 已创建 |
| 设置管理 | `D:\EZWowX2\EZAssistedX2.PY\settings_manager.py` | JSON设置持久化 | ✅ 已创建 |
| 窗口枚举器 | `D:\EZWowX2\EZAssistedX2.PY\window_enumerator.py` | WoW窗口检测与枚举 | ✅ 已创建并增强 |
| 技能名称编辑器 | `D:\EZWowX2\EZAssistedX2.PY\skill_name_editor.py` | 技能名称编辑对话框 | ✅ 已创建 |
| **智能日志** | **`D:\EZWowX2\EZAssistedX2.PY\smart_logging.py`** | **SmartLogManager日志管理** | **✅ 新增** |
| 配置文件 | `D:\EZWowX2\EZAssistedX2.PY\skill_names.json` | 技能名称配置（运行时生成） | ✅ 自动生成 |
| 配置文件 | `D:\EZWowX2\EZAssistedX2.PY\settings.json` | 用户设置（运行时生成） | ✅ 自动生成 |
| 启动脚本 | `D:\EZWowX2\EZAssistedX2.PY\Start.bat` | 无CMD窗口启动（pythonw） | ✅ 已优化 |
| 启动脚本 | `D:\EZWowX2\EZAssistedX2.PY\启动EZAssistedX2.bat` | 带提示信息启动（python） | ✅ 保留备用 |

### 1.3 实施阶段

| 阶段 | 内容 | 工期 |
|-----|------|------|
| Phase 1 | 基础浮窗框架 | 0.5天 |
| Phase 2 | 状态显示、按键日志、快捷键 | 0.5天 |
| Phase 3 | 设置保存加载、窗口选择器 | 0.5天 |
| Phase 4 | 状态统计、技能名称编辑 | 0.5天 |
| Phase 5 | 托盘功能、最终优化 | 0.5天 |

---

## 2. 实施准备

### 2.1 环境依赖

**当前依赖文件**: `D:\EZWowX2\EZAssistedX2.PY\requirements.txt`

**已安装的核心依赖**:
```txt
PySide6>=6.6.0
opencv-python>=4.8.0
numpy>=1.24.0
dxcam>=0.1.0
pywin32>=300
comtypes>=1.2.0
```

> **注意 (v5.3更新)**: `keyboard`库已从依赖中移除，改用Win32 API混合方案。

---

## 3. Phase 1: 基础浮窗框架

### 3.1 浮窗主类

**新建文件**: `D:\EZWowX2\EZAssistedX2.PY\floating_window.py`

```python
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox
from PySide6.QtCore import Qt, QPoint, QTimer
from PySide6.QtGui import QPainter, QColor, QBrush, QKeyEvent

class FloatingWindow(QWidget):
    """游戏外浮窗主窗口"""

    COMPACT_WIDTH = 240
    COMPACT_HEIGHT = 160
    EXPANDED_WIDTH = 240
    EXPANDED_HEIGHT = 280
    WINDOW_OPACITY = 0.80

    COLORS = {
        'background': QColor(25, 25, 30, 200),
        'border': QColor(60, 60, 70, 220),
        'text': QColor(210, 210, 220),
        'status_running': QColor(80, 220, 120),
        'status_paused': QColor(255, 200, 50),
        'status_error': QColor(255, 80, 80),
        'button_bg': QColor(50, 50, 60),
        'button_hover': QColor(70, 70, 85),
        'hotkey_highlight': QColor(100, 180, 255),
        'skill_highlight': QColor(255, 220, 100),
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_expanded = False
        self._is_paused = False
        self._is_dragging = False
        self._drag_position = QPoint()
        self._current_hotkey = 'q'
        self._is_capturing_hotkey = False
        self._hotkey_callback = None

        self._runtime_seconds = 0
        self._key_count = 0
        self._error_count = 0
        self._runtime_timer = QTimer()
        self._runtime_timer.timeout.connect(self._update_runtime)

        self._init_window()
        self._init_ui()

    def _init_window(self):
        self.setFixedSize(self.COMPACT_WIDTH, self.COMPACT_HEIGHT)
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowOpacity(self.WINDOW_OPACITY)

    def _init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(8, 8, 8, 8)
        self.main_layout.setSpacing(4)

        self._create_status_bar()
        self._create_key_log_area()
        self._create_hotkey_display()
        self._create_expanded_panel()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(self.COLORS['background']))
        painter.setPen(self.COLORS['border'])
        painter.drawRoundedRect(self.rect(), 8, 8)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = True
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self._is_dragging:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._is_dragging = False
        event.accept()

    def keyPressEvent(self, event):
        if self._is_capturing_hotkey:
            if event.key() == Qt.Key_Escape:
                self.cancel_hotkey_capture()
                return

            key = event.text()
            if key and len(key) == 1 and key.isalpha():
                self._is_capturing_hotkey = False
                self.set_hotkey(key.lower())
                if self._hotkey_callback:
                    self._hotkey_callback(key.lower())
            else:
                self.hotkey_display.setText("[无效]")
                QTimer.singleShot(500, lambda: self.set_hotkey(self._current_hotkey))
        else:
            super().keyPressEvent(event)

    def toggle_expand(self):
        self._is_expanded = not self._is_expanded
        if self._is_expanded:
            self.setFixedSize(self.EXPANDED_WIDTH, self.EXPANDED_HEIGHT)
            self.settings_button.setText("▼")
        else:
            self.setFixedSize(self.COMPACT_WIDTH, self.COMPACT_HEIGHT)
            self.settings_button.setText("⚙")

    def _create_status_bar(self):
        status_layout = QHBoxLayout()

        self.status_indicator = QLabel("●")
        self.status_indicator.setStyleSheet("color: rgb(80, 220, 120); font-size: 14pt;")
        status_layout.addWidget(self.status_indicator)

        self.status_label = QLabel("运行中")
        self.status_label.setStyleSheet("color: rgb(210, 210, 220); font-size: 11pt; font-weight: bold;")
        status_layout.addWidget(self.status_label)

        self.skill_label = QLabel("")
        self.skill_label.setStyleSheet("color: rgb(255, 220, 100); font-size: 12pt; font-weight: bold;")
        status_layout.addWidget(self.skill_label)

        status_layout.addStretch()

        self.pause_button = QLabel("⏸")
        self.pause_button.setFixedSize(24, 24)
        self.pause_button.setStyleSheet("""
            background-color: rgb(50, 50, 60);
            border-radius: 4px;
            color: rgb(210, 210, 220);
            font-size: 12pt;
        """)
        self.pause_button.mousePressEvent = lambda e: self._on_pause_click()
        status_layout.addWidget(self.pause_button)

        self.settings_button = QLabel("⚙")
        self.settings_button.setFixedSize(24, 24)
        self.settings_button.setStyleSheet("""
            background-color: rgb(50, 50, 60);
            border-radius: 4px;
            color: rgb(210, 210, 220);
            font-size: 12pt;
        """)
        self.settings_button.mousePressEvent = lambda e: self.toggle_expand()
        status_layout.addWidget(self.settings_button)

        self.close_button = QLabel("×")
        self.close_button.setFixedSize(24, 24)
        self.close_button.setStyleSheet("""
            background-color: rgb(50, 50, 60);
            border-radius: 4px;
            color: rgb(210, 210, 220);
            font-size: 14pt;
        """)
        self.close_button.mousePressEvent = lambda e: self.hide()
        status_layout.addWidget(self.close_button)

        self.main_layout.addLayout(status_layout)

    def _create_key_log_area(self):
        log_label = QLabel("最近按键:")
        log_label.setStyleSheet("color: rgb(180, 180, 180); font-size: 10pt;")
        self.main_layout.addWidget(log_label)

        self.key_log_widget = QWidget()
        self.key_log_layout = QVBoxLayout(self.key_log_widget)
        self.key_log_layout.setContentsMargins(4, 4, 4, 4)
        self.key_log_layout.setSpacing(2)

        self.key_log_items = []
        for i in range(3):
            log_item = QLabel(f"▶ --")
            log_item.setStyleSheet("color: rgb(150, 150, 150); font-family: Consolas; font-size: 9pt;")
            self.key_log_layout.addWidget(log_item)
            self.key_log_items.append(log_item)

        self.main_layout.addWidget(self.key_log_widget)

    def _create_hotkey_display(self):
        hotkey_layout = QHBoxLayout()

        hotkey_label = QLabel("启停快捷键:")
        hotkey_label.setStyleSheet("color: rgb(180, 180, 180); font-size: 10pt;")
        hotkey_layout.addWidget(hotkey_label)

        hotkey_layout.addStretch()

        self.hotkey_display = QLabel("[Q]")
        self.hotkey_display.setFixedSize(40, 24)
        self.hotkey_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hotkey_display.setStyleSheet("""
            background-color: rgb(50, 50, 60);
            border-radius: 4px;
            color: rgb(100, 180, 255);
            font-family: Consolas;
            font-size: 11pt;
            font-weight: bold;
            padding: 2px 8px;
        """)
        self.hotkey_display.mousePressEvent = lambda e: self._on_hotkey_edit_click()
        hotkey_layout.addWidget(self.hotkey_display)

        self.hotkey_edit_button = QLabel("✎")
        self.hotkey_edit_button.setFixedSize(20, 24)
        self.hotkey_edit_button.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hotkey_edit_button.setStyleSheet("""
            background-color: rgb(50, 50, 60);
            border-radius: 4px;
            color: rgb(180, 180, 180);
            font-size: 11pt;
        """)
        self.hotkey_edit_button.mousePressEvent = lambda e: self._on_hotkey_edit_click()
        hotkey_layout.addWidget(self.hotkey_edit_button)

        self.main_layout.addLayout(hotkey_layout)

    def _create_expanded_panel(self):
        self.expanded_widget = QWidget()
        self.expanded_layout = QVBoxLayout(self.expanded_widget)
        self.expanded_layout.setContentsMargins(0, 8, 0, 0)
        self.expanded_layout.setSpacing(4)
        self.expanded_widget.setVisible(False)

        self._create_window_selector()
        self._create_stats_panel()
        self._create_skill_edit_button()

        self.main_layout.addWidget(self.expanded_widget)

    def _create_window_selector(self):
        selector_layout = QHBoxLayout()

        label = QLabel("目标窗口:")
        label.setStyleSheet("color: rgb(180, 180, 180); font-size: 10pt;")
        selector_layout.addWidget(label)

        self.window_combo = QComboBox()
        self.window_combo.setFixedHeight(22)
        self.window_combo.setStyleSheet("""
            background-color: rgb(50, 50, 60);
            color: rgb(210, 210, 220);
            border: 1px solid rgb(60, 60, 70);
            border-radius: 4px;
            padding: 2px 4px;
        """)
        selector_layout.addWidget(self.window_combo)

        self.expanded_layout.addLayout(selector_layout)

    def _create_stats_panel(self):
        stats_label = QLabel("状态统计:")
        stats_label.setStyleSheet("color: rgb(180, 180, 180); font-size: 10pt;")
        self.expanded_layout.addWidget(stats_label)

        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("color: rgb(150, 150, 150); font-family: Consolas; font-size: 9pt;")
        self.stats_label.setText(
            "├─ 运行时间: 00:00:00\n"
            "├─ 已发送按键: 0\n"
            "└─ 错误计数: 0"
        )
        self.expanded_layout.addWidget(self.stats_label)

    def _create_skill_edit_button(self):
        btn_layout = QHBoxLayout()

        self.skill_edit_button = QLabel("编辑技能名称")
        self.skill_edit_button.setFixedHeight(24)
        self.skill_edit_button.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.skill_edit_button.setStyleSheet("""
            background-color: rgb(50, 50, 60);
            border-radius: 4px;
            color: rgb(210, 210, 220);
            font-size: 10pt;
        """)
        self.skill_edit_button.mousePressEvent = lambda e: self._on_edit_skills_click()
        btn_layout.addWidget(self.skill_edit_button)

        self.expanded_layout.addLayout(btn_layout)

    def _on_pause_click(self):
        self._is_paused = not self._is_paused
        if self._is_paused:
            self.status_indicator.setStyleSheet("color: rgb(255, 200, 50); font-size: 14pt;")
            self.status_label.setText("已暂停")
            self.pause_button.setText("▶")
            self._runtime_timer.stop()
        else:
            self.status_indicator.setStyleSheet("color: rgb(80, 220, 120); font-size: 14pt;")
            self.status_label.setText("运行中")
            self.pause_button.setText("⏸")
            self._runtime_timer.start(1000)

    def _on_hotkey_edit_click(self):
        self.start_hotkey_capture(self._on_hotkey_changed)

    def _on_hotkey_changed(self, new_hotkey: str):
        pass

    def _on_edit_skills_click(self):
        if self._edit_skill_callback:
            self._edit_skill_callback()

    def start_hotkey_capture(self, on_hotkey_changed):
        self._is_capturing_hotkey = True
        self._hotkey_callback = on_hotkey_changed
        self.hotkey_display.setText("[...]")
        self.hotkey_display.setStyleSheet("""
            background-color: rgb(70, 70, 85);
            border-radius: 4px;
            color: rgb(100, 180, 255);
            font-family: Consolas;
            font-size: 11pt;
            font-weight: bold;
            padding: 2px 8px;
            border: 1px solid rgb(100, 180, 255);
        """)

    def cancel_hotkey_capture(self):
        if self._is_capturing_hotkey:
            self._is_capturing_hotkey = False
            self.set_hotkey(self._current_hotkey)

    def set_hotkey(self, hotkey: str):
        self._current_hotkey = hotkey.lower()
        self.hotkey_display.setText(f"[{self._current_hotkey.upper()}]")
        self.hotkey_display.setStyleSheet("""
            background-color: rgb(50, 50, 60);
            border-radius: 4px;
            color: rgb(100, 180, 255);
            font-family: Consolas;
            font-size: 11pt;
            font-weight: bold;
            padding: 2px 8px;
        """)

    def get_current_hotkey(self) -> str:
        return self._current_hotkey

    def set_edit_skill_callback(self, callback):
        self._edit_skill_callback = callback

    def update_skill_name(self, color_key: str, skill_name: str):
        self.skill_label.setText(skill_name)

    def update_key_log(self, index: int, combo_name: str, color_key: str):
        if 0 <= index < len(self.key_log_items):
            self.key_log_items[index].setText(f"▶ {combo_name} ({color_key})")

    def update_stats(self, runtime: str, key_count: int, error_count: int):
        self.stats_label.setText(
            f"├─ 运行时间: {runtime}\n"
            f"├─ 已发送按键: {key_count}\n"
            f"└─ 错误计数: {error_count}"
        )
        self._runtime_seconds = self._parse_runtime(runtime)
        self._key_count = key_count
        self._error_count = error_count

    def _parse_runtime(self, runtime: str) -> int:
        try:
            parts = runtime.split(':')
            if len(parts) == 3:
                h, m, s = map(int, parts)
                return h * 3600 + m * 60 + s
        except:
            pass
        return 0

    def _update_runtime(self):
        self._runtime_seconds += 1
        h = self._runtime_seconds // 3600
        m = (self._runtime_seconds % 3600) // 60
        s = self._runtime_seconds % 60
        runtime = f"{h:02d}:{m:02d}:{s:02d}"
        self.stats_label.setText(
            f"├─ 运行时间: {runtime}\n"
            f"├─ 已发送按键: {self._key_count}\n"
            f"└─ 错误计数: {self._error_count}"
        )

    def increment_key_count(self):
        self._key_count += 1
        self._update_runtime()

    def increment_error_count(self):
        self._error_count += 1
        self._update_runtime()

    def start_runtime_timer(self):
        self._runtime_timer.start(1000)

    def stop_runtime_timer(self):
        self._runtime_timer.stop()

    def get_selected_window(self):
        return self.window_combo.currentData()

    def refresh_window_list(self, windows: list):
        current = self.window_combo.currentText()
        self.window_combo.clear()
        for hwnd, title in windows:
            self.window_combo.addItem(title[:30], hwnd)
        index = self.window_combo.findText(current)
        if index >= 0:
            self.window_combo.setCurrentIndex(index)
```

**预期效果**:
- 透明度80%（与UI Plan一致）
- 紧凑模式: 240x160
- 展开模式: 240x280
- 快捷键捕获支持ESC取消
- 内置窗口选择器、状态统计、技能编辑按钮

---

## 4. Phase 2: 快捷键管理和设置保存

### 4.1 快捷键管理器

**新建文件**: `D:\EZWowX2\EZAssistedX2.PY\hotkey_manager.py`

```python
import keyboard
import threading
import ctypes
from typing import Callable, Optional, Tuple

user32 = ctypes.windll.user32


class GlobalHotkeyManager:
    """全局快捷键管理器"""

    MOD_ctrl = 0x0002
    MOD_shift = 0x0004
    MOD_alt = 0x0001
    MOD_norepeat = 0x4000

    def __init__(self):
        self._hooks = []
        self._callbacks = {}
        self._combo_handles = {}
        self._running = False

    def register(self, key: str, callback: Callable):
        key = key.lower()

        def wrapped_callback(e):
            if e.event_type == 'down' and not e.is_repeated:
                callback()

        hook = keyboard.on_press_key(key, wrapped_callback, suppress=False)
        self._hooks.append(hook)
        self._callbacks[key] = callback

    def register_combo(self, modifiers: Tuple[str, ...], key: str, callback: Callable):
        modifier_code = 0
        for m in modifiers:
            if m == 'ctrl':
                modifier_code |= self.MOD_ctrl
            elif m == 'shift':
                modifier_code |= self.MOD_shift
            elif m == 'alt':
                modifier_code |= self.MOD_alt

        modifier_code |= self.MOD_norepeat
        hotkey_id = abs(hash((modifiers, key))) % 10000

        try:
            ret = user32.RegisterHotKey(None, hotkey_id, modifier_code, ord(key.upper()))
            if ret:
                self._combo_handles[hotkey_id] = (modifiers, key, callback)
        except Exception as e:
            print(f"注册组合键异常: {e}")

    def unregister(self, key: str):
        key = key.lower()
        if key in self._callbacks:
            del self._callbacks[key]

    def unregister_all(self):
        for hook in self._hooks:
            keyboard.unhook(hook)
        self._hooks.clear()
        self._callbacks.clear()

        for hotkey_id in list(self._combo_handles.keys()):
            user32.UnregisterHotKey(None, hotkey_id)
        self._combo_handles.clear()

    def start_listening(self, blocking: bool = True):
        self._running = True
        if blocking:
            self._run_message_loop()
        else:
            self._listener_thread = threading.Thread(target=self._run_message_loop, daemon=True)
            self._listener_thread.start()

    def _run_message_loop(self):
        from ctypes import wintypes
        MSG = wintypes.MSG
        WM_HOTKEY = 0x0312
        msg = MSG()
        while self._running:
            ret = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
            if ret == 0:
                break
            if msg.message == WM_HOTKEY:
                hotkey_id = msg.wParam
                if hotkey_id in self._combo_handles:
                    _, _, callback = self._combo_handles[hotkey_id]
                    callback()
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

    def stop_listening(self):
        self._running = False
        self.unregister_all()
```

### 4.2 设置管理器

**新建文件**: `D:\EZWowX2\EZAssistedX2.PY\settings_manager.py`

```python
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
```

### 4.3 窗口枚举器

**新建文件**: `D:\EZWowX2\EZAssistedX2.PY\window_enumerator.py`

```python
import win32gui
import win32con


class WindowEnumerator:
    """窗口枚举器"""

    @staticmethod
    def enumerate_windows():
        result = []

        def callback(hwnd, extra):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and len(title) > 0:
                    try:
                        cls_name = win32gui.GetClassName(hwnd)
                        if cls_name not in ['WorkerW', 'Shell_TrayWnd', 'Progman']:
                            result.append((hwnd, title))
                    except:
                        pass

        win32gui.EnumWindows(callback, None)
        return result

    @staticmethod
    def get_window_title(hwnd: int) -> str:
        try:
            return win32gui.GetWindowText(hwnd)
        except:
            return ""
```

---

## 5. Phase 3: 技能名称管理

### 5.1 技能名称管理器

**新建文件**: `D:\EZWowX2\EZAssistedX2.PY\skill_name_manager.py`

```python
import json
from pathlib import Path
from typing import Dict


DEFAULT_SKILL_NAMES: Dict[str, str] = {
    "13,255,0": "惩击",
    "0,255,64": "治疗之触",
    "0,255,140": "清晰术",
    "0,255,217": "护星术",
    "0,255,255": "野性成长",
    "13,255,255": "滋养",
    "64,255,0": "愈合",
    "140,255,0": "回春术",
    "217,255,0": "生命绽放",
    "255,255,0": "驱散",
    "255,217,0": "联结治疗",
    "255,140,0": "野性印记",
    "255,64,0": "星火术",
    "255,0,0": "愤怒",
    "255,0,64": "月火术",
    "255,0,140": "精灵火",
    "255,0,217": "台风",
    "217,0,255": "纠缠根须",
    "140,0,255": "自然之力",
    "89,255,0": "自然防御",
}


class SkillNameManager:
    """技能名称管理器"""

    def __init__(self, config_path: str = "skill_names.json"):
        self.config_path = Path(config_path)
        self.skills: Dict[str, dict] = {}
        self._load_config()

    def _load_config(self):
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.skills = data.get("skills", {})
            except (json.JSONDecodeError, IOError):
                self.skills = self._default_config()
        else:
            self.skills = self._default_config()

    def _default_config(self) -> Dict[str, dict]:
        return {
            color_key: {"name": name, "enabled": True}
            for color_key, name in DEFAULT_SKILL_NAMES.items()
        }

    def get_name(self, color_key: str) -> str:
        return self.skills.get(color_key, {}).get("name", "未知")

    def set_name(self, color_key: str, name: str):
        if color_key in self.skills:
            self.skills[color_key]["name"] = name
            self._save_config()

    def get_all_skills(self) -> Dict[str, dict]:
        return self.skills.copy()

    def reset_all(self):
        self.skills = self._default_config()
        self._save_config()

    def _save_config(self):
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(
                    {"version": 1, "skills": self.skills},
                    f,
                    ensure_ascii=False,
                    indent=2
                )
        except IOError as e:
            print(f"保存技能名称配置失败: {e}")
```

### 5.2 技能名称编辑器

**新建文件**: `D:\EZWowX2\EZAssistedX2.PY\skill_name_editor.py`

```python
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea, QWidget
from PySide6.QtCore import Qt


class SkillNameEditor(QDialog):
    """技能名称编辑器对话框"""

    def __init__(self, skill_manager, parent=None):
        super().__init__(parent)
        self.skill_manager = skill_manager
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("编辑技能名称")
        self.setFixedSize(300, 400)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)

        layout = QVBoxLayout(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        self.edits = {}
        for color_key, data in self.skill_manager.get_all_skills().items():
            item_layout = QHBoxLayout()

            color_label = QLabel(color_key)
            color_label.setFixedWidth(80)
            color_label.setStyleSheet("color: rgb(150, 150, 150); font-family: Consolas; font-size: 9pt;")
            item_layout.addWidget(color_label)

            name_edit = QLineEdit(data['name'])
            name_edit.setMaxLength(8)
            name_edit.setFixedHeight(22)
            name_edit.setStyleSheet("""
                background-color: rgb(50, 50, 60);
                color: rgb(210, 210, 220);
                border: 1px solid rgb(60, 60, 70);
                border-radius: 4px;
                padding: 2px 4px;
            """)
            item_layout.addWidget(name_edit)

            self.edits[color_key] = name_edit
            scroll_layout.addLayout(item_layout)

        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        btn_layout = QHBoxLayout()

        reset_btn = QPushButton("重置")
        reset_btn.clicked.connect(self._on_reset)
        btn_layout.addWidget(reset_btn)

        btn_layout.addStretch()

        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(save_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    def _on_reset(self):
        self.skill_manager.reset_all()
        for color_key, edit in self.edits.items():
            edit.setText(self.skill_manager.get_name(color_key))

    def _on_save(self):
        for color_key, edit in self.edits.items():
            new_name = edit.text().strip()
            if new_name:
                self.skill_manager.set_name(color_key, new_name)
        self.accept()
```

---

## 6. Phase 4: 主程序集成

### 6.1 主程序修改

**修改文件**: `D:\EZWowX2\EZAssistedX2.PY\EZAssistedX2.py`

```python
import sys
from PySide6.QtWidgets import QApplication, QStyle
from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QAction

from floating_window import FloatingWindow
from hotkey_manager import GlobalHotkeyManager
from settings_manager import SettingsManager
from skill_name_manager import SkillNameManager
from skill_name_editor import SkillNameEditor
from window_enumerator import WindowEnumerator


class EZWowX2App:
    def __init__(self):
        self.app = QApplication(sys.argv)

        self.settings = SettingsManager()
        self.skill_manager = SkillNameManager()

        self.floating_window = FloatingWindow()
        self.floating_window.show()

        self.hotkey_manager = GlobalHotkeyManager()

        self._setup_hotkeys()
        self._setup_tray()
        self._setup_callbacks()
        self._refresh_windows()

        self.floating_window.start_runtime_timer()

    def _setup_hotkeys(self):
        is_paused = [False]

        def toggle_pause():
            is_paused[0] = not is_paused[0]
            self.floating_window._on_pause_click()
            if not is_paused[0]:
                self.floating_window.increment_key_count()

        def update_hotkey(new_hotkey: str):
            old_hotkey = self.floating_window.get_current_hotkey()
            self.hotkey_manager.unregister(old_hotkey)
            self.hotkey_manager.register(new_hotkey, toggle_pause)
            self.floating_window.set_hotkey(new_hotkey)
            self.settings.set('hotkey', new_hotkey)

        self.floating_window._hotkey_callback = update_hotkey

        saved_hotkey = self.settings.get('hotkey', 'q')
        self.floating_window.set_hotkey(saved_hotkey)
        self.hotkey_manager.register(saved_hotkey, toggle_pause)

        def on_expand_toggle():
            self.floating_window.toggle_expand()
            self.settings.set('window_expanded', self.floating_window._is_expanded)

        def on_show_hide():
            if self.floating_window.isVisible():
                self.floating_window.hide()
            else:
                self.floating_window.show()

        self.hotkey_manager.register_combo(('ctrl', 'shift'), 'e', on_expand_toggle)
        self.hotkey_manager.register_combo(('ctrl', 'shift'), 'h', on_show_hide)

        self.hotkey_manager.start_listening(blocking=False)

    def _setup_tray(self):
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(self.app.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        self.tray.setToolTip("EZWowX2 - 辅助工具")

        menu = QMenu()

        show_action = QAction("显示", menu)
        show_action.triggered.connect(lambda: self.floating_window.show())
        menu.addAction(show_action)

        menu.addSeparator()

        exit_action = QAction("退出", menu)
        exit_action.triggered.connect(self._on_exit)
        menu.addAction(exit_action)

        self.tray.setContextMenu(menu)
        self.tray.show()

        self.floating_window.close_button.mousePressEvent = lambda e: self.floating_window.hide()

    def _setup_callbacks(self):
        self.floating_window.set_edit_skill_callback(self._on_edit_skills)

    def _refresh_windows(self):
        windows = WindowEnumerator.enumerate_windows()
        self.floating_window.refresh_window_list(windows)

    def _on_edit_skills(self):
        dialog = SkillNameEditor(self.skill_manager, self.floating_window)
        if dialog.exec():
            pass

    def _on_exit(self):
        self.floating_window.stop_runtime_timer()
        self.hotkey_manager.stop_listening()
        self.tray.hide()
        self.app.quit()

    def run(self):
        sys.exit(self.app.exec())


def main():
    app = EZWowX2App()
    app.run()


if __name__ == "__main__":
    main()
```

---

## 7. 集成测试

### 7.1 测试清单

| 测试项 | 操作 | 预期结果 |
|-------|------|---------|
| 浮窗显示 | 运行程序 | 左上角显示240x160半透明浮窗 |
| 拖拽移动 | 拖拽窗口 | 窗口可移动 |
| 透明度 | 视觉检查 | 透明度80% |
| Q键启停 | 按Q键 | 运行/暂停状态切换 |
| ESC取消 | 捕获时按ESC | 退出捕获模式 |
| Ctrl+Shift+E | 按组合键 | 展开/收起浮窗 |
| Ctrl+Shift+H | 按组合键 | 显示/隐藏浮窗 |
| 窗口选择 | 下拉选择 | 可选择目标窗口 |
| 状态统计 | 查看展开面板 | 显示运行时间/按键计数 |
| 技能编辑 | 点击编辑按钮 | 弹出编辑对话框 |
| 托盘菜单 | 右键托盘 | 显示菜单 |
| 设置保存 | 修改后重启 | 设置保留 |

### 7.2 验收标准

| 编号 | 检查项 | 优先级 |
|-----|-------|-------|
| AC-01 | 浮窗显示 | P0 |
| AC-02 | 透明度80% | P0 |
| AC-03 | Q键启停 | P0 |
| AC-04 | ESC取消快捷键捕获 | P0 |
| AC-05 | Ctrl+Shift+E/H | P0 |
| AC-06 | 窗口选择器 | P1 |
| AC-07 | 状态统计 | P1 |
| AC-08 | 技能名称编辑 | P1 |
| AC-09 | 设置保存加载 | P1 |
| AC-10 | 托盘功能 | P1 |

---

## 8. 文件变更清单

### 8.1 新建文件

| 文件 | 说明 |
|-----|------|
| `floating_window.py` | 浮窗主组件（含窗口选择器、状态统计） |
| `hotkey_manager.py` | 快捷键管理 |
| `settings_manager.py` | 设置管理 |
| `skill_name_manager.py` | 技能名称管理 |
| `skill_name_editor.py` | 技能名称编辑器对话框 |
| `window_enumerator.py` | 窗口枚举器 |

### 8.2 修改文件

| 文件 | 修改 |
|-----|------|
| `requirements.txt` | 添加keyboard, pywin32 |
| `EZAssistedX2.py` | 主程序集成 |

---

## 9. 修复记录

| 版本 | 日期 | 修复内容 |
|-----|------|---------|
| 1.0 | 2026-04-03 | 初始版本 |
| 2.0 | 2026-04-03 | 添加Ctrl+Shift组合键、设置保存、托盘功能 |
| 3.0 | 2026-04-03 | 修正透明度80%、添加窗口选择器、状态统计、技能名称编辑、ESC取消快捷键捕获 |
| 4.0 | 2026-04-03 | 实施执行：完成所有模块创建和主程序集成 |
| 5.0 | 2026-04-03 | 修复Q键无法触发问题（keyboard库→Win32 API混合方案） |
| 5.1 | 2026-04-03 | 修复跨线程通信问题（QTimer.singleShot→Qt Signal/Slot） |
| 5.2 | 2026-04-03 | 解决CMD窗口显示问题（python→pythonw）、添加SmartLogManager日志管理、添加📝日志开关按钮 |
| **5.3** | **2026-04-03** | **清理与优化**: 删除8个临时/测试文件，修复4处代码问题，更新文档，生成清理报告 |

---

## 10. 执行状态

### 10.1 文件创建状态

| 文件 | 路径 | 状态 | 说明 |
|-----|------|------|------|
| floating_window.py | `D:\EZWowX2\EZAssistedX2.PY\floating_window.py` | ✅ 已创建并优化 | 浮窗主组件（含📝按钮） |
| hotkey_manager.py | `D:\EZWowX2\EZAssistedX2.PY\hotkey_manager.py` | ✅ 已创建并重写 | 混合方案（Hook+轮询） |
| settings_manager.py | `D:\EZWowX2\EZAssistedX2.PY\settings_manager.py` | ✅ 已创建 | 设置管理 |
| skill_name_manager.py | `D:\EZWowX2\EZAssistedX2.PY\skill_name_manager.py` | ✅ 已创建 | 技能名称管理 |
| skill_name_editor.py | `D:\EZWowX2\EZAssistedX2.PY\skill_name_editor.py` | ✅ 已创建 | 技能名称编辑器 |
| window_enumerator.py | `D:\EZWowX2\EZAssistedX2.PY\window_enumerator.py` | ✅ 已创建并增强 | WoW窗口检测与枚举 |
| **smart_logging.py** | **`D:\EZWowX2\EZAssistedX2.PY\smart_logging.py`** | **✅ 新增** | **智能日志管理** |
| EZAssistedX2.py | `D:\EZWowX2\EZAssistedX2.PY\EZAssistedX2.py` | ✅ 已修改并优化 | 主程序集成（Signal/Slot） |
| requirements.txt | `D:\EZWowX2\EZAssistedX2.PY\requirements.txt` | ✅ 已确认 | 依赖完整（已移除keyboard） |
| Start.bat | `D:\EZWowX2\EZAssistedX2.PY\Start.bat` | ✅ 已优化 | 无CMD窗口启动 |

### 10.2 功能实现状态

| 功能 | 状态 | 实现位置 | 备注 |
|-----|------|---------|------|
| 浮窗显示 | ✅ | FloatingWindow类 | 240x160/280, 透明度80% |
| Q键启停 | ✅ | GlobalHotkeyManager (轮询模式) | 30ms间隔, 300ms防抖 |
| Ctrl+Shift+E展开 | ✅ | register_combo (轮询) | 组合键支持 |
| Ctrl+Shift+H隐藏 | ✅ | register_combo (轮询) | 组合键支持 |
| **日志开关(📝)** | **✅** | **SmartLogManager + UI按钮** | **v5.2新增** |
| 窗口选择器 | ✅ | WindowEnumerator + QComboBox | 自动查找WoW窗口 |
| 状态统计 | ✅ | _create_stats_panel | 运行时间/按键/错误计数 |
| 技能名称编辑 | ✅ | SkillNameEditor | 对话框形式 |
| 设置保存加载 | ✅ | SettingsManager | JSON持久化 |
| 托盘功能 | ✅ | QSystemTrayIcon | 显示/退出菜单 |
| 按键日志更新 | ✅ | _on_key_sent | 最近3条记录 |
| 运行时间计时 | ✅ | QTimer | 1秒间隔 |
| **无CMD窗口** | **✅** | **Start.bat (pythonw)** | **v5.2优化** |
| **跨线程安全** | **✅** | **Qt Signal/Slot机制** | **v5.1修复** |

### 10.3 已知问题修复历史

| 问题 | 严重性 | 修复方案 | 状态 |
|-----|--------|---------|------|
| keyboard库Q键不响应 | 🔴 致命 | 改用GetAsyncKeyState轮询 | ✅ 已解决 |
| QTimer.singleShot跨线程失败 | 🔴 致命 | 改用Signal.emit() | ✅ 已解决 |
| CMD窗口始终显示 | 🟡 严重 | 使用pythonw.exe | ✅ 已解决 |
| comtypes DXGI日志刷屏 | 🟡 严重 | SmartLogManager过滤+默认关闭DEBUG | ✅ 已解决 |
| 日志文件过大风险 | 🟡 严重 | 默认OFF模式 (<5MB/4小时 vs 200-400MB) | ✅ 已解决 |
| Win32 Hook安装失败(error 0/126/1429) | 🟠 中等 | 自动降级到轮询模式 | ✅ 已解决 |
| ctypes.DWORD未定义 | 🔴 错误 | 改用wintypes.DWORD | ✅ 已解决 |
| _init_ui方法缺失 | 🔴 错误 | 重新添加方法 | ✅ 已解决 |
| 批处理文件中文乱码 | 🟡 严重 | 纯英文重写Start.bat | ✅ 已解决 |
| Optional类型未导入 | 🟢 警告 | 添加到typing导入 | ✅ 已解决(v7.2) |
| 函数内部重复import | 🟢 警告 | 移至文件顶部 | ✅ 已解决(v7.2) |
| window_enumerator全局basicConfig | 🟢 警告 | 移除全局配置 | ✅ 已解决(v7.2) |

### 10.4 已清理的临时文件 (v7.2)

| 文件 | 原因 | 清理时间 |
|-----|------|---------|
| test_hotkey.py | 诊断工具，已完成调试 | 2026-04-03 |
| test_q_key.py | Q键专项诊断，问题已解决 | 2026-04-03 |
| test_comprehensive.py | 综合测试脚本，不再需要 | 2026-04-03 |
| verify_fix.py | 快速验证脚本，已验证通过 | 2026-04-03 |
| view_logs.py | 日志查看器，已被📝按钮替代 | 2026-04-03 |
| hotkey_diagnostic.log | 旧诊断日志，无保留价值 | 2026-04-03 |
| Q_KEY_FIX_GUIDE.md | 临时修复指南，问题已归档 | 2026-04-03 |
| 启动EZAssistedX2_调试.bat | 调试批处理，已被Start.bat替代 | 2026-04-03 |
| __pycache__\\*.pyc | 编译缓存，可重新生成 | 2026-04-03 |

---

**文档版本**: 5.3
**最后更新**: 2026-04-03 (清理与优化完成)
