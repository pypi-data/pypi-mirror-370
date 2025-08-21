#!/usr/bin/env python3
"""
md_to_word_mcp 主入口
"""

import sys
import asyncio
from .server import main as async_main


def main() -> None:
    """同步入口，包装异步服务器启动。"""
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("\n服务器已停止")
        sys.exit(0)
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
