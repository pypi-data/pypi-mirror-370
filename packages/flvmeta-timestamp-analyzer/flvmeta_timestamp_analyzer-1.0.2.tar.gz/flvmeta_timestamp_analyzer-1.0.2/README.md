# FLV Timestamp Analyzer

FLV音视频时间戳分析工具，可用于检测FLV文件中的时间戳异常，如时间回退、大跳跃、缺失帧等问题。

## 功能特点

- 解析FLV文件中的音视频时间戳
- 分析时间戳间隔变化
- 检测时间戳异常（时间回退、大跳跃、缺失帧）
- 生成可视化图表
- 提供详细的文本分析报告
- 支持MCP协议，可作为AI模型服务集成

## 安装依赖

1. 安装Python依赖：
   ```bash
   pip install -r requirements.txt
   ```

2. 安装flvmeta工具：
   - macOS: `brew install flvmeta`
   - Linux: `sudo apt-get install flvmeta` 或从源码编译
   - Windows: 下载 https://github.com/noirotm/flvmeta/releases
   - 源码: https://github.com/noirotm/flvmeta

## 安装

### 使用pip安装

```bash
pip install flvmeta-timestamp-analyzer
```

### 使用npx安装

```bash
npx flvmeta-timestamp-analyzer
```

## 使用方法

### 命令行直接使用
```bash
# 基本用法
python3 flv_timestamp_analyzer.py input.flv

# 指定输出HTML文件
python3 flv_timestamp_analyzer.py input.flv output.html
```

### 作为MCP服务使用
```bash
# 启动MCP服务
python3 mcp_server.py

# 或使用调试客户端测试
python3 debug_client.py
```

## 详细发布和使用教程

请查看 [PUBLISHING_AND_USAGE.md](PUBLISHING_AND_USAGE.md) 获取详细的发布和使用教程，包括：
- 如何注册PyPI和npm账户
- 如何配置认证信息
- 如何构建和发布包
- 如何安装和使用工具
- 如何在AI客户端中使用MCP服务
- 故障排除指南

## MCP集成

本工具支持MCP协议，可以作为AI模型服务集成到支持MCP的平台中。

### MCP配置
- 模型名称: `flv-timestamp-analyzer`
- 支持文件输入
- 不支持流式传输
- 不支持音频/图像/文本输入

### MCP服务配置
在 `.mcp.servers.json` 中配置：
```json
{
  "mcpServers": {
    "flv-timestamp-analyzer": {
      "command": "python3",
      "args": ["-u", "mcp_server.py"],
      "cwd": "."
    }
  }
}
```

## 输出说明

### 文本报告
工具会输出详细的文本分析报告，包括：
- 音视频帧数和时长
- 时间戳间隔的平均值、最大值、最小值
- 检测到的异常点及其类型和位置

### 可视化图表
工具会生成HTML格式的可视化图表，显示：
- 音视频时间戳增量变化曲线
- 平均值参考线
- 异常点标记
- 支持缩放和拖拽查看

## 调试方法

### 使用调试客户端
```bash
# 交互式调试模式
python3 debug_client.py

# 单次测试
python3 debug_client.py /path/to/your/file.flv
```

### 查看日志
MCP服务会生成日志文件 `mcp_server.log`：
```bash
# 查看实时日志
tail -f mcp_server.log

# 查看错误日志
grep ERROR mcp_server.log
```