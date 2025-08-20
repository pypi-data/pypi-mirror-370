#!/usr/bin/env python3
"""命令行入口点"""

import sys
from .main import main

def cli():
    """CLI入口点"""
    main()

def cli_with_alias_warning():
    """CLI入口点（带别名提醒）"""
    print("💡 提示: 推荐使用 'dir2prompt' 命令（不带s），功能完全相同")
    print("   建议在shell配置文件中添加别名: alias dir2prompts='dir2prompt'")
    print()
    main()

if __name__ == "__main__":
    cli()