"""GUI widgets and main window."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QEvent, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QCursor, QPalette
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QSlider,
    QStyleFactory,
    QToolTip,
    QVBoxLayout,
    QWidget,
)

from ..config.items import ComboConfig, SliderConfig
from ..config.registry import ConfigRegistry
from ..engine.loop import RotationLoopEngine
from ..input.win32_sender import Win32Sender


class SliderWidget(QWidget):
    """Slider config widget."""

    value_changed = Signal(str, float)

    def __init__(self, config: SliderConfig, parent: QWidget | None = None):
        super().__init__(parent)
        self.config = config
        self._scale = 1.0 / config.step if config.step > 0 else 1.0
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(int(round((config.max_value - config.min_value) * self._scale)))
        self.slider.setSingleStep(1)
        self.slider.setValue(int(round((float(config.get_value()) - config.min_value) * self._scale)))
        self.slider.valueChanged.connect(self._on_changed)

        self._decimals = max(0, len(f"{config.step}".split(".")[1]) if "." in f"{config.step}" else 0)
        self.value_label = QLabel(f"{float(config.get_value()):.{self._decimals}f}")

        layout.addWidget(self.slider)
        layout.addWidget(self.value_label)

    def _on_changed(self, value: int) -> None:
        real_value = self.config.min_value + (value / self._scale)
        self.value_label.setText(f"{real_value:.{self._decimals}f}")
        self.config.set_value_from_gui(real_value)
        self.value_changed.emit(self.config.key, float(self.config.get_value()))


class ComboWidget(QWidget):
    """Combo config widget."""

    value_changed = Signal(str, object)

    def __init__(self, config: ComboConfig, parent: QWidget | None = None):
        super().__init__(parent)
        self.config = config
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.combo = QComboBox()
        self.combo.addItems(config.options)
        self.combo.setCurrentIndex(config.get_index())
        self.combo.currentIndexChanged.connect(self._on_changed)

        layout.addWidget(self.combo)

    def _on_changed(self, index: int) -> None:
        self.config.set_index_from_gui(index)
        self.value_changed.emit(self.config.key, self.config.get_value())


class CollapsibleBox(QWidget):
    """Collapsible container."""

    toggled = Signal(bool)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._collapsed = False
        self._content_height = 0

        self._setup_ui()

    def _setup_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.content_area = QFrame()
        self.content_area.setStyleSheet(
            """
            QFrame {
                border: none;
            }
            """
        )
        self._content_layout = QVBoxLayout(self.content_area)
        self._content_layout.setContentsMargins(5, 5, 5, 5)

        main_layout.addWidget(self.content_area)

    def set_content(self, widget: QWidget) -> None:
        while self._content_layout.count():
            item = self._content_layout.takeAt(0)
            if item is not None:
                item_widget = item.widget()
                if item_widget:
                    item_widget.setParent(None)

        self._content_layout.addWidget(widget)
        self.content_area.adjustSize()
        self._content_height = self.content_area.sizeHint().height()

    def toggle(self) -> None:
        self.set_collapsed(not self._collapsed)

    def is_collapsed(self) -> bool:
        return self._collapsed

    def set_collapsed(self, collapsed: bool) -> None:
        if self._collapsed == collapsed:
            return
        self._collapsed = collapsed

        if collapsed:
            self.content_area.hide()
        else:
            self.content_area.show()

        self.toggled.emit(collapsed)


class MainWindow(QWidget):
    """Driver main window."""

    log_signal = Signal(str)

    def __init__(
        self,
        engine: RotationLoopEngine,
        config: ConfigRegistry,
        window_sender: Win32Sender,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.engine = engine
        self.config = config
        self._window_sender = window_sender
        self._window_list: list[tuple[int, str]] = []
        self._fast_tooltip_widgets: set[QWidget] = set()
        self._dragging = False
        self._drag_pos: Any = None

        self.setWindowTitle(f"{engine.profile.__class__.__name__}")
        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.CustomizeWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.FramelessWindowHint
        )
        self.setWindowFlag(Qt.WindowType.MSWindowsFixedSizeDialogHint, True)
        self.setFixedWidth(315)
        self.setObjectName("mainWindow")

        app = QApplication.instance()
        if isinstance(app, QApplication):
            app.setStyle(QStyleFactory.create("Fusion"))
            palette = QPalette()
            role = QPalette.ColorRole
            palette.setColor(role.Window, QColor(240, 240, 240))
            palette.setColor(role.WindowText, QColor(0, 0, 0))
            palette.setColor(role.Base, QColor(255, 255, 255))
            palette.setColor(role.AlternateBase, QColor(245, 245, 245))
            palette.setColor(role.Text, QColor(0, 0, 0))
            palette.setColor(role.Button, QColor(240, 240, 240))
            palette.setColor(role.ButtonText, QColor(0, 0, 0))
            palette.setColor(role.Highlight, QColor(0, 120, 215))
            palette.setColor(role.HighlightedText, QColor(255, 255, 255))
            app.setPalette(palette)
            app.setStyleSheet(
                """
                QComboBox {
                    background: #ffffff;
                    color: #111111;
                    border: 1px solid #c8c8c8;
                    padding: 2px 6px;
                }
                QComboBox::drop-down {
                    border-left: 1px solid #c8c8c8;
                }
                QComboBox QAbstractItemView {
                    background: #ffffff;
                    color: #111111;
                    selection-background-color: #e6e6e6;
                    selection-color: #000000;
                }
                QToolTip {
                    background-color: #ffffff;
                    color: #111111;
                    border: 1px solid #c8c8c8;
                }
                """
            )

        self.init_ui()

        self.log_signal.connect(self._append_log)
        self.engine.set_log_callback(self.log_signal.emit)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_status)
        self.timer.start(500)

    def init_ui(self) -> None:
        main_layout = QVBoxLayout()
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(5, 5, 5, 5)

        control_container = QWidget()
        control_container.setAutoFillBackground(False)
        control_layout = QHBoxLayout(control_container)
        control_layout.setContentsMargins(0, 0, 0, 0)

        self.start_btn = QPushButton("▶️ 启动")
        self.start_btn.clicked.connect(self._start_engine)

        self.status_label = QLabel("🔴 已停止")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #888; background: transparent;")

        self.stop_btn = QPushButton("🟥 停止")
        self.stop_btn.clicked.connect(self._stop_engine)

        self.toggle_btn = QPushButton("🔒 折叠")
        self.toggle_btn.setToolTip("折叠/展开配置")

        control_layout.addWidget(self.start_btn, 3)
        control_layout.addWidget(self.status_label, 5)
        control_layout.addWidget(self.stop_btn, 3)
        control_layout.addWidget(self.toggle_btn, 3)
        main_layout.addWidget(control_container)

        self.window_combo = QComboBox()
        self.window_combo.currentIndexChanged.connect(self._on_window_changed)
        self.refresh_btn = QPushButton("刷新窗体")
        self.refresh_btn.clicked.connect(self._refresh_windows)
        self.close_btn = QPushButton("关闭 ❌")
        self.close_btn.clicked.connect(self.close)

        row_height = self.refresh_btn.sizeHint().height()
        self.start_btn.setFixedHeight(row_height)
        self.status_label.setFixedHeight(row_height)
        self.stop_btn.setFixedHeight(row_height)
        self.toggle_btn.setFixedHeight(row_height)
        self.window_combo.setFixedHeight(row_height)
        base_btn_width = self.start_btn.sizeHint().width()
        self.refresh_btn.setFixedWidth(int(base_btn_width * 0.8))
        self.close_btn.setFixedHeight(row_height)

        self.log_view = QLineEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setFixedHeight(row_height)
        self.log_view.setStyleSheet(
            """
            QLineEdit {
                background: #ffffff;
                border: 1px solid #c8c8c8;
                color: #111111;
            }
            """
        )
        self.log_view.installEventFilter(self)
        main_layout.addWidget(self.log_view)

        self.config_box = CollapsibleBox()
        config_content = QWidget()
        config_layout = QFormLayout(config_content)
        config_layout.setContentsMargins(0, 0, 0, 0)

        window_row = QWidget()
        window_layout = QHBoxLayout(window_row)
        window_layout.setContentsMargins(0, 0, 0, 0)
        window_label = QLabel("游戏窗体")
        window_label.setFixedHeight(row_height)
        window_layout.addWidget(window_label)
        window_layout.addWidget(self.window_combo, 1)
        window_layout.addWidget(self.refresh_btn)
        config_layout.addRow(window_row)

        for key, item in self.config.all_items().items():
            del key
            if isinstance(item, SliderConfig):
                widget = SliderWidget(item)
                widget.value_changed.connect(self._ignore_change)
                config_layout.addRow(item.label, widget)
                if item.description:
                    label = config_layout.labelForField(widget)
                    self._register_fast_tooltip(label, item.description)
                    self._register_fast_tooltip(widget, item.description)
            elif isinstance(item, ComboConfig):
                widget = ComboWidget(item)
                widget.value_changed.connect(self._ignore_change)
                config_layout.addRow(item.label, widget)
                if item.description:
                    label = config_layout.labelForField(widget)
                    self._register_fast_tooltip(label, item.description)
                    self._register_fast_tooltip(widget, item.description)

        close_row = QWidget()
        close_layout = QHBoxLayout(close_row)
        close_layout.setContentsMargins(0, 0, 0, 0)
        close_layout.addWidget(self.close_btn)
        config_layout.addRow(close_row)

        self.config_box.set_content(config_content)
        self.toggle_btn.clicked.connect(self.config_box.toggle)
        self.config_box.toggled.connect(self._on_config_toggled)

        main_layout.addWidget(self.config_box)

        self.setLayout(main_layout)
        self._refresh_windows()
        self._update_start_enabled()

    def _on_config_toggled(self, collapsed: bool) -> None:
        self.toggle_btn.setText("🛠️ 展开" if collapsed else "🔒 折叠")
        self.config_box.adjustSize()
        self.adjustSize()
        size_hint = self.sizeHint()
        self.setFixedHeight(size_hint.height())

    def _ignore_change(self, key: str, value: object) -> None:
        del key
        del value

    def _start_engine(self) -> None:
        self.engine.start()
        self.config_box.set_collapsed(True)

    def _stop_engine(self) -> None:
        self.engine.stop()

    def _update_status(self) -> None:
        running = self.engine.is_running()
        if running:
            self.status_label.setText("🟢 运行中")
            self.status_label.setStyleSheet("color: #28a745; font-weight: bold;")
        else:
            self.status_label.setText("🔴 已停止")
            self.status_label.setStyleSheet("color: #888;")
        self.start_btn.setEnabled(not running)
        self.stop_btn.setEnabled(running)
        self.window_combo.setEnabled(not running)
        self.refresh_btn.setEnabled(not running)
        self.close_btn.setEnabled(not running)
        if not running:
            self._update_start_enabled()
        self._update_button_styles(running=running)

    def closeEvent(self, event: Any) -> None:  # noqa: N802
        dialog = QInputDialog(self)
        dialog.setWindowTitle("确认关闭")
        dialog.setLabelText("请输入 exit 以关闭：")
        dialog.setTextEchoMode(QLineEdit.EchoMode.Normal)
        dialog.setOkButtonText("关闭")
        dialog.setCancelButtonText("取消")
        dialog.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.CustomizeWindowHint
            | Qt.WindowType.WindowTitleHint
        )
        dialog.setWindowFlag(Qt.WindowType.WindowMinimizeButtonHint, False)
        dialog.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint, False)
        dialog.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)
        dialog.setWindowFlag(Qt.WindowType.MSWindowsFixedSizeDialogHint, True)
        ok = dialog.exec()
        text = dialog.textValue()
        if ok and text.strip().lower() == "exit":
            self.engine.stop()
            event.accept()
        else:
            event.ignore()

    def mousePressEvent(self, event: Any) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: Any) -> None:  # noqa: N802
        if self._dragging and self._drag_pos is not None:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: Any) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            self._drag_pos = None
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event: Any) -> None:  # noqa: N802
        if event.key() == Qt.Key.Key_F4 and event.modifiers() & Qt.KeyboardModifier.AltModifier:
            event.ignore()
            return
        super().keyPressEvent(event)

    def eventFilter(self, obj: Any, event: Any) -> bool:
        if obj is self.log_view:
            if event.type() == event.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:  # type: ignore[attr-defined]
                self._dragging = True
                self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()  # type: ignore[attr-defined]
                event.accept()  # type: ignore[attr-defined]
                return True
            if event.type() == event.Type.MouseMove and self._dragging and self._drag_pos is not None:
                self.move(event.globalPosition().toPoint() - self._drag_pos)  # type: ignore[attr-defined]
                event.accept()  # type: ignore[attr-defined]
                return True
            if event.type() == event.Type.MouseButtonRelease and event.button() == Qt.MouseButton.LeftButton:  # type: ignore[attr-defined]
                self._dragging = False
                self._drag_pos = None
                event.accept()  # type: ignore[attr-defined]
                return True
        if obj in self._fast_tooltip_widgets:
            if event.type() == QEvent.Type.Enter:
                QToolTip.showText(QCursor.pos(), obj.toolTip(), obj)  # type: ignore[attr-defined]
            elif event.type() == QEvent.Type.Leave:
                QToolTip.hideText()
        return super().eventFilter(obj, event)

    def _register_fast_tooltip(self, widget: QWidget, text: str) -> None:
        widget.setToolTip(text)
        widget.installEventFilter(self)
        self._fast_tooltip_widgets.add(widget)

    def _append_log(self, message: str) -> None:
        self.log_view.setText(message)

    def _refresh_windows(self) -> None:
        all_windows = self._window_sender.list_windows()
        self._window_list = [(hwnd, title) for hwnd, title in all_windows if "魔兽世界" in title]
        self.window_combo.blockSignals(True)
        self.window_combo.clear()
        self.window_combo.addItem("请选择窗体", None)
        for hwnd, title in self._window_list:
            self.window_combo.addItem(title, hwnd)
        self.window_combo.blockSignals(False)
        self._on_window_changed(self.window_combo.currentIndex())

    def _on_window_changed(self, index: int) -> None:
        del index
        hwnd = self.window_combo.currentData()
        if isinstance(hwnd, int) and hwnd > 0:
            self.engine.set_target_window(hwnd)
        else:
            self.engine.set_target_window(None)
        self._update_start_enabled()

    def _update_start_enabled(self) -> None:
        can_start = self.engine.get_target_window() is not None
        self.start_btn.setEnabled(can_start and not self.engine.is_running())
        self._update_button_styles(running=self.engine.is_running(), can_start=can_start)

    def _update_button_styles(self, running: bool, can_start: bool | None = None) -> None:
        if can_start is None:
            can_start = self.engine.get_target_window() is not None

        if running:
            self.start_btn.setStyleSheet("background: #007bff; color: #ffffff;")
            self.stop_btn.setStyleSheet("background: #dc3545; color: #ffffff;")
            return

        if can_start:
            self.start_btn.setStyleSheet("background: #28a745; color: #ffffff;")
        else:
            self.start_btn.setStyleSheet("")
        self.stop_btn.setStyleSheet("")
