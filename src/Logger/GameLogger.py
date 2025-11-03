from loguru import logger
import sys
from typing import Optional

#轻量封装: 支持自定义格式、一键调整全局日志等级
#from Logger.GameLogger import GameLogger
#log = GameLogger(level="INFO", to_file="logs/app.log", detailed=True)
#log = GameLogger(level="INFO", to_file=None, detailed=True)
#log = GameLogger(level="TRACE", to_file=None, detailed=False)
#log.set_level("TRACE")                         # 全局放开
#log.info("hello {}", "world")                  # 直接快捷方法

class GameLogger:

    _LEVELS = {"TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"}

    def __init__(self,
                 level: str = "TRACE",
                 to_file: Optional[str] = None,
                 rotation: str = "1 week",
                 retention: str = "4 weeks",
                 compression: str = "gz",
                 detailed: bool = True):
        
        # —— 细节模式 —— 
        self._format_detailed = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<cyan>{elapsed}</cyan> | "
            "<level>{level:<8}</level> | "
            "{file}:{line} | "
            "{thread.id}:{thread.name} | "
            "<level>{message}</level>"
        )
        # 简略模式：date | level | file | message
        self._format_brief = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>| "
            "<level>{level:<8}</level> | "
            "{file}:{line} | "
            "<level>{message}</level>"
        )

        # 保存配置，便于动态重建 sink
        self._file_path      = to_file
        self._rotation       = rotation
        self._retention      = retention
        self._compression    = compression
        self._detailed       = bool(detailed)
        self._current_level  = self._normalize_level(level)

        # 先清空默认 sink
        logger.remove()

        # 建立 sink
        self._console_sink_id = None
        self._file_sink_id    = None
        self._rebuild_sinks()

    # —— 入口 —— 
    def log(self, level: str, msg: str, *args, **kwargs):
        level_up = self._normalize_level(level)
        logger.log(level_up, msg, *args, **kwargs)
        
    # —— 一键修改全局日志等级(同时作用于控制台与文件) ——
    def set_level(self, level: str):
        self._current_level = self._normalize_level(level)
        self._rebuild_sinks() 

    # —— 直接按等级方法名调用 —— 
    def trace(self, msg, *args, **kwargs): logger.opt(depth=2).trace(msg, *args, **kwargs)
    def debug(self, msg, *args, **kwargs): logger.opt(depth=2).debug(msg, *args, **kwargs)
    def info(self, msg, *args, **kwargs):  logger.opt(depth=2).info(msg, *args, **kwargs)
    def success(self, msg, *args, **kwargs):  logger.opt(depth=2).success(msg, *args, **kwargs) 
    def warning(self, msg, *args, **kwargs):  logger.opt(depth=2).warning(msg, *args, **kwargs)
    def error(self, msg, *args, **kwargs): logger.opt(depth=2).error(msg, *args, **kwargs)
    def critical(self, msg, *args, **kwargs): logger.opt(depth=2).critical(msg, *args, **kwargs)

 # —— 动态切换详/简样式 —— 
    def set_detailed(self, detailed: bool):
        self._detailed = bool(detailed)
        self._rebuild_sinks()

    # —— 内部：重建 sink，应用当前等级 & 样式 —— 
    def _rebuild_sinks(self):
        # 移除旧 sink
        if self._console_sink_id is not None:
            logger.remove(self._console_sink_id)
        if self._file_sink_id is not None:
            logger.remove(self._file_sink_id)

        fmt = self._format_detailed if self._detailed else self._format_brief

        # 控制台
        self._console_sink_id = logger.add(
            sys.stdout,
            level=self._current_level,
            format=fmt,
            colorize=True,
            enqueue=True,
            backtrace=False,
            diagnose=False,
        )

        # 写入文件
        self._file_sink_id = None
        if self._file_path:
            self._file_sink_id = logger.add(
                self._file_path,
                level=self._current_level,
                format=fmt,
                encoding="utf-8",
                rotation=self._rotation,
                retention=self._retention,
                compression=self._compression,
                enqueue=True,
            )

    # —— 工具：等级规范化 —— 
    def _normalize_level(self, level: str) -> str:
        up = str(level).upper()
        if up not in self._LEVELS:
            raise ValueError(f"Unsupported level '{level}'. Use one of {sorted(self._LEVELS)}")
        return up


# 全局单例  
_global = None

def get_logger() -> GameLogger:
    global _global
    if _global is None:
        _global = GameLogger(level="INFO", to_file=None, detailed=True)
    return _global

# 代理函数
def trace(*a, **k):     get_logger().trace(*a, **k)
def debug(*a, **k):    get_logger().debug(*a, **k)
def info(*a, **k):     get_logger().info(*a, **k)
def success(*a, **k):     get_logger().success(*a, **k)
def warning(*a, **k):     get_logger().warning(*a, **k)
def error(*a, **k):     get_logger().error(*a, **k)
def critical(*a, **k):     get_logger().critical(*a, **k)
def set_level(lv):     get_logger().set_level(lv)
def set_detailed(b):   get_logger().set_detailed(b)
