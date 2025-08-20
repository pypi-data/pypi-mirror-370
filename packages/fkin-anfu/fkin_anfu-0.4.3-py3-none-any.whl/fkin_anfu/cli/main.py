#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# vim: set tabstop=2 shiftwidth=2 textwidth=80 expandtab :
#
#
"""
fkin_anfu cli 主入口

@author: cyhfvg
@date: 2025/05/17
"""
import argparse
import sys

from fkin_anfu import __version__
from fkin_anfu.cli.parse_cmd import register_parse_subcommand
from fkin_anfu.utils.log_utils import debug_print


def main() -> None:
    """
    fkin-anfu CLI 主入口，支持 --help 和 --version 参数。
    """
    parser = argparse.ArgumentParser(
        prog="fkin-anfu",
        description="fkin-anfu - Network Security Automation Toolkit",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}", help="显示当前版本号")

    subparsers = parser.add_subparsers(title="subcommands", dest="command", help="可用子命令")
    # subcommand: parse
    register_parse_subcommand(subparsers)

    # :arg_parser
    args = parser.parse_args()

    if hasattr(args, "func"):
        try:
            args.func(args)
        except Exception as why:
            debug_print("ERROR", f"[main] 子命令执行失败: {why}")
            sys.exit(1)
    else:
        parser.print_help()
