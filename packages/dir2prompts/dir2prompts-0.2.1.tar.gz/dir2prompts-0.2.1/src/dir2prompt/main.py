#!/usr/bin/env python3
"""
dir2prompt - 目录树生成工具
用法: dir2prompt <目录路径> [选项]

选项:
  --ex <路径>     排除指定路径（可多次使用）
  --in <路径>     仅包含指定路径（可多次使用）
  -o <文件>       输出到指定文件
  -h, --help     显示帮助信息
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Set
from .clipboard import copy_to_clipboard, get_clipboard_info


class DirectoryTreeGenerator:
    def __init__(self, root_path: str, exclude_paths: List[str] = None, include_paths: List[str] = None):
        """
        初始化目录树生成器
        
        Args:
            root_path: 根目录路径
            exclude_paths: 要排除的路径列表
            include_paths: 要包含的路径列表
        """
        self.root_path = Path(root_path).resolve()
        self.exclude_paths = set()
        self.include_paths = set()
        
        # 处理排除路径
        if exclude_paths:
            for path in exclude_paths:
                abs_path = Path(path).resolve()
                self.exclude_paths.add(abs_path)
        
        # 处理包含路径
        if include_paths:
            for path in include_paths:
                abs_path = Path(path).resolve()
                self.include_paths.add(abs_path)
    
    def should_include_path(self, path: Path) -> bool:
        """
        判断路径是否应该被包含
        
        Args:
            path: 要检查的路径
            
        Returns:
            bool: True if 路径应该被包含
        """
        abs_path = path.resolve()
        
        # 检查是否在排除列表中
        for exclude_path in self.exclude_paths:
            try:
                abs_path.relative_to(exclude_path)
                return False  # 路径在排除目录中
            except ValueError:
                continue
        
        # 如果有包含列表，检查是否在包含列表中
        if self.include_paths:
            for include_path in self.include_paths:
                try:
                    abs_path.relative_to(include_path)
                    return True  # 路径在包含目录中
                except ValueError:
                    continue
                try:
                    include_path.relative_to(abs_path)
                    return True  # 包含目录在当前路径中
                except ValueError:
                    continue
            return False  # 有包含列表但路径不在其中
        
        return True  # 默认包含
    
    def get_directory_tree(self, path: Path = None, prefix: str = "", is_last: bool = True) -> str:
        """
        递归生成目录树字符串
        
        Args:
            path: 当前路径（默认为根路径）
            prefix: 当前行的前缀
            is_last: 是否为同级最后一个项目
            
        Returns:
            str: 目录树字符串
        """
        if path is None:
            path = self.root_path
        
        if not self.should_include_path(path):
            return ""
        
        tree_str = ""
        
        # 添加当前目录/文件
        if path == self.root_path:
            tree_str += f"{path.name}/\n"
            current_prefix = ""
        else:
            connector = "└── " if is_last else "├── "
            name = f"{path.name}/" if path.is_dir() else path.name
            tree_str += f"{prefix}{connector}{name}\n"
            current_prefix = prefix + ("    " if is_last else "│   ")
        
        # 如果是目录，递归处理子项目
        if path.is_dir():
            try:
                # 获取所有子项目并排序
                children = []
                for child in path.iterdir():
                    if self.should_include_path(child):
                        children.append(child)
                
                # 按名称排序，目录在前
                children.sort(key=lambda x: (not x.is_dir(), x.name.lower()))
                
                # 递归处理每个子项目
                for i, child in enumerate(children):
                    is_last_child = (i == len(children) - 1)
                    tree_str += self.get_directory_tree(child, current_prefix, is_last_child)
                    
            except PermissionError:
                tree_str += f"{current_prefix}├── [权限被拒绝]\n"
            except OSError as e:
                tree_str += f"{current_prefix}├── [错误: {e}]\n"
        
        return tree_str
    
    def generate_tree(self) -> str:
        """
        生成完整的目录树
        
        Returns:
            str: 完整的目录树字符串
        """
        if not self.root_path.exists():
            return f"错误: 路径 '{self.root_path}' 不存在"
        
        if not self.root_path.is_dir():
            return f"错误: '{self.root_path}' 不是一个目录"
        
        return self.get_directory_tree()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="生成目录树结构",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  dir2prompt /path/to/project          # 默认同时显示和复制到剪切板
  dir2prompt . --ex node_modules --ex .git
  dir2prompt /project --in src --in docs
  dir2prompt /project --ex __pycache__ --in src --in tests
  dir2prompt . -o tree.txt             # 输出到文件（同时复制到剪切板）
  dir2prompt . --no-clipboard          # 仅显示，不复制到剪切板
  dir2prompt . --clipboard-method osc52  # 指定剪切板方法
  dir2prompt . --clipboard-info        # 查看剪切板环境信息
        """
    )
    
    parser.add_argument("path", help="要扫描的目录路径")
    parser.add_argument("--ex", "--exclude", action="append", dest="exclude_paths", 
                       help="排除的路径（可多次使用）")
    parser.add_argument("--in", "--include", action="append", dest="include_paths",
                       help="包含的路径（可多次使用）")
    parser.add_argument("-o", "--output", dest="output_file",
                       help="输出到指定文件")
    parser.add_argument("--no-clipboard", action="store_true",
                       help="禁用剪切板功能，仅在终端显示")
    parser.add_argument("--clipboard-info", action="store_true",
                       help="显示剪切板环境信息")
    parser.add_argument("--clipboard-method", choices=["auto", "osc52", "pyperclip"],
                       default="auto", help="指定剪切板复制方法（默认: auto）")
    
    # 如果没有参数，显示帮助
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    try:
        args = parser.parse_args()
    except SystemExit:
        return
    
    # 处理剪切板环境信息查询
    if args.clipboard_info:
        info = get_clipboard_info()
        print("🔍 剪切板环境信息:")
        print(f"  SSH会话: {'是' if info['is_ssh_session'] else '否'}")
        print(f"  终端支持OSC52: {'是' if info['is_terminal_supports_osc52'] else '否'}")
        print(f"  终端类型: {info['term'] or '未知'}")
        print(f"  终端程序: {info['term_program'] or '未知'}")
        print(f"  TTY支持: {'是' if info['is_tty'] else '否'}")
        if info['ssh_connection']:
            print(f"  SSH连接: {info['ssh_connection']}")
        return
    
    # 创建目录树生成器
    generator = DirectoryTreeGenerator(
        root_path=args.path,
        exclude_paths=args.exclude_paths,
        include_paths=args.include_paths
    )
    
    # 生成目录树
    tree = generator.generate_tree()
    
    # 默认尝试复制到剪切板（除非用户明确禁用）
    clipboard_success = False
    if not args.no_clipboard:
        # 确定使用的方法
        method = None if args.clipboard_method == "auto" else args.clipboard_method
        clipboard_success, method_desc = copy_to_clipboard(tree, force_method=method)
        
        if clipboard_success:
            print(f"📋 已复制到剪切板 (使用: {method_desc})")
        else:
            # 静默失败，不打扰用户体验
            pass
    
    # 输出到文件
    if args.output_file:
        try:
            with open(args.output_file, 'w', encoding='utf-8') as f:
                f.write(tree)
            print(f"📁 目录树已保存到: {args.output_file}")
        except Exception as e:
            print(f"❌ 写入文件失败: {e}")
            return
    
    # 总是在终端显示内容
    print(tree)
    
    # 如果剪切板失败且用户没有禁用，给出提示
    if not args.no_clipboard and not clipboard_success:
        print(f"\n💡 提示: 剪切板复制失败 ({method_desc})，可使用 --clipboard-info 查看环境信息")


if __name__ == "__main__":
    main()