#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# vim: set tabstop=2 shiftwidth=2 textwidth=80 expandtab :
#
#
"""
模块功能：
    数据输出能力，支持导出为 Excel 或 JSON 文件。
    默认使用 UTF-8 编码,Excel 使用 openpyxl 实现。

    - 支持FindingResult输出

@author: cyhfvg
@date: 2025/07/17
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence, Union

import pandas as pd

from fkin_anfu.parsers.models.finding_result import FindingResult

__all__ = [
    "export_findings_to_excel",
    "export_findings_to_json",
]


def export_findings_to_excel(findings: Sequence[FindingResult], output_path: Union[Path, str]) -> None:
    """
    将漏洞列表导出为 Excel 文件(.xlsx)。

    Args:
        findings (Sequence[FindingResult]): FindingResult 对象列表
        output_path (Path): 输出文件路径，需以 .xlsx 结尾
    """
    if not findings:
        raise ValueError("Empty finding list, no data to export")

    output_path = Path(output_path)

    df = pd.DataFrame([f.model_dump() for f in findings])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(output_path, index=False, engine="openpyxl")


def export_findings_to_json(findings: Sequence[FindingResult], output_path: Union[Path, str]) -> None:
    """
    将漏洞列表导出为 JSON 文件.

    Args:
        findings (Sequence[FindingResult]): FindingResult 对象列表
        output_path (Path): 输出文件路径，需以 .json 结尾
    """
    if not findings:
        raise ValueError("Empty finding list, no data to export")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump([f.model_dump() for f in findings], f, ensure_ascii=False, indent=2)
