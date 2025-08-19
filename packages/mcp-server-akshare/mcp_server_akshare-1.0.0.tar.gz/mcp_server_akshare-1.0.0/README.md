# MCP Server AkShare

一个基于 Model Context Protocol (MCP) 的 AkShare 金融数据接口服务器。

## 安装

### 方式 1: 使用 uvx (推荐)

```bash
uvx mcp-server-akshare
```

### 方式 2: 使用 pip

```bash
pip install mcp-server-akshare
mcp-server-akshare
```

### 方式 3: 从源码安装

```bash
git clone <repository-url>
cd mcp-server-akshare
pip install -e .
```

## MCP 客户端配置

### Claude Desktop

将以下配置添加到你的 Claude Desktop 配置文件中：

```json
{
  "mcpServers": {
    "akshare": {
      "command": "uvx",
      "args": ["mcp-server-akshare"]
    }
  }
}
```

### 其他 MCP 客户端

```json
{
  "command": "mcp-server-akshare",
  "args": [],
  "timeout": 30,
  "transportType": "stdio"
}
```

## 可用工具

### 核心工具

- `akshare_list_functions`: 列出所有可用的 AkShare 函数
- `akshare_get_categories`: 获取所有函数分类
- `akshare_call_function`: 调用任意 AkShare 函数
- `akshare_get_function_info`: 获取函数详细信息

### 常用函数快捷工具

- `akshare_stock_zh_a_hist`: 获取A股历史数据
- `akshare_stock_info_a_code_name`: 获取股票基本信息
- `akshare_macro_china_gdp`: 获取GDP数据
- `akshare_futures_main_sina`: 获取期货数据
- `akshare_bond_zh_hs_cov_daily`: 获取债券数据

## 使用示例

### 获取股票历史数据

```json
{
  "tool": "akshare_stock_zh_a_hist",
  "arguments": {
    "symbol": "000001",
    "period": "daily",
    "start_date": "20240101",
    "end_date": "20241231"
  }
}
```

### 列出股票相关函数

```json
{
  "tool": "akshare_list_functions",
  "arguments": {
    "category": "stock"
  }
}
```

### 调用任意函数

```json
{
  "tool": "akshare_call_function",
  "arguments": {
    "function_name": "stock_zh_a_hist",
    "parameters": {
      "symbol": "000001",
      "period": "daily"
    }
  }
}
```

## 支持的数据类别

- **stock**: 股票数据
- **futures**: 期货数据  
- **bond**: 债券数据
- **macro**: 宏观经济数据
- **energy**: 能源数据
- **crypto**: 加密货币数据
- **forex**: 外汇数据
- **commodity**: 商品数据
- **real_estate**: 房地产数据
- **news**: 新闻数据
- **other**: 其他数据

## 开发说明

项目结构：
```
akshare_mcp/
├── src/akshare_mcp/
│   ├── __init__.py
│   ├── server.py      # MCP服务器主程序
│   └── wrapper.py     # AkShare接口包装器
├── main.py            # 启动脚本
├── requirements.txt   # 依赖列表
└── README.md         # 说明文档
```

核心组件：
- `AkShareWrapper`: 自动发现和包装AkShare函数
- `AkShareMCPServer`: MCP协议服务器实现
