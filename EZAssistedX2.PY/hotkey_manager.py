import ctypes
import ctypes.wintypes as wintypes
import threading
import logging
import time
from typing import Callable, Tuple, Optional, Dict

# 使用根日志记录器（已在主程序中配置）
logger = logging.getLogger(__name__)

# Win32 常量
WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100
WM_SYSKEYDOWN = 0x0104
VK_CODE_MAP = {
    'a': 0x41, 'b': 0x42, 'c': 0x43, 'd': 0x44, 'e': 0x45,
    'f': 0x46, 'g': 0x47, 'h': 0x48, 'i': 0x49, 'j': 0x4A,
    'k': 0x4B, 'l': 0x4C, 'm': 0x4D, 'n': 0x4E, 'o': 0x4F,
    'p': 0x50, 'q': 0x51, 'r': 0x52, 's': 0x53, 't': 0x54,
    'u': 0x55, 'v': 0x56, 'w': 0x57, 'x': 0x58, 'y': 0x59,
    'z': 0x5A,
}

MODIFIER_CODES = {
    'ctrl': 0x11, 'control': 0x11,
    'shift': 0x10,
    'alt': 0x12,
}


class GlobalHotkeyManager:
    """
    全局快捷键管理器
    
    使用两种方案：
    1. 首选方案: Win32 Low-Level Keyboard Hook (线程级别)
    2. 备用方案: 轮询检测 (GetAsyncKeyState)
    """

    def __init__(self):
        self._single_key_callbacks: Dict[str, Callable] = {}
        self._hotkey_callbacks: Dict[str, Callable] = {}
        self._running = False
        self._listener_thread: Optional[threading.Thread] = None
        self._polling_thread: Optional[threading.Thread] = None
        self._hook_id = None
        self._use_polling = False  # 是否使用轮询模式
        
        # 加载Win32 DLL
        try:
            self.user32 = ctypes.WinDLL('user32.dll', use_last_error=True)
            self.kernel32 = ctypes.WinDLL('kernel32.dll', use_last_error=True)
            logger.debug("Win32 DLL加载成功")
        except Exception as e:
            logger.error(f"加载Win32 DLL失败: {e}")
            raise

    def register(self, key: str, callback: Callable):
        key = key.lower()
        if key in self._single_key_callbacks:
            logger.debug(f"按键 {key} 已注册，跳过")
            return

        self._single_key_callbacks[key] = callback
        logger.debug(f"注册单键: {key} (VK码: {VK_CODE_MAP.get(key, 'N/A')})")

    def register_combo(self, modifiers: Tuple[str, ...], key: str, callback: Callable):
        combo_key = f"{'+'.join(modifiers)}+{key.lower()}"
        self._hotkey_callbacks[combo_key] = callback
        logger.debug(f"注册组合键: {combo_key}")

    def unregister(self, key: str):
        key = key.lower()
        if key in self._single_key_callbacks:
            del self._single_key_callbacks[key]
            logger.debug(f"注销单键: {key}")

    def unregister_all(self):
        self._single_key_callbacks.clear()
        self._hotkey_callbacks.clear()
        logger.debug("已清除所有快捷键注册")

    def start_listening(self, blocking: bool = True):
        if self._running:
            logger.warning("监听已在运行中")
            return
            
        self._running = True
        
        # 尝试安装键盘钩子
        hook_installed = self._try_install_hook()
        
        if hook_installed:
            logger.info("✓ 使用Hook模式监听按键")
            if blocking:
                self._run_message_loop()
            else:
                self._listener_thread = threading.Thread(target=self._run_message_loop, daemon=True)
                self._listener_thread.start()
                logger.debug("非阻塞模式：Hook监听线程已启动")
        else:
            # Hook失败，使用轮询模式
            logger.warning("⚠ Hook安装失败，切换到轮询模式")
            self._use_polling = True
            
            if blocking:
                self._run_polling_loop()
            else:
                self._polling_thread = threading.Thread(target=self._run_polling_loop, daemon=True)
                self._polling_thread.start()
                logger.debug("非阻塞模式：轮询监听线程已启动")

    def _try_install_hook(self) -> bool:
        """尝试安装键盘钩子，返回是否成功"""
        try:
            # 定义KBDLLHOOKSTRUCT结构体
            class KBDLLHOOKSTRUCT(ctypes.Structure):
                _fields_ = [
                    ("vkCode", wintypes.DWORD),
                    ("scanCode", wintypes.DWORD),
                    ("flags", wintypes.DWORD),
                    ("time", wintypes.DWORD),
                    ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG)),
                ]

            # 定义回调函数原型
            HOOKPROC = ctypes.CFUNCTYPE(
                ctypes.c_int,
                ctypes.c_int,
                wintypes.WPARAM,
                wintypes.LPARAM,
            )

            # 创建钩子回调函数
            def low_level_keyboard_proc(nCode, wParam, lParam):
                try:
                    if nCode >= 0:
                        if wParam == WM_KEYDOWN or wParam == WM_SYSKEYDOWN:
                            kbd_struct = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
                            
                            vk_code = kbd_struct.vkCode
                            
                            # 忽略注入的按键
                            if not (kbd_struct.flags & 0x10):  # LLKHF_INJECTED
                                self._process_key_event(vk_code)
                except Exception as e:
                    logger.error(f"键盘钩子回调异常: {e}")
                
                return self.user32.CallNextHookExW(self._hook_id, nCode, wParam, lParam)

            # 创建回调并保持引用
            self._hook_proc = HOOKPROC(low_level_keyboard_proc)
            
            # 对于线程级别Hook，使用当前线程ID和NULL模块句柄
            thread_id = self.kernel32.GetCurrentThreadId()
            
            logger.debug(f"尝试安装线程级Hook (ThreadID={thread_id})...")
            
            # 安装线程级键盘钩子 (dwThreadId != 0)
            self._hook_id = self.user32.SetWindowsHookExW(
                WH_KEYBOARD_LL,
                self._hook_proc,
                None,  # 线程级Hook可以使用None
                thread_id  # 当前线程ID
            )
            
            if not self._hook_id:
                error = ctypes.get_last_error()
                logger.warning(f"线程级Hook安装失败 (错误代码: {error})，将使用轮询模式")
                return False
            
            logger.info(f"✓ 键盘钩子已安装成功，Hook ID: {self._hook_id}")
            return True
            
        except Exception as e:
            logger.error(f"安装键盘钩子异常: {e}")
            return False

    def _run_polling_loop(self):
        """轮询模式：定期检查按键状态"""
        logger.info("开始轮询模式监听...")
        
        # 记录上一次的按键状态，避免重复触发
        last_pressed = set()
        
        # 防抖动：记录每个按键最后触发的时间
        last_trigger_time = {}
        debounce_interval = 0.3  # 300ms防抖间隔
        
        poll_interval = 0.03  # 30ms轮询间隔 (~33Hz) - 更快的响应
        
        while self._running:
            try:
                current_time = time.time()
                
                # 检查所有已注册的单键
                for key_name in list(self._single_key_callbacks.keys()):
                    if key_name not in VK_CODE_MAP:
                        continue
                    
                    vk_code = VK_CODE_MAP[key_name]
                    
                    # GetAsyncKeyState 返回值的最高位表示按键是否按下
                    state = self.user32.GetAsyncKeyState(vk_code)
                    is_pressed = (state & 0x8000) != 0
                    
                    if is_pressed and key_name not in last_pressed:
                        # 按键刚按下（上升沿）
                        last_pressed.add(key_name)
                        
                        # 检查防抖
                        if key_name in last_trigger_time:
                            time_since_last = current_time - last_trigger_time[key_name]
                            if time_since_last < debounce_interval:
                                logger.debug(f"按键 {key_name} 防抖中 ({time_since_last*1000:.0f}ms < {debounce_interval*1000:.0f}ms)")
                                continue
                        
                        # 记录触发时间
                        last_trigger_time[key_name] = current_time
                        
                        logger.info(f"✓ 轮询检测到按键: {key_name} (VK=0x{vk_code:02X})")
                        
                        try:
                            self._single_key_callbacks[key_name]()
                            logger.debug(f"  → {key_name} 回调执行成功")
                        except Exception as ex:
                            logger.error(f"  ✗ 单键回调异常 ({key_name}): {ex}", exc_info=True)
                    
                    elif not is_pressed and key_name in last_pressed:
                        # 按键释放
                        last_pressed.discard(key_name)
                
                # 检查组合键
                for combo_key in list(self._hotkey_callbacks.keys()):
                    parts = combo_key.split('+')
                    if len(parts) < 2:
                        continue
                    
                    modifiers = parts[:-1]
                    target_key = parts[-1]
                    
                    if target_key not in VK_CODE_MAP:
                        continue
                    
                    # 检查修饰键状态
                    ctrl_ok = 'ctrl' in modifiers and (self.user32.GetAsyncKeyState(MODIFIER_CODES['ctrl']) & 0x8000) != 0
                    shift_ok = 'shift' in modifiers and (self.user32.GetAsyncKeyState(MODIFIER_CODES['shift']) & 0x8000) != 0
                    
                    # 检查目标键状态
                    target_vk = VK_CODE_MAP[target_key]
                    target_pressed = (self.user32.GetAsyncKeyState(target_vk) & 0x8000) != 0
                    
                    # 组合键组合标识
                    combo_id = f"combo_{combo_key}"
                    
                    if target_pressed:
                        # 检查所有修饰键是否都按下
                        all_modifiers_pressed = True
                        if 'ctrl' in modifiers and not ctrl_ok:
                            all_modifiers_pressed = False
                        if 'shift' in modifiers and not shift_ok:
                            all_modifiers_pressed = False
                        
                        if all_modifiers_pressed and combo_id not in last_pressed:
                            # 检查防抖
                            if combo_id in last_trigger_time:
                                time_since_last = current_time - last_trigger_time[combo_id]
                                if time_since_last < debounce_interval:
                                    continue
                            
                            last_pressed.add(combo_id)
                            last_trigger_time[combo_id] = current_time
                            
                            logger.info(f"✓ 轮询检测到组合键: {combo_key}")
                            
                            try:
                                self._hotkey_callbacks[combo_key]()
                                logger.debug(f"  → {combo_key} 回调执行成功")
                            except Exception as ex:
                                logger.error(f"  ✗ 组合键回调异常 ({combo_key}): {ex}", exc_info=True)
                        
                        elif not all_modifiers_pressed and combo_id in last_pressed:
                            last_pressed.discard(combo_id)
                    elif combo_id in last_pressed:
                        last_pressed.discard(combo_id)
                
                time.sleep(poll_interval)
                
            except Exception as e:
                logger.error(f"轮询循环异常: {e}")
                time.sleep(1)  # 出错后等待1秒再继续
        
        logger.info("轮询模式结束")

    def _process_key_event(self, vk_code: int):
        """处理按键事件"""
        try:
            # 检查修饰键状态
            ctrl_pressed = (self.user32.GetAsyncKeyState(MODIFIER_CODES['ctrl']) & 0x8000) != 0
            shift_pressed = (self.user32.GetAsyncKeyState(MODIFIER_CODES['shift']) & 0x8000) != 0
            
            # 查找对应的字母键
            pressed_key = None
            for key_name, code in VK_CODE_MAP.items():
                if code == vk_code:
                    pressed_key = key_name
                    break
            
            if not pressed_key:
                return
            
            logger.debug(f"Hook按键事件: VK=0x{vk_code:02X}, Key={pressed_key}, Ctrl={ctrl_pressed}, Shift={shift_pressed}")
            
            # 检查组合键 (Ctrl+Shift+X)
            if ctrl_pressed and shift_pressed:
                combo_key = f"ctrl+shift+{pressed_key}"
                if combo_key in self._hotkey_callbacks:
                    logger.debug(f"触发组合键回调: {combo_key}")
                    try:
                        self._hotkey_callbacks[combo_key]()
                    except Exception as ex:
                        logger.error(f"组合键回调异常 ({combo_key}): {ex}")
                    return
            
            # 检查组合键 (Ctrl+X)
            if ctrl_pressed:
                combo_key = f"ctrl+{pressed_key}"
                if combo_key in self._hotkey_callbacks:
                    logger.debug(f"触发组合键回调: {combo_key}")
                    try:
                        self._hotkey_callbacks[combo_key]()
                    except Exception as ex:
                        logger.error(f"组合键回调异常 ({combo_key}): {ex}")
                    return
            
            # 检查单键
            if pressed_key in self._single_key_callbacks:
                logger.debug(f"触发单键回调: {pressed_key}")
                try:
                    self._single_key_callbacks[pressed_key]()
                except Exception as ex:
                    logger.error(f"单键回调异常 ({pressed_key}): {ex}")
                    
        except Exception as e:
            logger.error(f"处理按键事件异常: {e}", exc_info=True)

    def _run_message_loop(self):
        """消息循环 (Hook模式)"""
        logger.info("开始消息循环...")
        
        MSG = wintypes.MSG()
        while self._running:
            try:
                ret = self.user32.GetMessageW(ctypes.byref(MSG), None, 0, 0)
                if ret == 0:  # WM_QUIT
                    break
                elif ret == -1:
                    error = ctypes.get_last_error()
                    logger.error(f"GetMessage失败，错误代码: {error}")
                    break
                
                self.user32.TranslateMessage(ctypes.byref(MSG))
                self.user32.DispatchMessageW(ctypes.byref(MSG))
            except Exception as e:
                logger.error(f"消息循环异常: {e}")
                break
        
        logger.info("消息循环结束")

    def stop_listening(self):
        logger.info("停止监听...")
        self._running = False
        
        # 卸载钩子
        if self._hook_id:
            result = self.user32.UnhookWindowsHookEx(self._hook_id)
            if result:
                logger.info("键盘钩子已卸载")
            else:
                error = ctypes.get_last_error()
                logger.error(f"卸载键盘钩子失败，错误代码: {error}")
            self._hook_id = None
        
        # 清空注册表
        self.unregister_all()


if __name__ == "__main__":
    print("=" * 60)
    print(" Hotkey Manager Test (Hybrid Mode)")
    print("=" * 60)
    
    manager = GlobalHotkeyManager()
    
    def on_q_press():
        print("\n[OK] Q key pressed!")
    
    def on_ctrl_shift_e():
        print("\n[OK] Ctrl+Shift+E pressed!")
    
    manager.register('q', on_q_press)
    manager.register_combo(('ctrl', 'shift'), 'e', on_ctrl_shift_e)
    
    print("\nRegistered hotkeys:")
    print("  - Q: Toggle pause")
    print("  - Ctrl+Shift+E: Expand/collapse")
    print("\nMode: Auto-detect (Hook or Polling)")
    print("Press Ctrl+C to exit...\n")
    
    try:
        manager.start_listening(blocking=True)
    except KeyboardInterrupt:
        print("\n\nExiting...")
        manager.stop_listening()
