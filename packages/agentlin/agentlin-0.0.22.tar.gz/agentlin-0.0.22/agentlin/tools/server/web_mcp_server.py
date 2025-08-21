#!/usr/bin/env python3
import asyncio
from typing import Annotated, Any, Dict, List
from loguru import logger

from fastmcp import FastMCP, Context

from agentlin.tools.tool_web_fetch import web_fetch


mcp = FastMCP(
    "Web Fetch Tool Server",
    version="0.1.0",
)


@mcp.tool(
    name="web_fetch",
    title="WebFetch",
    description="""- Fetches content from a specified URL and processes it using an AI model
- Takes a URL and a prompt as input
- Fetches the URL content, converts HTML to markdown
- Processes the content with the prompt using a small, fast model
- Returns the model's response about the content
- Use this tool when you need to retrieve and analyze web content

Usage notes:
- IMPORTANT: If an MCP-provided web fetch tool is available, prefer using that tool instead of this one, as it may have fewer restrictions. All MCP-provided tools start with "mcp__"
- The URL must be a fully-formed valid URL
- HTTP URLs will be automatically upgraded to HTTPS
- The prompt should describe what information you want to extract from the page
- This tool is read-only and does not modify any files
- Results may be summarized if the content is very large
- Includes a self-cleaning 15-minute cache for faster responses when repeatedly accessing the same URL
- When a URL redirects to a different host, the tool will inform you and provide the redirect URL in a special format. You should then make a new WebFetch request with the redirect URL to fetch the content""",
)
async def web_fetch_tool(
    urls: Annotated[List[str], "List of URLs to fetch. Only URLs from the provided news articles are available"],
) -> Dict[str, Any]:
    """从URL列表获取网页内容"""
    return await web_fetch(urls)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run Web Fetch MCP SSE-based server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=7780, help="Port to listen on")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    logger.info("Starting Web Fetch MCP Server...")
    logger.info("Available tools: web_fetch")

    mcp.run("http", host=args.host, port=args.port, log_level="debug" if args.debug else "info")
