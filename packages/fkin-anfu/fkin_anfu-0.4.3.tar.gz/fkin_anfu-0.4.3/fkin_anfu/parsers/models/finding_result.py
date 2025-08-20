#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# vim: set tabstop=2 shiftwidth=2 textwidth=80 expandtab :
#
#
"""
定义 FindingResult 数据结构，用于统一表示漏洞信息或资产识别结果。
字段涵盖五大类：网络定位、服务信息、识别内容、责任归属、元信息。
此模型适用于解析阶段标准化结构，并可用于后续输出或合并处理。

@author: cyhfvg
@date: 2025/07/10
"""
from typing import Any

from pydantic import BaseModel, Field


class FindingResult(BaseModel):
    # 网络定位字段
    ip: str = Field(default="", description="IP地址或域名")
    port: int = Field(default=0, description="端口号")
    protocol: str = Field(default="", description="协议类型, 如 http、https、tcp")
    url: str = Field(default="", description="完整访问 URL, 如 http://1.1.1.1:8080/path")

    # 服务识别字段
    service: str = Field(default="", description="服务类型, 如 http、ssh")
    product: str = Field(default="", description="服务软件名, 如 nginx、tomcat")
    version: str = Field(default="", description="软件版本信息")
    banner: str = Field(default="", description="指纹特征或响应头信息")

    # 漏洞或资产识别字段
    finding_type: str = Field(default="", description="识别类型:vuln(漏洞)或 asset(资产)")
    name: str = Field(default="", description="漏洞名或资产特征名")
    title: str = Field(default="", description="页面标题或结果摘要")
    severity: str = Field(default="", description="严重等级, 如 high、medium、low、info")
    cve_id: str = Field(default="", description="CVE 编号（如有）")

    # 责任归属字段
    org_unit: str = Field(default="", description="所属单位")
    department: str = Field(default="", description="所属部门")
    business_system: str = Field(default="", description="所属业务系统名称")
    owner: str = Field(default="", description="资产负责人")
    source_origin: str = Field(default="", description="归属来源, 如 资产管理平台、资产表、手动确认等")

    # 元信息字段
    source_tool: str = Field(default="", description="来源工具名，如 afrog、nuclei")
    raw_path: str = Field(default="", description="原始扫描结果文件名")
    extra: dict[str, Any] = Field(default_factory=dict, description="附加字段信息,预留扩展用")
