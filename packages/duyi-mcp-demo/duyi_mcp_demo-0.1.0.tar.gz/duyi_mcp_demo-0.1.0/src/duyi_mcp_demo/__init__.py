from mcp.server.fastmcp import FastMCP

# 创建一个 FastMCP 实例
mcp = FastMCP("Demo")


# 注册一个工具
@mcp.tool()
def add(a: int, b: int) -> int:
    """计算两个数的和"""
    return a + b


# 注册一个资源
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """根据名字生成问候语"""
    return f"Hello, {name}！"


def main() -> None:
    mcp.run("stdio")
