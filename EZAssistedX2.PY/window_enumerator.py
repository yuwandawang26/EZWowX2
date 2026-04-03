import win32gui
import win32con
import win32process
import ctypes
import logging

logger = logging.getLogger(__name__)


class WindowEnumerator:
    """窗口枚举器 - 增强版，支持窗口焦点检测"""

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
                    except Exception as e:
                        logger.debug(f"枚举窗口异常: {e}")

        win32gui.EnumWindows(callback, None)
        return result

    @staticmethod
    def get_window_title(hwnd: int) -> str:
        try:
            return win32gui.GetWindowText(hwnd)
        except:
            return ""

    @staticmethod
    def get_foreground_window() -> tuple:
        """
        获取当前前台窗口信息
        返回: (hwnd, title, class_name)
        """
        try:
            hwnd = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(hwnd)
            cls_name = win32gui.GetClassName(hwnd)
            return (hwnd, title, cls_name)
        except Exception as e:
            logger.error(f"获取前台窗口失败: {e}")
            return (None, None, None)

    @staticmethod
    def is_window_focused(hwnd: int) -> bool:
        """
        检查指定窗口是否为前台窗口
        """
        try:
            foreground_hwnd = win32gui.GetForegroundWindow()
            return foreground_hwnd == hwnd
        except Exception as e:
            logger.error(f"检查窗口焦点失败: {e}")
            return False

    @staticmethod
    def find_wow_windows():
        """
        查找所有魔兽世界窗口
        返回: [(hwnd, title), ...]
        """
        windows = WindowEnumerator.enumerate_windows()
        wow_windows = [(hwnd, title) for hwnd, title in windows 
                       if "魔兽世界" in title or "World of Warcraft" in title]
        
        if wow_windows:
            logger.info(f"找到 {len(wow_windows)} 个魔兽世界窗口")
            for hwnd, title in wow_windows:
                logger.debug(f"  - HWND: {hwnd}, 标题: {title}")
        else:
            logger.warning("未找到魔兽世界窗口")
        
        return wow_windows

    @staticmethod
    def get_process_id(hwnd: int) -> int:
        """
        获取窗口所属的进程ID
        """
        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            return pid
        except Exception as e:
            logger.error(f"获取进程ID失败: {e}")
            return 0

    @staticmethod
    def bring_to_front(hwnd: int):
        """
        将指定窗口带到前台
        """
        try:
            if not win32gui.IsWindow(hwnd):
                logger.error(f"窗口句柄无效: {hwnd}")
                return False
            
            # 如果窗口被最小化，先恢复
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            
            # 设置为前台窗口
            win32gui.SetForegroundWindow(hwnd)
            logger.debug(f"已将窗口 {hwnd} 带到前台")
            return True
            
        except Exception as e:
            logger.error(f"将窗口带到前台失败: {e}")
            return False

    @staticmethod
    def monitor_focus_change(callback, interval_ms: int = 500):
        """
        监控窗口焦点变化（需要在线程中运行）
        callback: 回调函数，参数为新前台窗口信息 (hwnd, title, cls_name)
        """
        import time
        
        last_hwnd = None
        
        while True:
            try:
                current_hwnd, title, cls_name = WindowEnumerator.get_foreground_window()
                
                if current_hwnd != last_hwnd:
                    if last_hwnd is not None:
                        callback(current_hwnd, title, cls_name)
                    last_hwnd = current_hwnd
                
                time.sleep(interval_ms / 1000.0)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"监控焦点变化异常: {e}")
                time.sleep(1)


if __name__ == "__main__":
    print("=" * 60)
    print("窗口枚举器测试")
    print("=" * 60)
    
    # 测试1：获取前台窗口
    print("\n[1] 当前前台窗口:")
    hwnd, title, cls_name = WindowEnumerator.get_foreground_window()
    print(f"  句柄: {hwnd}")
    print(f"  标题: {title}")
    print(f"  类名: {cls_name}")
    
    # 测试2：查找魔兽世界窗口
    print("\n[2] 魔兽世界窗口:")
    wow_windows = WindowEnumerator.find_wow_windows()
    for hwnd, title in wow_windows:
        print(f"  - {title} (HWND: {hwnd})")
    
    # 测试3：列出所有可见窗口（前10个）
    print("\n[3] 可见窗口列表 (前10个):")
    windows = WindowEnumerator.enumerate_windows()
    for i, (hwnd, title) in enumerate(windows[:10]):
        focused = " [FOCUSED]" if hwnd == WindowEnumerator.get_foreground_window()[0] else ""
        print(f"  {i+1}. {title[:40]:<40} ({hwnd}){focused}")
