import sys
import os
import random
import time
import ctypes
import logging
from datetime import datetime
from typing import List, Any, Optional

import cv2
import numpy as np
import dxcam
from win32gui import EnumWindows, GetWindowText, IsWindow

from PySide6.QtCore import Qt, QThread, Signal, Slot, QObject
from PySide6.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QComboBox, QPushButton, QLineEdit, QMessageBox, QSystemTrayIcon, QMenu, QStyle
from PySide6.QtGui import QAction

from floating_window import FloatingWindow
from hotkey_manager import GlobalHotkeyManager
from settings_manager import SettingsManager
from skill_name_manager import SkillNameManager
from skill_name_editor import SkillNameEditor
from window_enumerator import WindowEnumerator


# 导入智能日志管理器
from smart_logging import SmartLogManager, log_manager, logger

WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101

KEY_COLOR_MAP = {
    '13,255,0': 'SHIFT-NUMPAD1',
    '0,255,64': 'SHIFT-NUMPAD2',
    '0,255,140': 'SHIFT-NUMPAD3',
    '0,255,217': 'SHIFT-NUMPAD4',
    '0,217,255': 'SHIFT-NUMPAD5',
    '0,140,255': 'SHIFT-NUMPAD6',
    '0,64,255': 'SHIFT-NUMPAD7',
    '13,0,255': 'SHIFT-NUMPAD8',
    '89,0,255': 'SHIFT-NUMPAD9',
    '166,0,255': 'SHIFT-NUMPAD0',
    '242,0,255': 'ALT-NUMPAD1',
    '255,0,191': 'ALT-NUMPAD2',
    '255,0,115': 'ALT-NUMPAD3',
    '255,0,38': 'ALT-NUMPAD4',
    '255,38,0': 'ALT-NUMPAD5',
    '255,115,0': 'ALT-NUMPAD6',
    '255,191,0': 'ALT-NUMPAD7',
    '242,255,0': 'ALT-NUMPAD8',
    '166,255,0': 'ALT-NUMPAD9',
    '89,255,0': 'ALT-NUMPAD0',
}

VK_DICT = {
    "SHIFT": 0x10, "CTRL": 0x11, "ALT": 0x12,
    "NUMPAD0": 0x60, "NUMPAD1": 0x61, "NUMPAD2": 0x62,
    "NUMPAD3": 0x63, "NUMPAD4": 0x64, "NUMPAD5": 0x65,
    "NUMPAD6": 0x66, "NUMPAD7": 0x67, "NUMPAD8": 0x68,
    "NUMPAD9": 0x69,
    "F1": 0x70, "F2": 0x71, "F3": 0x72, "F5": 0x74,
    "F6": 0x75, "F7": 0x76, "F8": 0x77, "F9": 0x78,
    "F10": 0x79, "F11": 0x7A,
}

MOD_MAP = {
    "CTRL": 0x0002, "CONTROL": 0x0002,
    "SHIFT": 0x0004, "ALT": 0x0001,
}


def find_all_matches(
    screenshot_array: np.ndarray,
    template_array: np.ndarray,
    threshold: float = 0.999,
) -> list[tuple[int, int]]:
    template_height, template_width = template_array.shape[:2]
    screenshot_height, screenshot_width = screenshot_array.shape[:2]
    if template_height > screenshot_height or template_width > screenshot_width:
        return []
    result = cv2.matchTemplate(screenshot_array, template_array, cv2.TM_CCOEFF_NORMED)
    match_locations = np.where(result >= threshold)
    matches = [(int(x), int(y)) for y, x in zip(match_locations[0], match_locations[1])]
    matches.sort()
    return matches


def find_template_bounds(
    screenshot_array: np.ndarray,
    threshold: float = 0.999,
) -> tuple[int, int, int, int] | None:
    try:
        template_array = np.array([
            [[255, 0, 0], [255, 0, 0], [0, 255, 0], [0, 255, 0]],
            [[255, 0, 0], [255, 0, 0], [0, 255, 0], [0, 255, 0]],
            [[0, 0, 0], [0, 0, 0], [0, 0, 255], [0, 0, 255]],
            [[0, 0, 0], [0, 0, 0], [0, 0, 255], [0, 0, 255]],
        ], dtype=np.uint8)
        template_height, template_width = template_array.shape[:2]
        matches = find_all_matches(screenshot_array, template_array, threshold)
        if len(matches) != 2:
            return None
        x1, y1 = matches[0]
        x2, y2 = matches[1]
        left = int(min(x1, x2))
        top = int(min(y1, y2))
        right = int(max(x1 + template_width, x2 + template_width))
        bottom = int(max(y1 + template_height, y2 + template_height))
        width, height = right - left, bottom - top
        if width % 4 != 0 or height % 4 != 0:
            return None
        return (left, top, right, bottom)
    except Exception:
        return None


def press_key_hwnd(hwnd: int, skey: str) -> None:
    key = VK_DICT.get(skey)
    if key is None:
        raise KeyError(f"Virtual key '{skey}' not found")
    ctypes.windll.user32.PostMessageW(hwnd, WM_KEYDOWN, key, 0)


def release_key_hwnd(hwnd: int, skey: str) -> None:
    key = VK_DICT.get(skey)
    if key is None:
        raise KeyError(f"Virtual key '{skey}' not found")
    ctypes.windll.user32.PostMessageW(hwnd, WM_KEYUP, key, 0)


def send_hot_key(hwnd: int, hot_key: str) -> None:
    key_list = hot_key.split("-")
    for skey in key_list:
        press_key_hwnd(hwnd, skey)
    time.sleep(0.01)
    for skey in reversed(key_list):
        release_key_hwnd(hwnd, skey)


def get_windows_by_title(title: str) -> List[int]:
    windows: List[tuple] = []

    def enum_callback(hwnd: int, _: Any) -> None:
        windows.append((hwnd, GetWindowText(hwnd)))

    EnumWindows(enum_callback, None)
    return [hwnd for hwnd, wt in windows if title.lower() in wt.lower()]


def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except AttributeError:
        return False


class WorkerThread(QThread):
    log_signal = Signal(str)
    key_sent_signal = Signal(str, str)
    error_occurred_signal = Signal(str)
    finished_signal = Signal()

    def __init__(self, hwnd: int, skill_manager: SkillNameManager = None):
        super().__init__()
        self.hwnd = hwnd
        self._running = False
        self._is_paused = False
        self.skill_manager = skill_manager

    def run(self):
        self._running = True
        camera = None
        try:
            camera = dxcam.create()
            
            max_init_retries = 20
            init_retry_interval = 1.0
            bounds = None
            
            for attempt in range(max_init_retries):
                if not self._running:
                    return
                
                frame = camera.grab()
                if frame is None:
                    logger.warning(f"[WORKER] 初始化尝试 {attempt + 1}/{max_init_retries}: 无法抓取屏幕帧")
                    time.sleep(init_retry_interval)
                    continue
                
                bounds = find_template_bounds(frame)
                if bounds is None:
                    logger.info(f"[WORKER] 初始化尝试 {attempt + 1}/{max_init_retries}: 等待战斗开始（颜色块区域未检测到）")
                    time.sleep(init_retry_interval)
                    continue
                
                logger.info(f"[WORKER] ✅ 成功找到颜色块区域 (尝试 {attempt + 1})")
                break
            else:
                self.error_occurred_signal.emit(f"初始化失败: {max_init_retries}次尝试后仍未检测到颜色块区域")
                logger.error(f"[WORKER] ❌ 初始化失败: {max_init_retries}次尝试后未找到模板")
                if camera:
                    camera.release()
                    camera.stop()
                    del camera
                return

            left, top, right, bottom = bounds
            if not ((right - left) == 12 and (bottom - top) == 4):
                self.error_occurred_signal.emit("模板大小不正确")
                logger.error(f"[WORKER] ❌ 模板大小不正确: {right-left}x{bottom-top} (期望: 12x4)")
                camera.release()
                camera.stop()
                del camera
                return

            region = (left + 4, top, right - 4, bottom)
            camera.release()
            camera.stop()
            del camera

            camera = dxcam.create(region=region)
            camera.start(target_fps=30)
            logger.info(f"[WORKER] 🎮 开始技能检测循环 (区域: {region})")

            while self._running:
                time.sleep(random.uniform(0.1, 0.2))

                while self._is_paused and self._running:
                    time.sleep(0.1)

                if not self._running:
                    break

                cropped_frame = camera.get_latest_frame()
                if cropped_frame is None:
                    continue
                if np.all(cropped_frame == cropped_frame[0, 0]):
                    pix = cropped_frame[0, 0]
                    if pix[0] == 255 and pix[1] == 255 and pix[2] == 255:
                        self.log_signal.emit("纯白")
                    elif pix[0] == 0 and pix[1] == 0 and pix[2] == 0:
                        self.log_signal.emit("纯黑")
                    else:
                        color_key = f"{pix[0]},{pix[1]},{pix[2]}"
                        key = KEY_COLOR_MAP.get(color_key)
                        if key is not None:
                            send_hot_key(self.hwnd, key)
                            self.log_signal.emit(f"发送按键: {key}")
                            self.key_sent_signal.emit(color_key, key)
                        else:
                            self.log_signal.emit(f"未知颜色: {color_key}")
                else:
                    self.log_signal.emit("不是纯色")

            logger.info("[WORKER] 🛑 技能检测循环已停止")
            camera.stop()
            camera.release()
            del camera
        except Exception as e:
            logger.error(f"[WORKER] ❌ 异常退出: {e}", exc_info=True)
            self.error_occurred_signal.emit(str(e))
        finally:
            if camera:
                try:
                    camera.stop()
                    camera.release()
                    del camera
                except:
                    pass
            self.finished_signal.emit()

    def stop(self):
        self._running = False

    def pause(self):
        self._is_paused = True

    def resume(self):
        self._is_paused = False

    def is_paused(self):
        return self._is_paused


class EZWowX2App(QObject):
    # 自定义信号：用于从热键线程安全地调用主线程方法
    hotkey_toggle_signal = Signal()

    def __init__(self):
        super().__init__()
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        self.skill_manager = SkillNameManager()
        self.settings = SettingsManager()
        self.floating_window = FloatingWindow()
        self.hotkey_manager = GlobalHotkeyManager()
        self.worker: Optional[WorkerThread] = None

        self._init_ui()
        self._setup_hotkeys()
        self._setup_tray()
        self._setup_callbacks()
        self._refresh_windows()

        self.floating_window.start_runtime_timer()

    def _init_ui(self):
        """初始化UI界面"""
        logger.info("初始化UI界面...")
        
        # 显示浮窗
        self.floating_window.show()
        logger.info("✓ 浮窗已显示")
        
        # 设置窗口位置（左上角）
        screen = self.app.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            x = 50
            y = 50
            self.floating_window.move(x, y)
            logger.info(f"✓ 窗口位置: ({x}, {y})")

    def _setup_hotkeys(self):
        # 连接信号：热键触发 → 主线程执行
        self.hotkey_toggle_signal.connect(self._on_toggle_pause)
        logger.info("✓ hotkey_toggle_signal 信号已连接到 _on_toggle_pause")

        def toggle_pause_from_hotkey():
            logger.info(">>> [HOTKEY] toggle_pause_from_hotkey 被触发!")
            logger.info("    [HOTKEY] 发射 hotkey_toggle_signal 信号...")
            self.hotkey_toggle_signal.emit()
            logger.info("    [HOTKEY] ✅ 信号已发射 (将自动切换到主线程执行)")

        def update_hotkey(new_hotkey: str):
            old_hotkey = self.floating_window.get_current_hotkey()
            self.hotkey_manager.unregister(old_hotkey)
            self.hotkey_manager.register(new_hotkey, toggle_pause_from_hotkey)
            self.floating_window.set_hotkey(new_hotkey)
            self.settings.set('hotkey', new_hotkey)
            logger.info(f"快捷键已更新: {old_hotkey} -> {new_hotkey}")

        self.floating_window._hotkey_callback = update_hotkey

        saved_hotkey = self.settings.get('hotkey', 'q')
        self.floating_window.set_hotkey(saved_hotkey)
        self.hotkey_manager.register(saved_hotkey, toggle_pause_from_hotkey)
        logger.info(f"初始快捷键已注册: '{saved_hotkey}' (大小写: {saved_hotkey.islower()})")

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
        logger.info("快捷键监听已启动")

    @Slot()
    def _on_toggle_pause(self):
        logger.info(">>> [TOGGLE] _on_toggle_pause 被调用")
        self._on_pause_click()

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

        self.floating_window.set_exit_callback(self._on_exit)

    def _setup_callbacks(self):
        self.floating_window.set_edit_skill_callback(self._on_edit_skills)
        self.floating_window.pause_button.mousePressEvent = lambda e: self._on_pause_click()

    def _refresh_windows(self):
        # 使用增强的窗口枚举器查找魔兽世界窗口
        wow_windows = WindowEnumerator.find_wow_windows()
        
        if wow_windows:
            self.floating_window.refresh_window_list(wow_windows)
            logger.info(f"已刷新魔兽世界窗口列表: {len(wow_windows)} 个")
            
            # 自动选择第一个魔兽世界窗口
            if not self.floating_window.get_selected_window():
                first_hwnd, first_title = wow_windows[0]
                index = self.floating_window.window_combo.findData(first_hwnd)
                if index >= 0:
                    self.floating_window.window_combo.setCurrentIndex(index)
                    logger.info(f"自动选择窗口: {first_title}")
        else:
            # 如果没有魔兽世界窗口，显示所有可见窗口
            windows = WindowEnumerator.enumerate_windows()
            self.floating_window.refresh_window_list(windows[:20])  # 限制显示数量
            logger.warning("未找到魔兽世界窗口，显示通用窗口列表")

    def _on_pause_click(self):
        logger.debug(f"_on_pause_click 被调用, worker={self.worker}, isRunning={self.worker.isRunning() if self.worker else 'N/A'}")
        
        # 记录当前前台窗口信息
        fg_hwnd, fg_title, fg_cls = WindowEnumerator.get_foreground_window()
        logger.debug(f"当前前台窗口: {fg_title} (HWND={fg_hwnd})")
        
        if self.worker is None or not self.worker.isRunning():
            hwnd = self.floating_window.get_selected_window()
            if hwnd is None:
                # 优先查找魔兽世界窗口
                wow_windows = WindowEnumerator.find_wow_windows()
                if wow_windows:
                    hwnd = wow_windows[0][0]
                    logger.info(f"自动选择魔兽世界窗口: {wow_windows[0][1]}")
                else:
                    self.floating_window.status_label.setText("未找到游戏")
                    logger.warning("未找到游戏窗口")
                    return

            try:
                logger.debug(f"创建WorkerThread, hwnd={hwnd}")
                
                # 验证目标窗口是否有效
                if not IsWindow(hwnd):
                    self.floating_window.status_label.setText("窗口无效")
                    logger.error(f"目标窗口无效或已关闭: {hwnd}")
                    return
                
                target_title = WindowEnumerator.get_window_title(hwnd)
                logger.info(f"目标窗口: {target_title}")
                
                self.worker = WorkerThread(hwnd, self.skill_manager)
                self.worker.log_signal.connect(self._on_log)
                self.worker.key_sent_signal.connect(self._on_key_sent)
                self.worker.error_occurred_signal.connect(self._on_error)
                self.worker.finished_signal.connect(self._on_finished)
                self.worker.start()
                logger.debug("WorkerThread已启动")

                self.floating_window.set_running_state(True, False)
                self.floating_window.update_skill_name("", "运行中...")
                
            except Exception as e:
                logger.error(f"启动失败: {e}", exc_info=True)
                self.floating_window.status_label.setText(f"启动失败: {str(e)[:30]}")
                return
        else:
            if self.worker.is_paused():
                self.worker.resume()
                self.floating_window.set_running_state(True, False)
                logger.debug("Worker已恢复")
                self.floating_window.update_skill_name("", "运行中...")
            else:
                self.worker.pause()
                self.floating_window.set_running_state(True, True)
                logger.debug("Worker已暂停")
                self.floating_window.update_skill_name("", "已暂停")

    def _on_log(self, msg: str):
        pass

    def _on_key_sent(self, color_key: str, key: str):
        skill_name = self.skill_manager.get_name(color_key)
        self.floating_window.update_skill_name(color_key, skill_name)

        for i in range(2, 0, -1):
            self.floating_window.key_log_items[i].setText(
                self.floating_window.key_log_items[i - 1].text()
            )
        self.floating_window.key_log_items[0].setText(f"▶ {key} ({color_key})")
        self.floating_window.increment_key_count()

    def _on_error(self, msg: str):
        logger.error(f"[ERROR] WorkerThread错误: {msg}")
        self.floating_window.increment_error_count()
        self.floating_window.status_label.setText(f"⚠ {str(msg)[:20]}")

    def _on_finished(self):
        logger.debug("Worker已完成")
        self.worker = None
        self.floating_window.set_running_state(False, False)

    def _on_edit_skills(self):
        dialog = SkillNameEditor(self.skill_manager, self.floating_window)
        dialog.exec()

    def _on_exit(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
        self.floating_window.stop_runtime_timer()
        self.hotkey_manager.stop_listening()
        self.tray.hide()
        self.app.quit()

    def run(self):
        sys.exit(self.app.exec())


def main():
    mutex_name = "EZAssistedX2"
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, mutex_name)
    already_running = ctypes.windll.kernel32.GetLastError() == 183

    if already_running:
        app_check = QApplication(sys.argv)
        QMessageBox.information(None, "EZAssistedX2", "程序已在运行中。")
        sys.exit(0)

    if not is_admin():
        app_check = QApplication(sys.argv)
        QMessageBox.information(None, "EZAssistedX2", "必须以UAC管理员身份运行。")
        sys.exit(0)

    app = EZWowX2App()
    app.run()

    ctypes.windll.kernel32.ReleaseMutex(mutex)
    ctypes.windll.kernel32.CloseHandle(mutex)


if __name__ == "__main__":
    main()