from . import server
import asyncio

def main():
    """包的主入口点。"""
    asyncio.run(server.main())

# 可选:在包级别暴露其他重要项
__all__ = ['main', 'server']