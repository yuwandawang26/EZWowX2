
import os
import sys
import logging
from datetime import datetime


class SmartLogManager:
    """智能日志管理器 - 支持动态开关、大小限制"""
    
    _instance = None
    _debug_enabled = False
    
    def __init__(self):
        self.log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        
        self.file_handler = None
        self.console_handler = None
        
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def setup(self, debug_mode=False):
        """初始化日志系统"""
        
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        
        # 清除已有的处理器
        root_logger.handlers.clear()
        
        # 日志文件名
        log_file = os.path.join(self.log_dir, f'ezwowx2_{datetime.now().strftime("%Y%m%d")}.log')
        
        # 文件处理器 - 根据模式设置级别
        file_level = logging.DEBUG if debug_mode else logging.WARNING
        self.file_handler = logging.FileHandler(log_file, encoding='utf-8', mode='a')
        self.file_handler.setLevel(file_level)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.file_handler.setFormatter(file_formatter)
        root_logger.addHandler(self.file_handler)
        
        # 控制台处理器 - 默认只显示WARNING及以上（不打扰用户）
        console_level = logging.INFO if debug_mode else logging.WARNING
        self.console_handler = logging.StreamHandler(sys.stdout)
        self.console_handler.setLevel(console_level)
        console_formatter = logging.Formatter('%(levelname)s: %(message)s')
        self.console_handler.setFormatter(console_formatter)
        root_logger.addHandler(self.console_handler)
        
        # 降低第三方库的日志级别
        logging.getLogger('comtypes._post_coinit').setLevel(logging.ERROR)
        logging.getLogger('comtypes.client').setLevel(logging.ERROR)
        logging.getLogger('dxcam').setLevel(logging.ERROR)
        
        SmartLogManager._debug_enabled = debug_mode
        
        return logging.getLogger(__name__)
    
    def toggle_debug(self, enable=None):
        """
        切换DEBUG模式
        enable: True=开启, False=关闭, None=切换
        返回: 当前DEBUG模式状态
        """
        if enable is None:
            SmartLogManager._debug_enabled = not SmartLogManager._debug_enabled
        else:
            SmartLogManager._debug_enabled = enable
        
        # 更新文件处理器级别
        if self.file_handler:
            new_level = logging.DEBUG if SmartLogManager._debug_enabled else logging.WARNING
            self.file_handler.setLevel(new_level)
            
            # 更新控制台处理器
            if self.console_handler:
                console_level = logging.INFO if SmartLogManager._debug_enabled else logging.WARNING
                self.console_handler.setLevel(console_level)
        
        logger = logging.getLogger(__name__)
        status = "ON" if SmartLogManager._debug_enabled else "OFF"
        logger.info(f"[LOG] Debug Mode: {status}")
        
        return SmartLogManager._debug_enabled
    
    def is_debug_enabled(self):
        return SmartLogManager._debug_enabled
    
    def get_log_size_mb(self):
        """获取当前所有日志文件总大小(MB)"""
        log_files = [f for f in os.listdir(self.log_dir) if f.endswith('.log')]
        total_size = sum(
            os.path.getsize(os.path.join(self.log_dir, f)) 
            for f in log_files
        )
        return round(total_size / (1024 * 1024), 2)
    
    def cleanup_old_logs(self, keep_days=7):
        """清理N天前的旧日志文件"""
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=keep_days)
        deleted_count = 0
        
        for filename in os.listdir(self.log_dir):
            if filename.endswith('.log'):
                filepath = os.path.join(self.log_dir, filename)
                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                
                if file_time < cutoff:
                    try:
                        os.remove(filepath)
                        deleted_count += 1
                    except Exception as e:
                        pass
        
        if deleted_count > 0:
            logger = logging.getLogger(__name__)
            logger.info(f"[LOG] Cleaned {deleted_count} old log files")
        
        return deleted_count


# 全局日志管理器实例
log_manager = SmartLogManager.get_instance()

# 初始化日志系统（默认关闭DEBUG模式）
logger = log_manager.setup(debug_mode=False)


