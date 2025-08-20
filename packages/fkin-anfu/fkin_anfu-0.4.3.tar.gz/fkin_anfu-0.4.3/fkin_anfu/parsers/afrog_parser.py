#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# vim: set tabstop=2 shiftwidth=2 textwidth=80 expandtab :
#
#
"""
Afrog 扫描工具解析器：
用于将 Afrog 输出的 JSON 格式文件（单个或目录）解析为 FindingResult 结构。
支持递归扫描目录，提取漏洞或资产识别结果。

@author: cyhfvg
@date: 2025/07/11
"""

import json
from pathlib import Path
from typing import List, Union
from urllib.parse import urlparse

from fkin_anfu.common.constants import PRODUCT_MAPPING
from fkin_anfu.common.enums import ParseType
from fkin_anfu.parsers.base_parser import BaseParser
from fkin_anfu.parsers.models.finding_result import FindingResult
from fkin_anfu.utils.log_utils import debug_print

__all__ = ["AfrogParser"]


class AfrogParser(BaseParser):
    """
    Afrog 扫描结果解析器，支持单文件或目录批量解析。
    """

    def parse(self, path: Path, recursive: bool) -> List[FindingResult]:
        """
        解析 Afrog JSON 结果，支持文件或目录。

        Args:
            path (Path): 文件或目录路径
            recursive (bool): 是否递归目录下的所有文件

        Returns:
            List[FindingResult]: 统一结构的解析结果列表

        Raises:
            ValueError: 当文件格式不符合 Afrog JSON 要求时抛出
        """
        files: List[Path] = []

        if path.is_file():
            files = [path]
        elif path.is_dir():
            pattern = "**/*.json" if recursive else "*.json"
            files = list(path.glob(pattern))
        else:
            raise ValueError(f"[AfrogParser] 路径无效: {path}")

        debug_print("INFO", f"[AfrogParser] 发现 {len(files)} 个文件待解析")

        results: List[FindingResult] = []

        results = self.read_vuln_list_from_json_file_list(files)

        debug_print("INFO", f"[AfrogParser] 成功解析 {len(results)} 条记录")
        return results

    def _extract_host_port(self, fulltarget: str) -> tuple[str, int]:
        """
        提取 host 和 port,支持裸 IP:port 与 URL 格式。
        如果 URL 中未指定端口，根据 scheme 推断默认端口。
        """
        if not isinstance(fulltarget, str):
            return "", 0

        # 裸形式如 1.2.3.4:3306
        if "://" not in fulltarget and fulltarget.count(":") == 1:
            host, port = fulltarget.split(":")
            return host.strip(), int(port.strip())

        try:
            parsed = urlparse(fulltarget)
            host = parsed.hostname or ""
            port = parsed.port
            if not port:
                if parsed.scheme == "http":
                    port = 80
                elif parsed.scheme == "https":
                    port = 443
            return host, port if port else 0
        except Exception as why:
            debug_print("WARNING", "[extract_host_port] failed to parse: " + f"{fulltarget}, reason: {why}")
            return "", 0

    def _parse_json_file(self, json_file: Union[Path, str]) -> list[FindingResult]:
        """
        从指定的 JSON 文件中读取漏洞列表数据，返回包含字典的列表。

        :param json_file: JSON 文件路径(Path 或 str)
        :return: 漏洞信息对象列表
        :raises ValueError: 若 JSON 格式非法或内容不是列表
        :raises FileNotFoundError: 若文件不存在
        """
        json_path = Path(json_file)

        try:
            with json_path.open("r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError as why:
                    debug_print(
                        "ERROR",
                        f"[AfrogParser] JSON 加载失败: {json_path} - {why}",
                    )
                    debug_print(
                        "WARNING",
                        f"[AfrogParser] JSON 加载失败，尝试修复文件格式错误，尝试在尾部添加【]】: {json_path}",
                    )
                    f.seek(0)
                    raw = f.read()
                    # 由于上游afrog工具输出问题，其输出的json文件时常文件末尾缺少【]】,尝试修复手动闭合
                    if not raw.strip().endswith("]"):
                        raw = raw.strip() + "]"
                    try:
                        data = json.loads(raw)
                        debug_print("DEBUG", f"[AfrogParser] JSON文件格式修复成功: {json_path}")
                    except Exception as err:
                        raise ValueError(f"[AfrogParser] 修复 JSON 文件失败: {json_path} - {err}")

                if not isinstance(data, list):
                    debug_print(
                        "ERROR", "[_parse_json_file] Expected list at top level," + f"got: {type(data).__name__}"
                    )
                    raise ValueError("Expected JSON array," + f" got {type(data).__name__} in file: {json_path}")

                result_list = []
                for vuln in data:
                    url = vuln.get('fulltarget', '')
                    ip, port = self._extract_host_port(url)
                    pocinfo = vuln.get('pocinfo', {})
                    name = pocinfo.get('infoname', '')
                    severity = pocinfo.get('infoseg', '')

                    # TODO: finding_type: vuln , asset 需要更准确划分
                    finding_type = ParseType.VULN.value
                    if str.lower(severity) == 'info':
                        finding_type = ParseType.ASSET.value
                    else:
                        finding_type = ParseType.VULN.value

                    protocol = 'http'
                    service = 'http'
                    product = ''

                    lower_name = name.lower()
                    for keyword, prod in PRODUCT_MAPPING.items():
                        if keyword in lower_name:
                            product = prod
                            break

                    res = FindingResult(
                        ip=ip,
                        port=port,
                        protocol=protocol,
                        url=url,
                        service=service,
                        product=product,
                        version="",
                        banner="",
                        finding_type=finding_type,
                        name=name,
                        title="",
                        severity=severity,
                        cve_id="",
                        org_unit="",
                        department="",
                        business_system="",
                        owner="",
                        source_origin="",
                        source_tool="afrog",
                        raw_path=json_path.name,
                        extra={},
                    )
                    result_list.append(res)
        except FileNotFoundError as why:
            debug_print("ERROR", "[_parse_json_file] File not found: " + f"{json_path} - {why}")
            raise

        debug_print(
            "DEBUG",
            "[_parse_json_file] read json data list item num: " + f" {len(data)} records from: " + f"{json_path}",
        )
        debug_print(
            "INFO",
            "[_parse_json_file] "
            + f"{len(result_list)} parsed from {len(data)} raw records "
            + f"in file: {json_path}",
        )
        return result_list

    def read_vuln_list_from_json_file_list(self, json_file_list: list[Union[Path, str]]) -> list[FindingResult]:
        """
        按文件列表处理json_file, 读取每个json_file

        :param json_file_list: json_file路径列表,允许空列表
        :return: 读取的包含所有对象的列表
        """
        l_result = []
        for f in json_file_list:
            l_result.extend(self._parse_json_file(f))
        return l_result
