#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# vim: set tabstop=2 shiftwidth=2 textwidth=80 expandtab :
#
#
"""
Excel 读取/写入/导出列

@author: cyhfvg
@date: 2025/04/23
"""
from collections import OrderedDict
from pathlib import Path
from typing import Dict, List, Optional, Union

import pandas as pd
from pandas import DataFrame

__all__ = ["read_excel", "write_excel", "fill_merged_cells"]


def read_excel(
    file_path: Union[Path, str],
    sheet_name: Optional[Union[str, list[str]]] = None,
    header: Optional[int] = 0,
    usecols: Optional[Union[list[str], list[int]]] = None,
) -> Union[DataFrame, Dict[str, DataFrame]]:
    """
    读取 Excel 文件并返回 DataFrame，支持路径存在性检查，header 行指定和读取指定列。

    :param file_path: Excel 文件路径，可以是 Path 对象或字符串
    :param sheet_name: 要读取的工作表名称，可以是 str（读取单个工作表），list（读取多个工作表），或 None（读取所有工作表）
    :param header: 指定哪一行作为列名（默认为 0，第一行）
    :param usecols: 指定要读取的列，可以是列名列表或列索引列表（默认为 None，读取所有列）
    :return: 包含 Excel 数据的 DataFrame 或字典（如果读取多个工作表）
    :raises FileNotFoundError: 如果文件路径不存在，抛出该异常
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Excel 文件不存在：{file_path.resolve()}")

    # 读取单个或多个工作表
    return pd.read_excel(file_path, sheet_name=sheet_name, header=header, usecols=usecols, index_col=None)


def write_excel(sheets: OrderedDict[str, DataFrame], file_path: Union[Path, str]) -> None:
    """
    将多个 DataFrame 写入 Excel 文件中多个 sheet，支持写入顺序控制。

    :param sheets: 有序字典，键为 sheet 名称，值为对应的 DataFrame（保持插入顺序）
    :param file_path: Excel 文件保存路径（str 或 Path）
    :raises ValueError: 如果 sheets 为空或任意 sheet_name 为空
    """
    if not sheets:
        raise ValueError("必须提供至少一个 sheet 数据")
    if any(not sheet_name for sheet_name in sheets):
        raise ValueError("所有 sheet_name 都必须是非空字符串")

    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(file_path, engine="xlsxwriter") as writer:
        for sheet_name, df in sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)


def fill_merged_cells(df: DataFrame, columns: Union[List[str], List[int]]) -> DataFrame:
    """
    对指定列进行向下填充(合并单元格反向填充)，支持列名或列索引。

    :param df: 原始 DataFrame
    :param columns: 要填充的列列表，可以是列名（str）或列索引（int）
    :return: 填充后的副本 DataFrame
    :raises ValueError: 如果列名/索引无效
    """
    df_copy = df.copy()

    if not columns:
        raise ValueError("必须指定需要填充的列")

    for col in columns:
        if isinstance(col, int):
            try:
                col = df.columns[col]
            except IndexError as why:
                raise ValueError(f"列索引 {col} 越界，当前列数为 {len(df.columns)}") from why
        elif col not in df.columns:
            raise ValueError(f"列名 '{col}' 不存在于 DataFrame 中")

        df_copy[col] = df_copy[col].replace('', pd.NA).ffill()

    return df_copy
