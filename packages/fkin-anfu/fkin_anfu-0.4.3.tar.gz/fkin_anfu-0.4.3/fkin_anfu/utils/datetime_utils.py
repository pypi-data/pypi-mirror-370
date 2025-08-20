#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# vim: set tabstop=2 shiftwidth=2 textwidth=80 expandtab :
#
#
"""
时间日期工具

@author: cyhfvg
@date: 2025/04/20
"""
from datetime import datetime

__all__ = ['get_datetime_str', 'get_date_str']


def get_datetime_str() -> str:
    """
    返回当前时间字符串，格式为 YYYYMMDD_HHMM_SS。

    示例：
        >>> get_datetime_str()
        '20250413_2032_15'
    """
    return datetime.now().strftime("%Y%m%d_%H%M_%S")


def get_date_str() -> str:
    """
    返回当前日期字符串，格式为 YYYYMMDD。

    示例：
        >>> get_date_str()
        '20250413'
    """
    return datetime.now().strftime("%Y%m%d")
