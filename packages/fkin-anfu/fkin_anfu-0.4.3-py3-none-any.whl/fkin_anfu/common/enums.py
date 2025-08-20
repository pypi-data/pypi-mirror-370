#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# vim: set tabstop=2 shiftwidth=2 textwidth=80 expandtab :
#
#
"""
定义通用枚举类型,包括解析任务类型(ParseType)与输出格式类型(OutputType)

@author: cyhfvg
@date: 2025/07/10
"""
from enum import Enum


class ParseType(str, Enum):
    """
    解析任务类型，用于标识当前解析任务的语义目的。
    """

    VULN = "vuln"  # 漏洞信息解析
    ASSET = "asset"  # 资产识别解析


class OutputType(str, Enum):
    """
    输出文件格式类型，决定最终生成文件的格式。
    """

    XLSX = "xlsx"  # 输出为 Excel 表格
    JSON = "json"  # 输出为 JSON 文件


class ScanTool(str, Enum):
    """
    扫描工具类型
    """

    AFROG = "afrog"
    FSCAN = "fscan"
    # # 未来扩展：
    # XRAY = "xray"
    # NUCLEI = "nuclei"
