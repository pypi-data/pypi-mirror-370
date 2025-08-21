# python -m 的时候会执行此文件

import asyncio
from .core import mcp_stdio_server

if __name__ == "__main__":
    asyncio.run(mcp_stdio_server())