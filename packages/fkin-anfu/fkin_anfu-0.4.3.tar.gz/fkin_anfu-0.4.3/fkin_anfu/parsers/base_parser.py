#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# vim: set tabstop=2 shiftwidth=2 textwidth=80 expandtab :
#
#
"""
定义解析器抽象基类，用于约束所有扫描工具解析器必须实现统一的 parse 方法。
每个解析器负责将扫描工具的输出文件（单个或目录）解析为 FindingResult 数据结构列表。

@author: cyhfvg
@date: 2025/07/11
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from fkin_anfu.parsers.models.finding_result import FindingResult


class BaseParser(ABC):
    """
    抽象解析器接口，所有解析器应继承本类并实现 parse 方法。
    """

    @abstractmethod
    def parse(self, path: Path, recursive: bool) -> List[FindingResult]:
        """
        扫描结果解析方法，支持输入为文件或目录，返回 FindingResult 结果集。

        Args:
            path (Path): 输入路径，可以是文件或目录
            recursive (bool): 是否递归解析目录下的所有文件

        Returns:
            List[FindingResult]: 标准结构的解析结果列表
        """
        pass
