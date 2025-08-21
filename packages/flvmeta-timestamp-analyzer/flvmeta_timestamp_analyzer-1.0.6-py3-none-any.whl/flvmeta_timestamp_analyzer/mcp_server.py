#!/usr/bin/env python3
"""
MCP服务器模块入口点
支持 python -m flvmeta_timestamp_analyzer.mcp_server 运行方式
"""

import sys
import os

# 添加项目根目录到路径，以便导入mcp_server
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from mcp_server import main

if __name__ == "__main__":
    main()