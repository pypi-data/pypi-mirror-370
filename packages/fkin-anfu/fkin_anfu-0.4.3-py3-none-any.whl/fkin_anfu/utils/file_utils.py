#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# vim: set tabstop=2 shiftwidth=2 textwidth=80 expandtab :
#
#
"""
>读取文件内容：读取文本文件、二进制文件。
>写入文件：将数据写入文件（比如 JSON 写入、CSV 写入等）。
>文件复制、删除、移动：文件管理操作。
>文件内容处理：如文本文件按行读取或按特定方式解析。

@author: cyhfvg
@date: 2025/04/22
"""
import shutil
from pathlib import Path
from typing import List, Union

__all__ = ['is_file_exists', 'read_file', 'write_file', 'append_to_file', 'copy_file', 'delete_file']


def is_file_exists(file_path: Union[Path, str]) -> bool:
    """
    检查文件是否存在。

    :param file_path: 文件路径，可以是 Path 对象或字符串
    :return: 如果文件存在返回 True，否则返回 False
    """
    return Path(file_path).exists()


def read_file(file_path: Union[Path, str]) -> List[str]:
    """
    读取文件内容并返回一个列表，每行是列表的一个元素。

    :param file_path: 文件路径，可以是 Path 对象或字符串
    :return: 文件内容，每行作为一个元素的列表
    :raises FileNotFoundError: 如果文件不存在
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"文件 {path} 不存在")
    with path.open('r', encoding='utf-8') as file:
        return file.readlines()


def safe_read_lines(path: Path) -> list[str]:
    """
    安全读取文本文件为行列表,自动处理编码(UTF-8优先,失败回退GBK)

    Args:
        path (Path): 文件路径

    Returns:
        list[str]: 按行拆分的字符串列表
    """
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return path.read_text(encoding="gbk", errors="ignore").splitlines()


def write_file(file_path: Union[Path, str], content: List[str]) -> None:
    """
    将内容写入文件，每个列表元素作为文件中的一行。如果父目录不存在，则创建它。

    :param file_path: 文件路径，可以是 Path 对象或字符串
    :param content: 文件内容，每个元素代表文件中的一行
    :return: 无返回值
    """
    path = Path(file_path)

    # 确保父目录存在，如果不存在则创建
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open('w', encoding='utf-8') as file:
        file.writelines([line + '\n' for line in content])


def append_to_file(file_path: Union[Path, str], content: List[str]) -> None:
    """
    将内容追加到文件末尾，每个列表元素作为文件中的一行。如果文件不存在，则创建文件。

    :param file_path: 文件路径，可以是 Path 对象或字符串
    :param content: 要追加的内容，每个元素代表文件中的一行
    :return: 无返回值
    """
    path = Path(file_path)

    # 确保父目录存在，如果不存在则创建
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open('a', encoding='utf-8') as file:
        file.writelines([line + '\n' for line in content])


def copy_file(src: Union[Path, str], dest: Union[Path, str]) -> None:
    """
    复制文件，如果源文件不存在则抛出 FileNotFoundError。如果目标目录不存在，则创建目标目录。

    :param src: 源文件路径，可以是 Path 对象或字符串
    :param dest: 目标文件路径，可以是 Path 对象或字符串
    :return: 无返回值
    :raises FileNotFoundError: 如果源文件不存在
    """
    src_path = Path(src)
    dest_path = Path(dest)

    # 检查源文件是否存在
    if not src_path.exists():
        raise FileNotFoundError(f"源文件 {src_path} 不存在")

    # 确保目标文件的父目录存在，如果不存在则创建
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    # 复制文件
    shutil.copy(src_path, dest_path)


def delete_file(file_path: Union[Path, str]) -> None:
    """
    删除文件或目录。如果文件或目录不存在，则不做任何操作。

    :param file_path: 要删除的文件或目录路径，可以是 Path 对象或字符串
    :return: 无返回值
    """
    path = Path(file_path)

    if not path.exists():
        return

    if path.is_file():
        path.unlink()

    elif path.is_dir():
        shutil.rmtree(path)
