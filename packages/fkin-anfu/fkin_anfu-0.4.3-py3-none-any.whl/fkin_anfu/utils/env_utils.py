#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# vim: set tabstop=2 shiftwidth=2 textwidth=100 expandtab :
#
"""
.env 环境变量加载与访问封装工具
用于安全管理配置，例如数据库、API密钥、运行模式等

@author: cyhfvg
@date: 2025/04/23
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import load_dotenv

__all__ = ["get_env_str", "get_env_int", "get_env_bool", "get_env_groups_structured"]

# 默认加载项目根目录下 .env 文件
load_dotenv(dotenv_path=Path(".env"), override=False)


def get_env_str(key: str, default: Optional[str] = None, strict: bool = False) -> str:
    """
    获取字符串类型的环境变量

    :param key: 环境变量名
    :param default: 可选默认值
    :param strict: 如果为 True 且未设置值，则抛出异常
    :return: 字符串值
    """
    value = os.getenv(key)
    if value is not None:
        return value
    if default is not None:
        return default
    if strict:
        raise EnvironmentError(f"环境变量 `{key}` 未设置，且未提供默认值")
    return ""


def get_env_int(key: str, default: Optional[int] = None, strict: bool = False) -> int:
    """
    获取整数类型的环境变量

    :param key: 环境变量名
    :param default: 可选默认值
    :param strict: 如果为 True 且未设置值，则抛出异常
    :return: 整数值
    """
    raw = os.getenv(key)
    if raw is not None:
        try:
            return int(raw)
        except ValueError as why:
            raise ValueError(f"环境变量 `{key}` 的值无法转换为 int:{raw}") from why
    if default is not None:
        return default
    if strict:
        raise EnvironmentError(f"环境变量 `{key}` 未设置，且未提供默认值")
    return 0


def get_env_bool(key: str, default: Optional[bool] = None, strict: bool = False) -> bool:
    """
    获取布尔类型的环境变量（支持 1/0, true/false, yes/no , on/off）

    :param key: 环境变量名
    :param default: 可选默认值
    :param strict: 如果为 True 且未设置值，则抛出异常
    :return: 布尔值
    """
    raw = os.getenv(key)
    if raw is not None:
        return raw.strip().lower() in {"1", "true", "yes", "on"}
    if default is not None:
        return default
    if strict:
        raise EnvironmentError(f"环境变量 `{key}` 未设置，且未提供默认值")
    return False


def get_env_groups_structured(prefix: str, keys: List[str]) -> List[Dict[str, str]]:
    """
    自动识别并提取 .env 中符合 <prefix>_<idx>_<key> 格式的多组配置项。

    支持键名中包含小写、大写、数字、下划线和中划线。

    示例：
        MYSQL_1_HOST=127.0.0.1
        MYSQL_1_PORT=3306
        MYSQL_2_HOST=192.168.1.2

        get_env_groups_structured("MYSQL", ["HOST", "PORT"]) =>
        [
            {"host": "127.0.0.1", "port": "3306"},
            {"host": "192.168.1.2", "port": "3306"},
        ]

    :param prefix: 组前缀（如 "MYSQL"）
    :param keys: 每组所需字段名称列表（如 ["HOST", "PORT"]）
    :return: 每组配置组成的列表，按 <idx> 从小到大排序
    :raises EnvironmentError: 如果某一组缺少所需字段
    """
    pattern = re.compile(rf"^{re.escape(prefix)}_(\d+)_([-A-Za-z0-9_]+)$")
    groups: Dict[int, Dict[str, str]] = {}

    for env_key, value in os.environ.items():
        match = pattern.match(env_key)
        if match:
            idx = int(match.group(1))
            key_name = match.group(2)
            if idx not in groups:
                groups[idx] = {}
            groups[idx][key_name] = value

    result: List[Dict[str, str]] = []

    for idx in sorted(groups):
        group = groups[idx]
        missing = [k for k in keys if k not in group]
        if missing:
            raise EnvironmentError(f"环境变量组 `{prefix}_{idx}_` 缺少字段: {missing}")
        result.append({k.lower(): group[k] for k in keys})

    return result
