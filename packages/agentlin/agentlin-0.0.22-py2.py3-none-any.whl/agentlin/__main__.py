"""
Entry point for running agentlin modules as executables.
Usage:
  python -m agentlin.tools.server.bash_mcp_server --port 9999
  agentlin launch --mcp-server bash --port 9999
  agentlin agent_server --port 8000
"""

from loguru import logger
import typer
import uvicorn
from agentlin.tools.server import (
    bash_mcp_server,
    file_system_mcp_server,
    memory_mcp_server,
    web_mcp_server,
    todo_mcp_server,
)


app = typer.Typer()

mcp_servers = {
    "bash": bash_mcp_server,
    "file_system": file_system_mcp_server,
    "memory": memory_mcp_server,
    "web": web_mcp_server,
    "todo": todo_mcp_server,
}

example_usage = "\n\n".join([f"agentlin launch --mcp-server {name} --host localhost --port 7779 --path /{name}_mcp --debug" for name in mcp_servers.keys()])


@app.command(
    help=f"""Run the specified MCP server.

Examples:

{example_usage}
"""
)
def launch(
    mcp_server: str = typer.Option("bash", help="The name of the MCP server to run. Choices: [bash, file_system, memory]"),
    host: str = typer.Option("localhost", help="The host to bind the server to"),
    port: int = typer.Option(7779, help="The port to run the server on"),
    path: str = typer.Option("/bash_mcp", help="The path for the MCP server"),
    home: str = typer.Option(None, help="The target directory for file operations (if applicable)"),
    debug: bool = typer.Option(False, help="Enable debug mode"),
):
    if mcp_server not in mcp_servers:
        typer.echo(f"Unknown MCP server: {mcp_server}. Available servers: {', '.join(mcp_servers.keys())}")
        raise typer.Exit(code=1)
    mcp = mcp_servers[mcp_server].mcp
    if mcp_server == "file_system":
        if home:
            mcp_servers[mcp_server].TARGET_DIRECTORY = home
        else:
            typer.echo("For file_system server, please specify --home to set the target directory.")
            raise typer.Exit(code=1)
    typer.echo(f"Starting {mcp_server} MCP server on {host}:{port} at path {path} with debug={debug}")
    # Run the selected MCP server
    mcp.run("http", host=host, port=port, path=path, log_level="debug" if debug else "info")


@app.command(
    help="Run the agent server",
)
def agent_server(
    host: str = typer.Option("localhost", help="The host to bind the agent server to"),
    port: int = typer.Option(9999, help="The port to run the agent server on"),
    debug: bool = typer.Option(False, help="Enable debug mode for the agent server"),
    env_file: str = typer.Option(".env", help="Path to the .env file for environment variables"),
):
    """
    Run the agent server with the specified host and port.
    """
    typer.echo(f"Starting agent server on {host}:{port}")
    from agentlin.route.server import app

    if debug:
        logger.info("Debug mode is enabled.")
        app.debug = True
        app.logger.setLevel("DEBUG")

    if env_file:
        from dotenv import load_dotenv

        load_dotenv(env_file)
        logger.info(f"Loading environment variables from {env_file}")

    # Run the FastAPI app
    typer.echo(f"Running Agent Server at http://{host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    app()
