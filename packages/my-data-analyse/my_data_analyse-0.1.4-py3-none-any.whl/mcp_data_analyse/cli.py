
import asyncio
from .core import mcp_stdio_server

def main():
    asyncio.run(mcp_stdio_server())
