#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# vim: set tabstop=2 shiftwidth=2 textwidth=80 expandtab :
#
#
"""
字符串颜色高亮模块

功能特性：
- 支持 red/green/yellow/orange 等前景色设置
- 支持加粗样式控制
- 提供统一封装接口 highlight_text
- 提供常用快捷颜色函数 RED/GREEN/YELLOW/ORANGE 等

适用场景：
- CLI 输出高亮
- 日志重点字段着色
- 控制台交互提示增强

@author: cyhfvg
@date: 2025/07/19
"""

from colorama import Fore, Style, init

# 自动适配 Windows 控制台颜色支持
init(autoreset=False)

__all__ = ["highlight_text", "RED", "GREEN", "YELLOW", "ORANGE", "BLUE", "CYAN", "MAGENTA", "RESET"]

# 前景色映射表（按常见名称封装 colorama Fore 对象）
_COLOR_MAP: dict[str, str] = {
    "red": Fore.RED,
    "green": Fore.GREEN,
    "yellow": Fore.YELLOW,
    "orange": Fore.LIGHTRED_EX,
    "blue": Fore.BLUE,
    "cyan": Fore.CYAN,
    "magenta": Fore.MAGENTA,
}


def highlight_text(msg: str, color: str = "yellow", bold: bool = False) -> str:
    """
    对字符串添加颜色和加粗样式，支持 colorama 的标准色。

    Args:
        msg (str): 原始字符串内容
        color (str): 颜色名称(支持 red/green/yellow/orange/blue/cyan/magenta)
        bold (bool): 是否加粗(默认 False)

    Returns:
        str: 包含样式控制码的字符串，适用于终端输出

    Example:
        >>> highlight_text("警告信息", color="red", bold=True)
    """
    color_code: str = _COLOR_MAP.get(color.lower(), "")
    bold_code: str = Style.BRIGHT if bold else ""
    return f"{bold_code}{color_code}{msg}{Style.RESET_ALL}"


def RED(msg: str) -> str:
    """将字符串渲染为红色"""
    return highlight_text(msg, color="red")


def GREEN(msg: str) -> str:
    """将字符串渲染为绿色"""
    return highlight_text(msg, color="green")


def YELLOW(msg: str) -> str:
    """将字符串渲染为黄色"""
    return highlight_text(msg, color="yellow")


def ORANGE(msg: str) -> str:
    """将字符串渲染为橙色（使用 LIGHTRED 近似处理）"""
    return highlight_text(msg, color="orange")


def BLUE(msg: str) -> str:
    """将字符串渲染为蓝色"""
    return highlight_text(msg, color="blue")


def CYAN(msg: str) -> str:
    """将字符串渲染为青色"""
    return highlight_text(msg, color="cyan")


def MAGENTA(msg: str) -> str:
    """将字符串渲染为洋红色"""
    return highlight_text(msg, color="magenta")


def RESET() -> str:
    """
    返回终端颜色样式的重置码，用于手动拼接输出。

    Example:
        >>> print("前缀" + RED("危险") + RESET() + "后缀")
    """
    return Style.RESET_ALL
