#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# vim: set tabstop=2 shiftwidth=2 textwidth=80 expandtab :
#
#
"""
日志封装(colorama + logging + Lock)

@author: cyhfvg
@date: 2025/04/20
"""

import logging
from threading import Lock
from typing import Callable, Dict, Tuple

from fkin_anfu.utils.color_utils import BLUE, CYAN, GREEN, RED, YELLOW

__all__ = ['debug_print']

# 线程锁，保证日志打印不穿插
_log_lock = Lock()

# 创建一个独立的 logger, 避免污染 root logger
logger = logging.getLogger("fkin_anfu_log_utils")
logger.setLevel(logging.DEBUG)
# 不希望日志冒泡到父 logger，防止重复输出log
logger.propagate = False

# 如果没有 handler，主动加上
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# 默认 fallback设置
_DEFAULT_LOG_FUNC: Callable[[str], None] = logger.info
_DEFAULT_COLOR_FUNC: Callable[[str], str] = CYAN

# 日志级别与颜色函数的映射表
_LEVEL_MAP: Dict[str, Tuple[Callable[[str], None], Callable[[str], str]]] = {
    "debug": (logger.debug, BLUE),
    "info": (logger.info, CYAN),
    "success": (logger.info, GREEN),
    "warning": (logger.warning, YELLOW),
    "error": (logger.error, RED),
}


def debug_print(level: str, msg: str) -> None:
    """
    线程安全的统一日志输出接口，支持彩色控制台输出。

    :param level: 日志级别，如 "debug", "info", "success", "error", "warning"
    :param msg: 要输出的信息内容
    """
    level = level.lower()
    log_func, color_func = _LEVEL_MAP.get(level, (_DEFAULT_LOG_FUNC, _DEFAULT_COLOR_FUNC))
    tag = color_func(f"[{level.upper()}]")

    with _log_lock:
        log_func(f"{tag} {msg}")
