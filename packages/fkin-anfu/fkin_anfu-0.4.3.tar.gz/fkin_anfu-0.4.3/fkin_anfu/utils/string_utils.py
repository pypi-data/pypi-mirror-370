#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# vim: set tabstop=2 shiftwidth=2 textwidth=80 expandtab :

"""
字符串处理工具函数集合

适用于文本清洗、空白判断、脱敏、空格归一化、分隔解析等常用场景。
"""

import re
from typing import List, Optional

__all__ = [
    "is_blank",
    "remove_all_whitespace",
    "split_and_strip",
    "mask_string",
    "normalize_spaces",
    "regex_match",
    "replace_wide_chars",
    "replace_wide_chars_in_list",
    "remove_all_whitespace_from_list",
]


def is_blank(s: Optional[str]) -> bool:
    """
    判断字符串是否为空或全是空白字符（如 None、空串、空格、Tab）

    :param s: 输入字符串，可为 None
    :return: True 表示字符串为空或仅由空白字符组成

    示例：
        >>> is_blank(None)
        True
        >>> is_blank("   ")
        True
        >>> is_blank("abc")
        False
    """
    return not s or s.strip() == ""


def remove_all_whitespace(s: str) -> str:
    """
    移除字符串中所有空白字符(空格、Tab、换行等）

    :param s: 原始字符串
    :return: 所有空白字符被移除的结果字符串

    示例：
        >>> remove_all_whitespace("a b\tc\n")
        'abc'
    """
    return re.sub(r"\s+", "", s)


def remove_all_whitespace_from_list(strings: List[str]) -> List[str]:
    """
    移除列表中每个字符串元素的所有空白字符(空格、Tab、换行等)

    :param strings: 包含多个字符串的列表
    :return: 每个字符串元素的空白字符被移除后的新列表

    示例：
        >>> remove_all_whitespace_from_list(["a b\tc\n", " d e f "])
        ['abc', 'def']
    """
    return [remove_all_whitespace(s) for s in strings]


def split_and_strip(s: str, sep: str = ",") -> List[str]:
    """
    按分隔符切分字符串，并对每个子项去除首尾空白字符

    :param s: 原始字符串
    :param sep: 分隔符（默认逗号）
    :return: 去除空白后的子字符串列表，过滤空项

    示例：
        >>> split_and_strip(" a , b ,c ")
        ['a', 'b', 'c']
    """
    return [part.strip() for part in s.split(sep) if part.strip()]


def mask_string(s: str, keep: int = 1) -> str:
    """
    字符串脱敏，仅保留前后字符，其余部分用 * 替代

    :param s: 原始字符串
    :param keep: 保留前后字符数，默认为 1
    :return: 脱敏后的字符串

    示例：
        >>> mask_string("password", keep=1)
        'p******d'
        >>> mask_string("abc", keep=1)
        'a*c'
        >>> mask_string("ab", keep=1)
        '**'
    """
    if len(s) <= keep * 2:
        return "*" * len(s)
    return s[:keep] + "*" * (len(s) - keep * 2) + s[-keep:]


def normalize_spaces(s: str) -> str:
    """
    归并多个连续空格为一个，并去除首尾空格

    :param s: 原始字符串
    :return: 清洗后的字符串

    示例：
        >>> normalize_spaces("  a   b c  ")
        'a b c'
    """
    return re.sub(r"\s+", " ", s).strip()


def regex_match(s: str, pattern: str) -> bool:
    """
    判断字符串是否完整匹配正则表达式

    :param s: 输入字符串
    :param pattern: 正则表达式（需完整匹配）
    :return: 是否匹配

    示例：
        >>> regex_match("abc123", r"[a-z]+\\d+")
        True
        >>> regex_match("abc123xyz", r"[a-z]+\\d+")
        False
    """
    return bool(re.fullmatch(pattern, s))


def replace_wide_chars(s: str, exclude: Optional[List[str]] = None) -> str:
    """
    替换常见中文宽字符标点为半角英文标点，支持白名单排除

    :param s: 原始字符串
    :param exclude: 不参与替换的字符列表，默认为空（全部替换）
    :return: 替换后的新字符串

    示例：
        >>> replace_wide_chars("你好，世界。")
        '你好,世界.'
        >>> replace_wide_chars("【示例】《标题》。", exclude=["【", "】"])
        '【示例】<标题>.'
    """
    wide_map = {
        "．": ".",
        "，": ",",
        "。": ".",
        "；": ";",
        "：": ":",
        "！": "!",
        "？": "?",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "【": "[",
        "】": "]",
        "《": "<",
        "》": ">",
        "（": "(",
        "）": ")",
        "、": "/",
        "——": "-",
        "～": "~",
        "……": "...",
    }

    if exclude:
        for ch in exclude:
            wide_map.pop(ch, None)

    for wide_char, ascii_char in wide_map.items():
        s = s.replace(wide_char, ascii_char)

    return s


def replace_wide_chars_in_list(strings: List[str], exclude: Optional[List[str]] = None) -> List[str]:
    """
    替换列表中每个字符串的常见中文宽字符标点为半角英文标点，支持白名单排除

    :param strings: 包含多个字符串的列表
    :param exclude: 不参与替换的字符列表，默认为空（全部替换）
    :return: 每个字符串元素的宽字符标点被替换后的新列表

    示例：
        >>> replace_wide_chars_in_list(["你好，世界。", "【示例】《标题》。"])
        ['你好,世界.', '[示例]<标题>.']
    """
    return [replace_wide_chars(s, exclude) for s in strings]
