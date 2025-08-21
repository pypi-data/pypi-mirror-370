from .server import serve


def main():
    """MCP Wlzdgk Server - Port add and port delete functionality for MCP"""
    import asyncio

    
    asyncio.run(serve())


if __name__ == "__main__":
    main()
