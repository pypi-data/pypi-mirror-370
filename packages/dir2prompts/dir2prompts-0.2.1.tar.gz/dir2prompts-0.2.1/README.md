# dir2prompt

一个简单易用的命令行工具，用于生成目录树结构。

## 功能特点

- 生成清晰的目录树结构
- 支持排除指定目录或文件
- 支持仅包含指定目录或文件
- 跨平台支持（Windows、macOS、Linux）
- **🆕 智能剪切板支持（默认启用）**
  - 默认同时在终端显示并复制到剪切板
  - 本地环境：使用系统剪切板
  - SSH环境：通过OSC 52转义序列支持远程剪切板  
  - 自动检测环境并选择最佳复制方法
- 简洁的命令行界面

## 安装

使用 pip 安装：

```bash
pip install dir2prompt
```

## 使用方法

### 基本用法

```bash
# 显示当前目录的树结构（默认同时复制到剪切板）
dir2prompt .

# 显示指定目录的树结构（默认同时复制到剪切板）
dir2prompt /path/to/your/project
```

### 高级用法

```bash
# 排除特定目录
dir2prompt . --ex node_modules --ex .git

# 仅包含特定目录
dir2prompt /project --in src --in docs

# 组合使用排除和包含
dir2prompt /project --ex __pycache__ --in src --in tests

# 输出到文件（同时复制到剪切板）
dir2prompt . -o tree.txt

# 仅显示在终端，不复制到剪切板
dir2prompt . --no-clipboard
```

### 命令行选项

- `path`: 要扫描的目录路径
- `--ex, --exclude`: 排除的路径（可多次使用）
- `--in, --include`: 包含的路径（可多次使用）
- `-o, --output`: 输出到指定文件
- `--no-clipboard`: 禁用剪切板功能，仅在终端显示
- `--clipboard-info`: 显示剪切板环境信息
- `--clipboard-method`: 指定剪切板复制方法 (`auto`/`osc52`/`pyperclip`)
- `-h, --help`: 显示帮助信息

### 剪切板功能详解

#### 默认行为
```bash
# 默认同时显示在终端并复制到剪切板
dir2prompt .

# 仅在终端显示，不复制到剪切板
dir2prompt . --no-clipboard
```

#### 环境自适应
```bash
# 本地环境：自动使用系统剪切板
# SSH环境：自动使用OSC 52转义序列
dir2prompt .

# 查看剪切板环境信息
dir2prompt . --clipboard-info

# 强制使用OSC 52方法（适用于SSH）
dir2prompt . --clipboard-method osc52

# 强制使用pyperclip方法（适用于本地）
dir2prompt . --clipboard-method pyperclip
```

#### 支持的终端
OSC 52转义序列支持以下终端：
- iTerm2, Terminal.app (macOS)
- Windows Terminal, ConEmu (Windows) 
- Alacritty, kitty, wezterm (跨平台)
- tmux, screen (终端复用器)
- VS Code集成终端
- 大多数现代终端模拟器

## 示例输出

```
project/
├── src/
│   ├── __init__.py
│   └── main.py
├── tests/
│   └── test_main.py
├── pyproject.toml
├── README.md
└── LICENSE
```

## 开发

如果你想参与开发或自定义功能：

```bash
# 克隆仓库
git clone https://github.com/Jeffjeno/dir2prompt.git
cd dir2prompt

# 安装开发依赖
pip install -e .

# 运行工具
dir2prompt .
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！