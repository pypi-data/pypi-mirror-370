# dir2prompt

一个简单易用的命令行工具，用于生成目录树结构。

## 功能特点

- 生成清晰的目录树结构
- 支持排除指定目录或文件
- 支持仅包含指定目录或文件
- 跨平台支持（Windows、macOS、Linux）
- 简洁的命令行界面

## 安装

使用 pip 安装：

```bash
pip install dir2prompt
```

## 使用方法

### 基本用法

```bash
# 显示当前目录的树结构
dir2prompt .

# 显示指定目录的树结构
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

# 输出到文件
dir2prompt . -o tree.txt
```

### 命令行选项

- `path`: 要扫描的目录路径
- `--ex, --exclude`: 排除的路径（可多次使用）
- `--in, --include`: 包含的路径（可多次使用）
- `-o, --output`: 输出到指定文件
- `-h, --help`: 显示帮助信息

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