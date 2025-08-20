#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# vim: set tabstop=2 shiftwidth=2 textwidth=80 expandtab :
#
#
"""
定义解析调度器 dispatch_parsers, 用于根据工具名称调度对应解析器并汇总结果。
解析器输出为统一 FindingResult 列表

@author: cyhfvg
@date: 2025/07/12
"""
from pathlib import Path
from typing import List, Tuple

from fkin_anfu.common.enums import ParseType
from fkin_anfu.parsers.afrog_parser import AfrogParser
from fkin_anfu.parsers.fscan_parser import FscanParser
from fkin_anfu.parsers.models.finding_result import FindingResult
from fkin_anfu.utils.color_utils import YELLOW
from fkin_anfu.utils.log_utils import debug_print

# 工具名到解析器实例的映射表
PARSER_REGISTRY = {
    "afrog": AfrogParser(),
    "fscan": FscanParser(),
    # 可扩展添加更多工具解析器，如：
    # "nuclei": NucleiParser(),
    # "masscan": MasscanParser(),
}


def dispatch_parsers(
    task_list: List[Tuple[str, Path, bool]],
    parse_type: ParseType,
) -> List[FindingResult]:
    """
    接收解析任务列表，分发至对应解析器并汇总所有结果为 FindingResult 列表。

    Args:
        task_list (List[Tuple[str, Path, bool]]): 每个元素为 (tool_name, path, recursive)
        parse_type (ParseType): 当前解析类型(vuln 或 asset)

    Returns:
        List[FindingResult]: 所有解析结果组成的列表（类型已筛选）
    """
    all_results: List[FindingResult] = []

    for tool, path, recursive in task_list:
        parser = PARSER_REGISTRY.get(tool)
        if parser is None:
            raise ValueError(f"[dispatch_parsers] 不支持的工具类型: {tool}")

        debug_print("INFO", f"[dispatch_parsers] 调用解析器: {tool} - 路径: {path} - 递归: {recursive}")

        results = parser.parse(path, recursive)

        # 仅保留类型匹配的项
        filtered = [item for item in results if item.finding_type == parse_type.value]

        all_results.extend(filtered)
        debug_print(
            "INFO",
            f"[parse_manager] 过滤 {tool}:{YELLOW(path.name)} 结果筛选解析 {parse_type.value} 信息 {YELLOW(len(filtered))} 条",
        )

    debug_print("INFO", f"[parse_manager] 共过滤筛选解析汇总 {parse_type.value} 信息 {len(YELLOW(all_results))} 条")

    if not all_results:
        debug_print("INFO", "[dispatch_parsers] 所有任务解析结果为空")

    return all_results
