from fastmcp import FastMCP
import requests

mcp = FastMCP("Demo 🚀")
@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

mcp = FastMCP("Web Scraper MCP")

@mcp.tool
def fetch_page(url: str) -> str:
    """Download a web page and return its content as markdown"""
    jina_url = f"https://r.jina.ai/{url}"
    response = requests.get(jina_url, timeout=30)
    response.raise_for_status()
    return response.text




if __name__ == "__main__":
    mcp.run()

def main():
    print("Hello from 03-mcp!")


if __name__ == "__main__":
    main()


