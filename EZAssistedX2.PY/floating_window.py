from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
                                QSizeGrip)
from PySide6.QtCore import Qt, QPoint, QTimer, QRect
from PySide6.QtGui import QPainter, QColor, QBrush, QKeyEvent, QIcon, QCursor
import logging
import os


class FloatingWindow(QWidget):
    """游戏外浮窗主窗口 - 支持拖拽移动和边缘调整大小"""

    COMPACT_WIDTH = 240
    COMPACT_HEIGHT = 160
    EXPANDED_WIDTH = 240
    EXPANDED_HEIGHT = 280
    MINIMAL_HEIGHT = 36
    MINIMAL_WIDTH = 180
    WINDOW_OPACITY = 0.80
    RESIZE_MARGIN = 6
    MIN_WIDTH = 140
    MIN_HEIGHT = 28

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
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_expanded = False
        self._is_running = False
        self._is_paused = False
        self._is_minimal_mode = False
        self._is_dragging = False
        self._is_resizing = False
        self._drag_position = QPoint()
        self._resize_edge = None
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

        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'EZAssistedX2.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    def _enable_resize(self):
        self.setMinimumSize(self.MIN_WIDTH, self.MIN_HEIGHT)
        self.setMaximumSize(16777215, 16777215)

    def _disable_resize(self):
        current_size = self.size()
        self.setFixedSize(current_size.width(), current_size.height())

    def _init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(8, 8, 8, 8)
        self.main_layout.setSpacing(4)

        self._create_normal_container()
        self._create_minimal_container()

        self._size_grip = QSizeGrip(self)
        self._size_grip.setFixedSize(14, 14)
        self._size_grip.setStyleSheet("background: transparent;")
        self.main_layout.setAlignment(self._size_grip, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(self.COLORS['background']))
        painter.setPen(self.COLORS['border'])
        painter.drawRoundedRect(self.rect(), 8, 8)

    def _get_resize_edge(self, pos):
        x, y = pos.x(), pos.y()
        w, h = self.width(), self.height()
        edge = None
        if x >= w - self.RESIZE_MARGIN:
            edge = Qt.CursorShape.SizeHorCursor if y < self.RESIZE_MARGIN or y > h - self.RESIZE_MARGIN else Qt.CursorShape.SizeFDiagCursor
        elif y >= h - self.RESIZE_MARGIN:
            edge = Qt.CursorShape.SizeVerCursor if x < self.RESIZE_MARGIN or x > w - self.RESIZE_MARGIN else Qt.CursorShape.SizeBDiagCursor
        return edge

    def _update_cursor(self, pos):
        edge = self._get_resize_edge(pos)
        if edge:
            self.setCursor(edge)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def mouseMoveEvent(self, event):
        if self._is_resizing and not self._is_minimal_mode:
            global_pos = event.globalPosition().toPoint()
            delta = global_pos - self._drag_position
            new_w = max(self.MIN_WIDTH, self._original_geometry.width() + delta.x())
            new_h = max(self.MIN_HEIGHT, self._original_geometry.height() + delta.y())
            self.resize(new_w, new_h)
            event.accept()
            return

        if self._is_dragging:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()
            return

        if not self._is_minimal_mode:
            self._update_cursor(event.position().toPoint())

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            edge = self._get_resize_edge(event.position().toPoint())
            if edge and not self._is_minimal_mode:
                self._is_resizing = True
                self._drag_position = event.globalPosition().toPoint()
                self._original_geometry = self.geometry()
                event.accept()
                return

            self._is_dragging = True
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseReleaseEvent(self, event):
        self._is_dragging = False
        self._is_resizing = False
        self._update_cursor(event.position().toPoint())
        event.accept()

    def mouseDoubleClickEvent(self, event):
        if self._is_minimal_mode and event.button() == Qt.MouseButton.LeftButton:
            self._switch_to_normal_mode()
            event.accept()

    def leaveEvent(self, event):
        if not self._is_dragging and not self._is_resizing:
            self.setCursor(Qt.CursorShape.ArrowCursor)

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
                if hasattr(self, 'hotkey_display'):
                    self.hotkey_display.setText("[无效]")
                QTimer.singleShot(500, lambda: self.set_hotkey(self._current_hotkey))
        else:
            super().keyPressEvent(event)

    def toggle_expand(self):
        if self._is_minimal_mode:
            return
        self._is_expanded = not self._is_expanded
        if self._is_expanded:
            self.resize(self.EXPANDED_WIDTH, self.EXPANDED_HEIGHT)
            self.settings_button.setText("▼")
        else:
            self.resize(self.COMPACT_WIDTH, self.COMPACT_HEIGHT)
            self.settings_button.setText("⚙")

    def _create_normal_container(self):
        self.normal_widget = QWidget()
        normal_layout = QVBoxLayout(self.normal_widget)
        normal_layout.setContentsMargins(0, 0, 0, 0)
        normal_layout.setSpacing(0)

        self._create_status_bar()
        self._create_key_log_area()
        self._create_hotkey_display()
        self._create_expanded_panel()

        self.main_layout.addWidget(self.normal_widget)

    def _create_minimal_container(self):
        self.minimal_widget = QWidget()
        minimal_layout = QHBoxLayout(self.minimal_widget)
        minimal_layout.setContentsMargins(10, 5, 10, 5)
        minimal_layout.setSpacing(8)

        self.minimal_indicator = QLabel("●")
        self.minimal_indicator.setStyleSheet("color: rgb(80, 220, 120); font-size: 13pt; font-family: 'Microsoft YaHei', 'SimHei', sans-serif;")
        minimal_layout.addWidget(self.minimal_indicator)

        self.minimal_label = QLabel("运行中")
        self.minimal_label.setStyleSheet("color: rgb(80, 220, 120); font-size: 12pt; font-weight: bold; font-family: 'Microsoft YaHei', 'SimHei', sans-serif;")
        minimal_layout.addWidget(self.minimal_label)

        minimal_layout.addStretch()

        self.minimal_pause_btn = QLabel("⏸")
        self.minimal_pause_btn.setFixedSize(26, 24)
        self.minimal_pause_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.minimal_pause_btn.setStyleSheet("""
            background-color: rgba(50, 50, 60, 200);
            border-radius: 4px;
            color: rgb(210, 210, 220);
            font-size: 12pt;
            padding: 0px 3px;
        """)
        self.minimal_pause_btn.mousePressEvent = lambda e: self._on_pause_click()
        minimal_layout.addWidget(self.minimal_pause_btn)

        self.minimal_close_btn = QLabel("×")
        self.minimal_close_btn.setFixedSize(26, 24)
        self.minimal_close_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.minimal_close_btn.setStyleSheet("""
            background-color: rgba(200, 50, 50, 200);
            border-radius: 4px;
            color: rgb(255, 255, 255);
            font-size: 13pt;
            padding: 0px 3px;
        """)
        self.minimal_close_btn.mousePressEvent = lambda e: self._on_close_click()
        minimal_layout.addWidget(self.minimal_close_btn)

        self.minimal_widget.setVisible(False)
        self.main_layout.addWidget(self.minimal_widget)

    def _switch_to_minimal_mode(self):
        if self._is_minimal_mode:
            return
        self._is_minimal_mode = True
        self._disable_resize()
        self.normal_widget.setVisible(False)
        self.minimal_widget.setVisible(True)
        self.resize(max(self.MINIMAL_WIDTH, self.width()), self.MINIMAL_HEIGHT)
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def _switch_to_normal_mode(self):
        if not self._is_minimal_mode:
            return
        self._is_minimal_mode = False
        self.minimal_widget.setVisible(False)
        self.normal_widget.setVisible(True)
        target_w = self.EXPANDED_WIDTH if self._is_expanded else self.COMPACT_WIDTH
        target_h = self.EXPANDED_HEIGHT if self._is_expanded else self.COMPACT_HEIGHT
        self.resize(target_w, target_h)
        self._enable_resize()

    def _create_status_bar(self):
        status_layout = QHBoxLayout()
        status_layout.setSpacing(4)

        self.status_indicator = QLabel("●")
        self.status_indicator.setStyleSheet("color: rgb(150, 150, 150); font-size: 13pt;")
        status_layout.addWidget(self.status_indicator)

        self.status_label = QLabel("未运行")
        self.status_label.setStyleSheet("color: rgb(150, 150, 150); font-size: 10pt; font-weight: bold; font-family: 'Microsoft YaHei', 'SimHei', sans-serif;")
        status_layout.addWidget(self.status_label)

        status_layout.addStretch()

        self.pause_button = QLabel("▶")
        self.pause_button.setFixedSize(22, 22)
        self.pause_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.pause_button.setStyleSheet("""
            background-color: rgb(50, 50, 60);
            border-radius: 4px;
            color: rgb(210, 210, 220);
            font-size: 11pt;
        """)
        self.pause_button.mousePressEvent = lambda e: self._on_pause_click()
        status_layout.addWidget(self.pause_button)

        self.settings_button = QLabel("⚙")
        self.settings_button.setFixedSize(22, 22)
        self.settings_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.settings_button.setStyleSheet("""
            background-color: rgb(50, 50, 60);
            border-radius: 4px;
            color: rgb(210, 210, 220);
            font-size: 11pt;
        """)
        self.settings_button.mousePressEvent = lambda e: self.toggle_expand()
        status_layout.addWidget(self.settings_button)

        self.log_button = QLabel("📝")
        self.log_button.setFixedSize(22, 22)
        self.log_button.setToolTip("Toggle Debug Logging (OFF)")
        self.log_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.log_button.setStyleSheet("""
            background-color: rgb(60, 40, 40);
            border-radius: 4px;
            color: rgb(180, 180, 180);
            font-size: 11pt;
        """)
        self.log_button._log_enabled = False
        self.log_button.mousePressEvent = lambda e: self._on_log_toggle_click()
        status_layout.addWidget(self.log_button)

        self.close_button = QLabel("×")
        self.close_button.setFixedSize(22, 22)
        self.close_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.close_button.setStyleSheet("""
            background-color: rgb(50, 50, 60);
            border-radius: 4px;
            color: rgb(210, 210, 220);
            font-size: 13pt;
        """)
        self.close_button.mousePressEvent = lambda e: self._on_close_click()
        status_layout.addWidget(self.close_button)

        self.normal_widget.layout().addLayout(status_layout)

    def _create_key_log_area(self):
        log_label = QLabel("最近按键:")
        log_label.setStyleSheet("color: rgb(180, 180, 180); font-size: 9pt;")
        self.normal_widget.layout().addWidget(log_label)

        self.key_log_widget = QWidget()
        self.key_log_layout = QVBoxLayout(self.key_log_widget)
        self.key_log_layout.setContentsMargins(4, 2, 4, 2)
        self.key_log_layout.setSpacing(1)

        self.key_log_items = []
        for i in range(3):
            log_item = QLabel(f"▶ --")
            log_item.setStyleSheet("color: rgb(150, 150, 150); font-family: Consolas; font-size: 9pt;")
            self.key_log_layout.addWidget(log_item)
            self.key_log_items.append(log_item)

        self.normal_widget.layout().addWidget(self.key_log_widget)

    def _create_hotkey_display(self):
        hotkey_layout = QHBoxLayout()

        hotkey_label = QLabel("启停快捷键:")
        hotkey_label.setStyleSheet("color: rgb(180, 180, 180); font-size: 9pt;")
        hotkey_layout.addWidget(hotkey_label)

        hotkey_layout.addStretch()

        self.hotkey_display = QLabel("[Q]")
        self.hotkey_display.setFixedSize(36, 22)
        self.hotkey_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hotkey_display.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.hotkey_display.setStyleSheet("""
            background-color: rgb(50, 50, 60);
            border-radius: 4px;
            color: rgb(100, 180, 255);
            font-family: Consolas;
            font-size: 10pt;
            font-weight: bold;
            padding: 1px 6px;
        """)
        self.hotkey_display.mousePressEvent = lambda e: self._on_hotkey_edit_click()
        hotkey_layout.addWidget(self.hotkey_display)

        self.hotkey_edit_button = QLabel("✎")
        self.hotkey_edit_button.setFixedSize(18, 22)
        self.hotkey_edit_button.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hotkey_edit_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.hotkey_edit_button.setStyleSheet("""
            background-color: rgb(50, 50, 60);
            border-radius: 4px;
            color: rgb(180, 180, 180);
            font-size: 10pt;
        """)
        self.hotkey_edit_button.mousePressEvent = lambda e: self._on_hotkey_edit_click()
        hotkey_layout.addWidget(self.hotkey_edit_button)

        self.normal_widget.layout().addLayout(hotkey_layout)

    def _create_expanded_panel(self):
        self.expanded_widget = QWidget()
        self.expanded_layout = QVBoxLayout(self.expanded_widget)
        self.expanded_layout.setContentsMargins(0, 6, 0, 0)
        self.expanded_layout.setSpacing(3)
        self.expanded_widget.setVisible(False)

        self._create_window_selector()
        self._create_stats_panel()

        self.normal_widget.layout().addWidget(self.expanded_widget)

    def _create_window_selector(self):
        selector_layout = QHBoxLayout()

        label = QLabel("目标窗口:")
        label.setStyleSheet("color: rgb(180, 180, 180); font-size: 9pt;")
        selector_layout.addWidget(label)

        self.window_combo = QComboBox()
        self.window_combo.setFixedHeight(20)
        self.window_combo.setStyleSheet("""
            background-color: rgb(50, 50, 60);
            color: rgb(210, 210, 220);
            border: 1px solid rgb(60, 60, 70);
            border-radius: 4px;
            padding: 1px 4px;
        """)
        selector_layout.addWidget(self.window_combo)

        self.expanded_layout.addLayout(selector_layout)

    def _create_stats_panel(self):
        stats_label = QLabel("状态统计:")
        stats_label.setStyleSheet("color: rgb(180, 180, 180); font-size: 9pt;")
        self.expanded_layout.addWidget(stats_label)

        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("color: rgb(150, 150, 150); font-family: Consolas; font-size: 9pt;")
        self.stats_label.setText(
            "├─ 运行时间: 00:00:00\n"
            "├─ 已发送按键: 0\n"
            "└─ 错误计数: 0"
        )
        self.expanded_layout.addWidget(self.stats_label)

    def _on_pause_click(self):
        logger = logging.getLogger(__name__)
        logger.debug(f"FloatingWindow._on_pause_click: _is_running={self._is_running}, _is_paused={self._is_paused}")

        if not self._is_running:
            self._is_running = True
            self._is_paused = False
            self._apply_running_visuals()
            self._switch_to_minimal_mode()
            self._runtime_timer.start(1000)
        elif self._is_paused:
            self._is_paused = False
            self._apply_running_visuals()
            self._switch_to_minimal_mode()
            self._runtime_timer.start(1000)
        else:
            self._is_paused = True
            self._apply_paused_visuals()
            self._switch_to_normal_mode()
            self._runtime_timer.stop()

    def set_running_state(self, is_running: bool, is_paused: bool = False):
        logger = logging.getLogger(__name__)
        logger.debug(f"set_running_state: is_running={is_running}, is_paused={is_paused}")

        self._is_running = is_running
        self._is_paused = is_paused

        if not is_running:
            self._apply_stopped_visuals()
            self._switch_to_normal_mode()
            self._runtime_timer.stop()
        elif is_paused:
            self._apply_paused_visuals()
            self._switch_to_normal_mode()
            self._runtime_timer.stop()
        else:
            self._apply_running_visuals()
            self._switch_to_minimal_mode()
            self._runtime_timer.start(1000)

    def _apply_running_visuals(self):
        color = f"rgb({self.COLORS['status_running'].red()}, {self.COLORS['status_running'].green()}, {self.COLORS['status_running'].blue()})"
        ff = "'Microsoft YaHei', 'SimHei', sans-serif"
        self.status_indicator.setStyleSheet(f"color: {color}; font-size: 13pt;")
        self.status_label.setText("运行中")
        self.status_label.setStyleSheet(f"color: {color}; font-size: 10pt; font-weight: bold; font-family: {ff};")
        self.pause_button.setText("⏸")

        self.minimal_indicator.setStyleSheet(f"color: {color}; font-size: 13pt; font-family: {ff};")
        self.minimal_label.setText("运行中")
        self.minimal_label.setStyleSheet(f"color: {color}; font-size: 12pt; font-weight: bold; font-family: {ff};")
        self.minimal_pause_btn.setText("⏸")

    def _apply_paused_visuals(self):
        color = f"rgb({self.COLORS['status_paused'].red()}, {self.COLORS['status_paused'].green()}, {self.COLORS['status_paused'].blue()})"
        ff = "'Microsoft YaHei', 'SimHei', sans-serif"
        self.status_indicator.setStyleSheet(f"color: {color}; font-size: 13pt;")
        self.status_label.setText("已暂停")
        self.status_label.setStyleSheet(f"color: {color}; font-size: 10pt; font-weight: bold; font-family: {ff};")
        self.pause_button.setText("▶")

        self.minimal_indicator.setStyleSheet(f"color: {color}; font-size: 13pt; font-family: {ff};")
        self.minimal_label.setText("已暂停")
        self.minimal_label.setStyleSheet(f"color: {color}; font-size: 12pt; font-weight: bold; font-family: {ff};")
        self.minimal_pause_btn.setText("▶")

    def _apply_stopped_visuals(self):
        gray = "rgb(150, 150, 150)"
        ff = "'Microsoft YaHei', 'SimHei', sans-serif"
        self.status_indicator.setStyleSheet(f"color: {gray}; font-size: 13pt;")
        self.status_label.setText("未运行")
        self.status_label.setStyleSheet(f"color: {gray}; font-size: 10pt; font-weight: bold; font-family: {ff};")
        self.pause_button.setText("▶")

        self.minimal_indicator.setStyleSheet(f"color: {gray}; font-size: 13pt; font-family: {ff};")
        self.minimal_label.setText("未运行")
        self.minimal_label.setStyleSheet(f"color: {gray}; font-size: 12pt; font-weight: bold; font-family: {ff};")
        self.minimal_pause_btn.setText("▶")

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

    def _on_close_click(self):
        if self._exit_callback:
            self._exit_callback()
        else:
            self.hide()

    def _on_log_toggle_click(self):
        from smart_logging import log_manager

        is_enabled = log_manager.toggle_debug()

        self.log_button._log_enabled = is_enabled

        if is_enabled:
            self.log_button.setStyleSheet("""
                background-color: rgb(40, 80, 40);
                border-radius: 4px;
                color: rgb(100, 255, 100);
                font-size: 11pt;
            """)
            self.log_button.setToolTip("Toggle Debug Logging (ON)")
        else:
            self.log_button.setStyleSheet("""
                background-color: rgb(60, 40, 40);
                border-radius: 4px;
                color: rgb(180, 180, 180);
                font-size: 11pt;
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
            font-size: 10pt;
            font-weight: bold;
            padding: 1px 6px;
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
            font-size: 10pt;
            font-weight: bold;
            padding: 1px 6px;
        """)

    def get_current_hotkey(self) -> str:
        return self._current_hotkey

    def update_skill_name(self, color_key: str, skill_name: str):
        pass

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
        except Exception:
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
