#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# vim: set ts=2 sw=2 et:
"""
MySQL 数据库工具函数，基于 SQLAlchemy 实现连接管理、测试、表结构操作等。

@module: db_utils
@author: cyhfvg
@date: 2025/04/24
"""

from typing import Any, Callable, Dict, Optional

from pandas import DataFrame
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.pool import QueuePool
from sqlalchemy.sql import table as sql_table

from fkin_anfu.utils.log_utils import debug_print

__all__ = [
    "get_mysql_engine",
    "check_mysql_connection",
    "truncate_table",
    "is_table_exists",
    "safe_scalar",
    "write_df_to_mysql",
]


def get_mysql_engine(mysql_env: Dict[str, str]) -> Engine:
    """
    构造 SQLAlchemy MySQL 引擎(使用连接池 QueuePool)

    :param mysql_env: 包含连接配置的字典，键包括：
                      - user, password, host, port, db
    :return: SQLAlchemy Engine 对象
    :raises ValueError: 如果缺少必须的字段
    """
    required_keys = ["user", "password", "host", "port", "db"]
    for key in required_keys:
        if key not in mysql_env or not mysql_env[key]:
            raise ValueError(f"数据库配置缺失字段：{key}")

    url = (
        f"mysql+pymysql://{mysql_env['user']}:{mysql_env['password']}"
        f"@{mysql_env['host']}:{mysql_env['port']}/{mysql_env['db']}?charset=utf8mb4"
    )

    debug_print("info", f"构造数据库连接：{url.replace(mysql_env['password'], '******')}")
    return create_engine(
        url,
        poolclass=QueuePool,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=False,
    )


def check_mysql_connection(engine: Engine) -> bool:
    """
    测试数据库连接是否成功(执行 SELECT 1)

    :param engine: SQLAlchemy Engine 实例
    :return: True 表示连接正常,False 表示异常
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except OperationalError as why:
        debug_print("error", f"数据库连接失败(OperationalError):{why}")
    except SQLAlchemyError as why:
        debug_print("error", f"数据库连接失败(SQLAlchemyError):{why}")
    return False


def truncate_table(table_name: str, engine: Engine) -> None:
    """
    清空数据库表中的所有数据(TRUNCATE 操作)

    :param table_name: 要清空的表名
    :param engine: SQLAlchemy Engine 实例
    :raises Exception: 执行失败时抛出异常
    """
    if not is_table_exists(table_name, engine):
        debug_print("warning", f"目标表不存在:{table_name}")
        return

    try:
        debug_print("info", f"准备清空表:{table_name}")
        with engine.begin() as conn:
            tbl = sql_table(table_name)
            conn.execute(text(f"TRUNCATE TABLE `{tbl.name}`"))
    except SQLAlchemyError as why:
        debug_print("error", f"清空表失败 `{table_name}`: {why}")
        raise


def is_table_exists(table_name: str, engine: Engine) -> bool:
    """
    判断数据库中是否存在指定表名(当前数据库)

    :param table_name: 表名
    :param engine: SQLAlchemy Engine 实例
    :return: 存在返回 True,不存在返回 False
    """
    sql = text(
        "SELECT COUNT(*) FROM information_schema.tables " + "WHERE table_schema = DATABASE() AND table_name = :name"
    )
    try:
        with engine.connect() as conn:
            result = conn.execute(sql, {"name": table_name})
            count = safe_scalar(result, default=0, convert=int)
            return count > 0
    except SQLAlchemyError as why:
        debug_print("error", f"检查表是否存在失败 `{table_name}`: {why}")
        raise


def safe_scalar(result: Any, default: Optional[Any] = 0, convert: Optional[Callable[[Any], Any]] = None) -> Any:
    """
    安全提取 SQLAlchemy 查询结果的 scalar 值,None 时返回默认值。

    :param result: SQLAlchemy 查询返回的 Result 对象
    :param default: scalar() 为 None 时使用的默认值(默认 0)
    :param convert: 类型转换函数，如 int/float/str 等
    :return: 提取后的值
    """
    try:
        value = result.scalar()
        if value is None:
            return default
        return convert(value) if convert else value
    except Exception as why:
        raise RuntimeError(f"safe_scalar 提取失败: {why}") from why


def write_df_to_mysql(df: DataFrame, table_name: str, engine: Engine, overwrite: bool = True) -> None:
    """
    将 DataFrame 写入 MySQL 表,支持是否先清空表再写入(overwrite)

    :param df: 要写入的 DataFrame
    :param table_name: 目标表名
    :param engine: SQLAlchemy 引擎实例
    :param overwrite: 是否先清空表(默认为 True)
    :raises SQLAlchemyError: 若表不存在或写入失败
    """
    if not is_table_exists(table_name, engine):
        msg = f"目标表不存在: {table_name}"
        debug_print("error", msg)
        raise SQLAlchemyError(msg)

    try:
        tbl = sql_table(table_name)

        with engine.begin() as conn:
            if overwrite:
                debug_print("info", f"正在清空表 `{tbl.name}` ...")
                conn.execute(text(f"DELETE FROM `{tbl.name}`"))

            debug_print("info", f"正在写入 {len(df)} 条记录到 `{tbl.name}`(覆盖模式: {overwrite})...")
            df.to_sql(name=tbl.name, con=conn, if_exists="append", index=False)

        debug_print("success", f"数据已写入 `{tbl.name}`，记录数: {len(df)}")

    except SQLAlchemyError as why:
        debug_print("error", f"MySQL 写入失败:{why}")
        raise


def execute_one_sql(engine: Engine, one_sql: str) -> None:
    """
    执行提供的单条 SQL 语句，使用 SQLAlchemy engine。

    :param engine: SQLAlchemy Engine 对象
    :param one_sql: 要执行的 SQL 语句（应为完整语句）
    :raises RuntimeError: 执行失败时抛出异常
    """
    try:
        with engine.begin() as conn:  # 自动 commit 或 rollback
            conn.execute(text(one_sql))
        debug_print("INFO", f"[execute_one_sql] 成功执行 SQL: {one_sql.strip()}")
    except SQLAlchemyError as why:
        debug_print("ERROR", f"[execute_one_sql] SQL 执行失败: {one_sql.strip()} | {why}")
        raise RuntimeError(f"执行 SQL 失败: {one_sql.strip()}") from why
