# MCP协议支持说明

本项目已支持MCP（Model Context Protocol）协议，可以将黄历AI Agent功能暴露为MCP工具，供支持MCP的AI客户端使用。

## 安装依赖

首先安装MCP SDK：

```bash
pip install mcp
```

或者使用requirements.txt安装所有依赖：

```bash
pip install -r requirements.txt
```

## MCP服务器功能

MCP服务器提供了以下两个工具：

### 1. get_calendar_info

获取指定日期的黄历信息。

**参数：**
- `date` (必需): 日期，可以是相对日期（今天、明天、后天等）或具体日期（YYYY-MM-DD格式）
- `force_refresh` (可选): 是否强制从API获取最新数据，忽略缓存。默认为false

**示例：**
```json
{
  "date": "今天",
  "force_refresh": false
}
```

### 2. answer_calendar_question

回答关于黄历的问题。

**参数：**
- `question` (必需): 用户关于黄历的问题，可以包含相对日期（今天、明天等）或具体日期
- `force_refresh` (可选): 是否强制从API获取最新数据，忽略缓存。默认为false

**示例：**
```json
{
  "question": "今天适合做什么？",
  "force_refresh": false
}
```

## 配置MCP服务器

### 在Cursor中配置

1. 打开Cursor设置
2. 找到MCP服务器配置（通常在 `~/.cursor/mcp.json` 或项目配置中）
3. 添加以下配置：

```json
{
  "mcpServers": {
    "cardcaptor-calendar": {
      "command": "python",
      "args": [
        "/path/to/your/project/mcp_server.py"
      ],
      "env": {
        "DEEPSEEK_API_KEY": "your-deepseek-api-key-here",
        "DEEPSEEK_BASE_URL": "https://api.deepseek.com/v1",
        "DEEPSEEK_LLM_MODEL": "deepseek-r1-250528"
      }
    }
  }
}
```

**注意：** 请将 `/path/to/your/project/mcp_server.py` 替换为实际的项目路径。

### 环境变量

确保设置以下环境变量（可以通过配置文件或系统环境变量）：

- `DEEPSEEK_API_KEY`: DeepSeek API密钥
- `DEEPSEEK_BASE_URL`: DeepSeek API基础URL（可选，默认为 https://api.deepseek.com/v1）
- `DEEPSEEK_LLM_MODEL`: 使用的模型名称（可选，默认为 deepseek-r1-250528）

## 运行MCP服务器

### 直接运行

```bash
python mcp_server.py
```

### 通过MCP客户端连接

MCP服务器使用stdio传输，可以通过支持MCP的客户端（如Cursor、Claude Desktop等）连接。

## 测试

可以使用MCP客户端工具测试服务器功能，或直接在支持MCP的AI应用中使用。

## 故障排除

1. **导入错误**: 确保已安装MCP SDK：`pip install mcp`
2. **环境变量**: 确保设置了必要的环境变量
3. **路径问题**: 确保MCP配置文件中的路径正确
4. **权限问题**: 确保Python脚本有执行权限

## 更多信息

关于MCP协议的更多信息，请参考：
- [MCP官方文档](https://modelcontextprotocol.io)
- [Cursor MCP文档](https://docs.cursor.com/zh/context/mcp)

