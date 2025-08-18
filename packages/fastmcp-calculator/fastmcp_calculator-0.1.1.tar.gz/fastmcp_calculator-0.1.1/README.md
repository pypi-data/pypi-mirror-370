# FastMCP Calculator

这是一个基于FastMCP的测试项目，提供了基本的数学运算功能。

## 功能介绍

该项目实现了一个简单的MCP服务器，包含以下工具：

- `add`: 计算两个整数的和
- `subtract`: 计算两个整数的差
- `multiply`: 计算两个整数的积
- `divide`: 计算两个数的商（包含除数为零检查）

## 安装要求

- Python 3.13或更高版本
- MCP CLI 1.13.0或更高版本

## 安装步骤

1. 从PyPI安装：`pip install fastmcp-calculator`
2. 或者克隆此项目后本地安装：
   - 进入项目目录：`cd d:\MCP_test1`
   - 安装依赖：`uv install`（如果使用uv）或`pip install -e .`

## 使用方法

1. 启动服务器：`python main.py`
2. 使用MCP客户端调用工具，例如：
   ```bash
   mcp call mcp.config.usrlocalmcp.mcp-calculate add --a 10 --b 5
   ```

## 示例

### 调用add工具
```bash
mcp call mcp.config.usrlocalmcp.mcp-calculate add --a 233 --b 1
# 输出: 234
```

### 调用subtract工具
```bash
mcp call mcp.config.usrlocalmcp.mcp-calculate subtract --a 233 --b 1
# 输出: 232
```

### 调用multiply工具
```bash
mcp call mcp.config.usrlocalmcp.mcp-calculate multiply --a 10 --b 5
# 输出: 50
```

### 调用divide工具
```bash
mcp call mcp.config.usrlocalmcp.mcp-calculate divide --a 10 --b 2
# 输出: 5.0
```

## 贡献指南

欢迎提交问题和拉取请求来改进这个项目。

## 许可证

[MIT License](LICENSE)