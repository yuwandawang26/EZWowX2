from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox
from PySide6.QtCore import Qt, QPoint, QTimer
from PySide6.QtGui import QPainter, QColor, QBrush, QKeyEvent
import logging

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
        self._is_running = False
        self._is_paused = False
        self._is_dragging = False
        self._drag_position = QPoint()
        self._current_hotkey = 'q'
        self._is_capturing_hotkey = False
        self._hotkey_callback = None
        self._edit_skill_callback = None

        self._runtime_seconds = 0
        self._key_count = 0
        self._error_count = 0
        self._runtime_timer = QTimer()
        self._runtime_timer.timeout.connect(self._update_runtime)

        self._init_window()
        self._init_ui()
        self._set_stopped_state()

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

        self.log_button = QLabel("📝")
        self.log_button.setFixedSize(24, 24)
        self.log_button.setToolTip("Toggle Debug Logging (OFF)")
        self.log_button.setStyleSheet("""
            background-color: rgb(60, 40, 40);
            border-radius: 4px;
            color: rgb(180, 180, 180);
            font-size: 12pt;
        """)
        self.log_button._log_enabled = False
        self.log_button.mousePressEvent = lambda e: self._on_log_toggle_click()
        status_layout.addWidget(self.log_button)

        self.skill_edit_button = QLabel("✎")
        self.skill_edit_button.setFixedSize(24, 24)
        self.skill_edit_button.setStyleSheet("""
            background-color: rgb(50, 50, 60);
            border-radius: 4px;
            color: rgb(210, 210, 220);
            font-size: 12pt;
        """)
        self.skill_edit_button.mousePressEvent = lambda e: self._on_edit_skills_click()
        status_layout.addWidget(self.skill_edit_button)

        self.close_button = QLabel("×")
        self.close_button.setFixedSize(24, 24)
        self.close_button.setStyleSheet("""
            background-color: rgb(50, 50, 60);
            border-radius: 4px;
            color: rgb(210, 210, 220);
            font-size: 14pt;
        """)
        self._exit_callback = None
        self.close_button.mousePressEvent = lambda e: self._on_close_click()
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
        logger = logging.getLogger(__name__)
        logger.debug(f"FloatingWindow._on_pause_click: _is_running={self._is_running}, _is_paused={self._is_paused}")
        
        if not self._is_running:
            self._is_running = True
            self._is_paused = False
            self.status_indicator.setStyleSheet("color: rgb(80, 220, 120); font-size: 14pt;")
            self.status_label.setText("运行中")
            self.pause_button.setText("⏸")
            self._runtime_timer.start(1000)
        elif self._is_paused:
            self._is_paused = False
            self.status_indicator.setStyleSheet("color: rgb(80, 220, 120); font-size: 14pt;")
            self.status_label.setText("运行中")
            self.pause_button.setText("⏸")
            self._runtime_timer.start(1000)
        else:
            self._is_paused = True
            self.status_indicator.setStyleSheet("color: rgb(255, 200, 50); font-size: 14pt;")
            self.status_label.setText("已暂停")
            self.pause_button.setText("▶")
            self._runtime_timer.stop()

    def set_running_state(self, is_running: bool, is_paused: bool = False):
        logger = logging.getLogger(__name__)
        logger.debug(f"set_running_state: is_running={is_running}, is_paused={is_paused}")
        
        self._is_running = is_running
        self._is_paused = is_paused
        
        if not is_running:
            self.status_indicator.setStyleSheet("color: rgb(150, 150, 150); font-size: 14pt;")
            self.status_label.setText("未运行")
            self.pause_button.setText("▶")
            self._runtime_timer.stop()
        elif is_paused:
            self.status_indicator.setStyleSheet("color: rgb(255, 200, 50); font-size: 14pt;")
            self.status_label.setText("已暂停")
            self.pause_button.setText("▶")
            self._runtime_timer.stop()
        else:
            self.status_indicator.setStyleSheet("color: rgb(80, 220, 120); font-size: 14pt;")
            self.status_label.setText("运行中")
            self.pause_button.setText("⏸")
            self._runtime_timer.start(1000)

    def _set_stopped_state(self):
        self.set_running_state(False, False)
        self._runtime_seconds = 0
        self._key_count = 0
        self._error_count = 0
        self._update_runtime()

    def _on_hotkey_edit_click(self):
        self.start_hotkey_capture(self._on_hotkey_changed)

    def _on_hotkey_changed(self, new_hotkey: str):
        pass

    def _on_edit_skills_click(self):
        if self._edit_skill_callback:
            self._edit_skill_callback()

    def _on_close_click(self):
        if self._exit_callback:
            self._exit_callback()
        else:
            self.hide()

    def _on_log_toggle_click(self):
        """切换DEBUG日志模式"""
        from smart_logging import log_manager
        
        # 切换日志模式
        is_enabled = log_manager.toggle_debug()
        
        # 更新按钮外观
        self.log_button._log_enabled = is_enabled
        
        if is_enabled:
            self.log_button.setStyleSheet("""
                background-color: rgb(40, 80, 40);
                border-radius: 4px;
                color: rgb(100, 255, 100);
                font-size: 12pt;
            """)
            self.log_button.setToolTip("Toggle Debug Logging (ON)")
        else:
            self.log_button.setStyleSheet("""
                background-color: rgb(60, 40, 40);
                border-radius: 4px;
                color: rgb(180, 180, 180);
                font-size: 12pt;
            """)
            self.log_button.setToolTip("Toggle Debug Logging (OFF)")

    def set_exit_callback(self, callback):
        self._exit_callback = callback

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