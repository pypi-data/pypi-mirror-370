#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# vim: set tabstop=2 shiftwidth=2 textwidth=80 expandtab :
#
#
"""
路径拼接：将多个路径合并为一个完整路径(注意使用 Path 对象)。
路径检查：检查路径是否存在、是否是文件、是否是目录等。
获取路径的父目录：获取文件或目录的父路径。
扩展名提取与替换：获取文件的扩展名，或替换扩展名。


@author: cyhfvg
@date: 2025/04/22
"""
from pathlib import Path
from typing import Optional, Union

__all__ = [
    'is_file',
    'is_dir',
    'is_path_exists',
    'get_file_extension',
    'get_parent_directory',
    'create_directory',
    'join_paths',
]


def is_file(path: Union[Path, str]) -> bool:
    """
    判断给定路径是否为文件。

    :param path: 要检查的路径字符串
    :return: 如果路径是文件，返回 True；否则返回 False
    """
    return Path(path).is_file()


def is_dir(path: Union[Path, str]) -> bool:
    """
    判断给定路径是否为目录。

    :param path: 要检查的路径，可以是 Path 对象或字符串
    :return: 如果路径是目录，返回 True；否则返回 False
    """
    path = Path(path)
    return path.is_dir()


def is_path_exists(path: Union[Path, str]) -> bool:
    """
    检查给定路径是否存在。

    :param path: 要检查的路径字符串
    :return: 如果路径存在，返回 True；否则返回 False
    """
    return Path(path).exists()


def get_file_extension(file_path: Union[Path, str]) -> str:
    """
    获取文件的扩展名。

    :param file_path: 文件路径字符串
    :return: 文件扩展名字符串，包括点（例如：'.txt'）
    """
    return Path(file_path).suffix


def get_parent_directory(file_path: Union[Path, str]) -> Optional[Path]:
    """
    获取文件或目录的父目录路径。

    :param file_path: 文件或目录的路径字符串
    :return: 父目录的路径，返回一个 Path 对象，如果路径无父目录，则返回 './'
    """
    parent = Path(file_path).parent
    return parent if parent != Path(file_path) else Path('./')


def create_directory(path: Union[Path, str]) -> None:
    """
    创建目录，如果目录不存在则创建。

    :param path: 要创建的目录路径，可以是 Path 对象或字符串
    :return: 无返回值
    :raises: FileExistsError 如果目录已存在
    """
    path = Path(path)  # 确保路径是 Path 对象
    try:
        path.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        raise FileExistsError(f"目录 {path} 已存在")


def join_paths(*paths: str) -> Path:
    """
    拼接多个路径，返回一个完整的 Path 对象。

    :param paths: 需要拼接的路径部分，可以是多个路径片段
    :return: 拼接后的完整路径，返回一个 Path 对象
    """
    return Path(*paths)
