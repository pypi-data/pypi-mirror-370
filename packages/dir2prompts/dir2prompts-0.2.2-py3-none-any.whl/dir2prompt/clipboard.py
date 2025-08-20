#!/usr/bin/env python3
"""
剪切板工具模块
支持本地环境和SSH环境的剪切板操作
"""

import os
import sys
import base64
from typing import Optional


def is_ssh_session() -> bool:
    """
    检测是否在SSH会话中
    
    Returns:
        bool: True if 在SSH会话中
    """
    return bool(os.environ.get('SSH_CLIENT') or os.environ.get('SSH_TTY') or os.environ.get('SSH_CONNECTION'))


def is_terminal_supports_osc52() -> bool:
    """
    检测终端是否支持OSC 52转义序列
    
    Returns:
        bool: True if 终端支持OSC 52
    """
    term = os.environ.get('TERM', '').lower()
    term_program = os.environ.get('TERM_PROGRAM', '').lower()
    
    # 已知支持OSC 52的终端
    supported_terms = [
        'xterm', 'screen', 'tmux', 'alacritty', 'kitty', 'wezterm',
        'iterm', 'hyper', 'vscode', 'gnome-terminal'
    ]
    
    # 检查TERM环境变量
    for supported in supported_terms:
        if supported in term:
            return True
    
    # 检查TERM_PROGRAM环境变量
    for supported in supported_terms:
        if supported in term_program:
            return True
    
    # 如果在SSH会话中且有TTY，假设支持
    return is_ssh_session() and sys.stdout.isatty()


def copy_to_clipboard_osc52(text: str) -> bool:
    """
    使用OSC 52转义序列复制到剪切板（适用于SSH环境）
    
    Args:
        text: 要复制的文本
        
    Returns:
        bool: True if 复制成功
    """
    try:
        # 将文本编码为base64
        encoded = base64.b64encode(text.encode('utf-8')).decode('ascii')
        
        # 构造OSC 52转义序列
        # \033]52;c;<base64_data>\007
        osc52_sequence = f"\033]52;c;{encoded}\007"
        
        # 直接写入stdout
        sys.stdout.write(osc52_sequence)
        sys.stdout.flush()
        
        return True
    except Exception:
        return False


def copy_to_clipboard_pyperclip(text: str) -> bool:
    """
    使用pyperclip复制到剪切板（适用于本地环境）
    
    Args:
        text: 要复制的文本
        
    Returns:
        bool: True if 复制成功
    """
    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except ImportError:
        return False
    except Exception:
        return False


def copy_to_clipboard(text: str, force_method: Optional[str] = None) -> tuple[bool, str]:
    """
    智能选择方法复制到剪切板
    
    Args:
        text: 要复制的文本
        force_method: 强制使用的方法 ("osc52" 或 "pyperclip")
        
    Returns:
        tuple: (成功状态, 使用的方法描述)
    """
    if not text:
        return False, "空文本"
    
    # 强制使用指定方法
    if force_method == "osc52":
        success = copy_to_clipboard_osc52(text)
        return success, "OSC 52转义序列"
    elif force_method == "pyperclip":
        success = copy_to_clipboard_pyperclip(text)
        return success, "pyperclip库"
    
    # 自动选择方法
    if is_ssh_session():
        # SSH环境，优先使用OSC 52
        if is_terminal_supports_osc52():
            success = copy_to_clipboard_osc52(text)
            if success:
                return True, "OSC 52转义序列 (SSH环境)"
        
        # OSC 52失败，尝试pyperclip
        success = copy_to_clipboard_pyperclip(text)
        if success:
            return True, "pyperclip库 (SSH环境备用)"
        
        return False, "SSH环境下剪切板操作失败"
    else:
        # 本地环境，优先使用pyperclip
        success = copy_to_clipboard_pyperclip(text)
        if success:
            return True, "pyperclip库 (本地环境)"
        
        # pyperclip失败，尝试OSC 52
        if is_terminal_supports_osc52():
            success = copy_to_clipboard_osc52(text)
            if success:
                return True, "OSC 52转义序列 (本地环境备用)"
        
        return False, "本地环境下剪切板操作失败"


def get_clipboard_info() -> dict:
    """
    获取剪切板环境信息
    
    Returns:
        dict: 包含环境信息的字典
    """
    return {
        "is_ssh_session": is_ssh_session(),
        "is_terminal_supports_osc52": is_terminal_supports_osc52(),
        "ssh_client": os.environ.get('SSH_CLIENT'),
        "ssh_tty": os.environ.get('SSH_TTY'),
        "ssh_connection": os.environ.get('SSH_CONNECTION'),
        "term": os.environ.get('TERM'),
        "term_program": os.environ.get('TERM_PROGRAM'),
        "is_tty": sys.stdout.isatty()
    }


if __name__ == "__main__":
    # 测试功能
    print("剪切板环境信息:")
    info = get_clipboard_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # 测试复制功能
    test_text = "这是一个测试文本"
    success, method = copy_to_clipboard(test_text)
    if success:
        print(f"\n✅ 复制成功，使用方法: {method}")
    else:
        print(f"\n❌ 复制失败: {method}")