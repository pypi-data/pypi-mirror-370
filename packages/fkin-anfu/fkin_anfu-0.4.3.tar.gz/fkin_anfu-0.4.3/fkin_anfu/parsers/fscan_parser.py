#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# vim: set tabstop=2 shiftwidth=2 textwidth=80 expandtab :
#
#
"""
fscan 扫描结果解析

支持：
- 单个文件解析
- 目录递归解析（仅 .txt 或无扩展名）
- 转换为统一的 FindingResult 列表结构

@author: cyhfvg
@date: 2025/07/17
"""
import re
from pathlib import Path
from typing import List
from urllib.parse import urlparse

from fkin_anfu.parsers.base_parser import BaseParser
from fkin_anfu.parsers.models.finding_result import FindingResult
from fkin_anfu.utils.file_utils import safe_read_lines
from fkin_anfu.utils.log_utils import debug_print

__all__ = ["FscanParser"]


class FscanParser(BaseParser):
    """
    fscan 扫描结果解析器：将 fscan 输出的纯文本结果解析为 FindingResult 结构。
    """

    def parse(self, path: Path, recursive: bool = False) -> List[FindingResult]:
        """
        扫描结果解析方法，支持文件或目录输入

        Args:
            path (Path): 输入路径（文件或目录）
            recursive (bool): 是否递归目录

        Returns:
            List[FindingResult]: 标准结构的解析结果
        """
        results: list[FindingResult] = []

        if path.is_file():
            results.extend(self._parse_file(path))
        elif path.is_dir():
            files = path.rglob("*.txt") if recursive else path.glob("*.txt")
            debug_print("INFO", f"[FscanParser] 发现 {len(files)} 个文件待解析")
            for file in files:
                results.extend(self._parse_file(file))

        debug_print("INFO", f"[AfrogParser] 成功解析 {len(results)} 条记录")

        return results

    def _parse_file(self, path: Path) -> list[FindingResult]:
        """
        解析单个 fscan 扫描结果文件

        Args:
            path (Path): 文件路径

        Returns:
            list[FindingResult]: 提取的结果
        """
        findings: list[FindingResult] = []

        try:
            lines = safe_read_lines(path)
        except Exception as why:
            raise RuntimeError(f"Failed to read file: {path}") from why

        for line in lines:
            line = line.strip()
            if not line:
                continue

            result = self._parse_line(line, raw_path=path.name)
            if result:
                findings.append(result)
        debug_print("INFO", f"[FscanParser] 解析文件 {path.name} {len(lines)}行数据,解析result {len(findings)} 条信息")

        return findings

    def _parse_line(self, line: str, raw_path: str) -> FindingResult | None:
        """
        单行解析逻辑

        Args:
            line (str): 单行文本
            raw_path (str): 来源文件名

        Returns:
            FindingResult | None: 若成功解析则返回结构，否则返回 None
        """

        # 端口开放格式 样例：【192.168.5.1:21 open】 {{{1
        port_open_pattern = re.compile(r"^(\d{1,3}(?:\.\d{1,3}){3}):(\d+)\s+open$", re.IGNORECASE)
        match = port_open_pattern.match(line)
        if match:
            ip = match.group(1)
            port = int(match.group(2))
            return FindingResult(
                ip=ip,
                port=port,
                protocol="tcp",
                finding_type="asset",
                name="端口开放",
                severity="info",
                source_tool="fscan",
                raw_path=raw_path,
            )
        # 1}}}

        # WebTitle行格式 样例 【[*] WebTitle http://192.168.5.2:38910 code:200 len:11212  title:Apache Tomcat/8.5.100】 {{{2
        webtitle_pattern = re.compile(r"^\[\*\] WebTitle (http[s]?://[^\s]+).*?title:\s*(.+)(?:\s|$)", re.IGNORECASE)

        match = webtitle_pattern.match(line)
        if match:
            url = match.group(1).strip()
            title = match.group(2).strip()

            parsed = urlparse(url)
            ip = parsed.hostname or ""
            port = parsed.port or (443 if parsed.scheme == "https" else 80)

            # 提取组件信息
            product = ""
            version = ""

            title_lc = title.lower()

            if "nginx" in title_lc:
                product = "nginx"
                # 可进一步匹配 nginx/1.18.0
                version_match = re.search(r"nginx/?\s*/?\s*([0-9.]+)", title_lc)
                if version_match:
                    version = version_match.group(1).strip()

            elif "tomcat" in title_lc:
                product = "tomcat"
                # 匹配 tomcat/8.5.93 或 Apache Tomcat/8.5.93
                version_match = re.search(r"tomcat/?\s*/?\s*([0-9.]+)", title_lc)
                if version_match:
                    version = version_match.group(1).strip()

            return FindingResult(
                ip=ip,
                port=port,
                protocol=parsed.scheme,
                url=url,
                service="http",
                finding_type="asset",
                name="web服务开放",
                title=title,
                product=product,
                version=version,
                severity="info",
                source_tool="fscan",
                raw_path=raw_path,
            )
        # 2}}}

        # PocScan行记录 示例 [+] PocScan http://192.168.5.3:31445/services
        # poc-yaml-apache-axis-webservice-detect [{path services}] {{{3
        pocscan_pattern = re.compile(r"^\[\+\] PocScan\s+(http[s]?://[^\s]+)\s+([^\s]+)", re.IGNORECASE)

        match = pocscan_pattern.match(line)
        if match:
            url = match.group(1).strip()
            poc_name = match.group(2).strip()

            parsed = urlparse(url)
            ip = parsed.hostname or ""
            port = parsed.port or (443 if parsed.scheme == "https" else 80)

            # 提取 title（去除 poc-yaml- 前缀）
            title = poc_name
            if poc_name.startswith("poc-yaml-"):
                title = poc_name[len("poc-yaml-") :]

            # 判断类型
            finding_type = "asset" if "-detect" in poc_name else "vuln"

            # 严重等级匹配（按优先级）
            name_lc = poc_name.lower()
            if "rce" in name_lc or "bypass" in name_lc or "default-password" in name_lc:
                severity = "high"
            elif "unauth" in name_lc:
                severity = "low"
            elif "leak" in name_lc:
                severity = "info"
            else:
                severity = "info"

            return FindingResult(
                ip=ip,
                port=port,
                protocol=parsed.scheme,
                url=url,
                service="http",
                finding_type=finding_type,
                name=poc_name,
                title=title,
                severity=severity,
                source_tool="fscan",
                raw_path=raw_path,
            )
        # 3}}}

        # InfoScan示例 [+] InfoScan http://192.168.5.4:29514/docs [Swagger UI] {{{4
        infoscan_pattern = re.compile(r"^\[\+\] InfoScan\s+(http[s]?://[^\s]+)\s+\[([^\]]+)\]", re.IGNORECASE)

        match = infoscan_pattern.match(line)
        if match:
            url = match.group(1).strip()
            title = match.group(2).strip()

            parsed = urlparse(url)
            ip = parsed.hostname or ""
            port = parsed.port or (443 if parsed.scheme == "https" else 80)

            return FindingResult(
                ip=ip,
                port=port,
                protocol=parsed.scheme,
                url=url,
                service="http",
                finding_type="asset",
                name=f"资产识别{title}",
                title=title,
                severity="info",
                source_tool="fscan",
                raw_path=raw_path,
            )
        # 4}}}

        #  密码爆破分支 示例 {{{5
        # 匹配类型 A：未授权访问
        # 未授权利用 示例【[+] Memcached 192.168.5.5:11211 unauthorized】
        unauth_pattern = re.compile(r"^\[\+\]\s+(\w+)\s+(\d{1,3}(?:\.\d{1,3}){3}):(\d+)\s+unauthorized", re.IGNORECASE)

        match = unauth_pattern.match(line)
        if match:
            service_raw = match.group(1).strip()
            ip = match.group(2)
            port = int(match.group(3))
            service = service_raw.lower()
            return FindingResult(
                ip=ip,
                port=port,
                protocol="tcp",
                url=f"{ip}:{port}",
                service=service,
                finding_type="vuln",
                name=f"{service_raw} unauthorized",
                title=service,
                severity="high",
                source_tool="fscan",
                raw_path=raw_path,
            )

        # 匹配类型 B：爆破成功记录
        # 【[+] ftp 192.168.5.5:21 admin 123456】
        brute_success_pattern = re.compile(
            r"^\[\+\]\s+(\w+)\s+(\d{1,3}(?:\.\d{1,3}){3}):(\d+)\s+(\S+)\s+(\S+)", re.IGNORECASE
        )

        match = brute_success_pattern.match(line)
        if match:
            service_raw = match.group(1).strip()
            ip = match.group(2)
            port = int(match.group(3))
            username = match.group(4)
            password = match.group(5)

            service = service_raw.lower()
            return FindingResult(
                ip=ip,
                port=port,
                protocol="tcp",
                url=f"{ip}:{port}",
                service=service,
                finding_type="vuln",
                name=f"{service}口令 {username} / {password}",
                title=service,
                severity="high",
                source_tool="fscan",
                raw_path=raw_path,
            )

        # 5}}}
        return None
