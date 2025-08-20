#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# vim: set tabstop=2 shiftwidth=2 textwidth=80 expandtab :
#
#
"""
ip整形、处理工具

@author: cyhfvg
@date: 2025/07/01
"""
from __future__ import annotations

import ipaddress
import re
from collections import defaultdict

from fkin_anfu.utils.log_utils import debug_print
from fkin_anfu.utils.string_utils import replace_wide_chars

__all__ = [
    "is_valid_ipv4",
    "is_ip_in_network",
    "extract_ipv4s_from_text",
    "normalize_ipv4_string",
    "parse_ip_range",
    "omni_extend_ip_list",
    "group_ips_by_c_segment",
    "find_continuous_ranges",
    "format_ip_range",
    "shrink_ip_list",
]

# 模块级 IP 正则表达式对象
_IPV4_PATTERN = re.compile(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b")


def is_valid_ipv4(ip: str) -> bool:
    """
    判断是否为合法 IPv4 地址。

    Args:
        ip (str): 待校验的 IP 地址字符串

    Returns:
        bool: 若为合法 IPv4 地址返回 True,否则返回 False
    """
    try:
        ipaddress.IPv4Address(ip)
        return True
    except Exception as why:
        debug_print("DEBUG", f"[is_valid_ipv4] invalid ip: {ip}, reason: {why}")
        return False


def is_ip_in_network(ip: str, cidr: str) -> bool:
    """
    判断某 IP 地址是否位于指定的 CIDR 网段中。

    Args:
        ip (str): 待判断的 IPv4 地址
        cidr (str): CIDR 表示的网络段，如 '192.168.1.0/24'

    Returns:
        bool: 若 IP 落在 CIDR 中返回 True,否则 False
    """
    try:
        ip_obj = ipaddress.IPv4Address(ip)
        network_obj = ipaddress.IPv4Network(cidr, strict=False)
        return ip_obj in network_obj
    except Exception as why:
        debug_print("DEBUG", f"[is_ip_in_network] ip={ip}, cidr={cidr}, reason: {why}")
        return False


def extract_ipv4s_from_text(text: str) -> list[str]:
    """
    从文本中提取所有合法的 IPv4 地址，按出现顺序去重保留。

    Args:
        text (str): 包含 IP 字符串的原始文本

    Returns:
        list[str]: 提取出的合法 IPv4 地址列表
    """
    found = _IPV4_PATTERN.findall(text)
    seen = set()
    result = []
    for ip in found:
        if ip not in seen and is_valid_ipv4(ip):
            seen.add(ip)
            result.append(ip)
    return result


def normalize_ipv4_string(ip: str) -> str:
    """
    清洗 IP 字符串：去除空白字符、替换全角点号、剔除非数字和点。

    Args:
        ip (str): 原始 IP 字符串

    Returns:
        str: 清洗后的 IP 字符串
    """
    if not isinstance(ip, str):
        debug_print("DEBUG", "[normalize_ipv4_string] input is not string")
        return ""
    ip = ip.strip()
    ip = replace_wide_chars(ip)
    ip = re.sub(r"[^\d.]", "", ip)

    # 清洗后校验有效性
    if not is_valid_ipv4(ip):
        debug_print("DEBUG", f"[normalize_ipv4_string] invalid after cleaning: {ip}")
        return ""

    return ip


def parse_ip_range(ip_range: str) -> list[str]:
    """
    解析形如 '127.0.0.1-127.0.0.5' 的 IP 范围为 IP 列表。

    Args:
        ip_range (str): IP 范围字符串，使用连字符连接

    Returns:
        list[str]: 展开后的 IP 列表；若非法则返回空列表
    """
    if "-" not in ip_range:
        if is_valid_ipv4(ip_range):
            return [ip_range]
        return []

    start_ip, end_ip = ip_range.split("-", 1)
    try:
        start = ipaddress.IPv4Address(start_ip.strip())
        end = ipaddress.IPv4Address(end_ip.strip())
        if int(start) > int(end):
            return []
        return [str(ipaddress.IPv4Address(ip)) for ip in range(int(start), int(end) + 1)]
    except Exception as why:
        debug_print("DEBUG", f"[parse_ip_range] invalid input: {ip_range}, reason: {why}")
        return []


def omni_extend_ip_list(ip_orig: str) -> list[str]:
    """
    自动识别 IP 字符串类型(CIDR / 范围 / 单个)并展开为列表。

    Args:
        ip_orig (str): 原始 IP 输入字符串

    Returns:
        list[str]: 展开的 IP 列表
    """
    ip_orig = ip_orig.strip()
    if "/" in ip_orig:
        try:
            net = ipaddress.IPv4Network(ip_orig, strict=False)
            return [str(ip) for ip in net.hosts()]
        except Exception as why:
            debug_print("DEBUG", f"[omni_extend_ip_list] CIDR invalid: {ip_orig}, reason: {why}")
            return []
    elif "-" in ip_orig:
        return parse_ip_range(ip_orig)
    elif is_valid_ipv4(ip_orig):
        return [ip_orig]
    return []


def group_ips_by_c_segment(ip_list: list[str]) -> dict[str, list[str]]:
    """
    按 C 段（前三段）将 IP 地址列表归类。

    Args:
        ip_list (list[str]): IPv4 地址列表

    Returns:
        dict[str, list[str]]: 以 C 段为键的 IP 分组字典
    """
    result: dict[str, list[str]] = defaultdict(list)
    for ip in ip_list:
        if is_valid_ipv4(ip):
            parts = ip.split(".")
            c_segment = ".".join(parts[:3])
            result[c_segment].append(ip)
        else:
            debug_print("DEBUG", f"[group_ips_by_c_segment] skip invalid ip: {ip}")
    return dict(result)


def find_continuous_ranges(ips: list[str]) -> list[tuple[str, str]]:
    """
    将 IPv4 地址列表划分为连续的起止段。

    Args:
        ips (list[str]): 待处理的 IPv4 地址列表

    Returns:
        list[tuple[str, str]]: 每一项为连续段的 (起始 IP, 结束 IP)
    """
    ip_ints = sorted(set(int(ipaddress.IPv4Address(ip)) for ip in ips if is_valid_ipv4(ip)))
    if not ip_ints:
        return []

    ranges = []
    start = prev = ip_ints[0]
    for num in ip_ints[1:]:
        if num == prev + 1:
            prev = num
        else:
            ranges.append((str(ipaddress.IPv4Address(start)), str(ipaddress.IPv4Address(prev))))
            start = prev = num
    ranges.append((str(ipaddress.IPv4Address(start)), str(ipaddress.IPv4Address(prev))))
    return ranges


def format_ip_range(start_ip: str, end_ip_num: int) -> str:
    """
    将 IP 范围格式化为 '127.0.0.1-5' 形式。

    Args:
        start_ip (str): 起始 IP
        end_ip_num (int): 结束 IP 的最后一段数字

    Returns:
        str: 格式化后的 IP 范围字符串
    """
    return f"{start_ip}-{end_ip_num}" if is_valid_ipv4(start_ip) else ""


def shrink_ip_list(ip_list: list[str]) -> list[str]:
    """
    将 IP 地址列表整理为多个连续范围字符串。

    Args:
        ip_list (list[str]): IPv4 地址列表

    Returns:
        list[str]: 精简后的 IP 段表示列表(如 '127.0.0.1-5')
    """
    result = []
    ranges = find_continuous_ranges(ip_list)
    for start, end in ranges:
        if start == end:
            result.append(start)
        else:
            result.append(format_ip_range(start, int(end.split(".")[-1])))
    return result
