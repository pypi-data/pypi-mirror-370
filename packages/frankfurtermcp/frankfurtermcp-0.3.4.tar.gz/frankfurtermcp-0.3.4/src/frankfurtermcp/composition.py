import signal
import sys
from fastmcp import FastMCP
from frankfurtermcp.common import EnvironmentVariables
from frankfurtermcp.server import app as frankfurtermcp
from frankfurtermcp.common import parse_env
from dotenv import load_dotenv

app = FastMCP(
    name="test_composition",
    instructions="This is a MCP server to test dynamic composition of MCP.",
)

COMPOSITION_PREFIX = "composition_"


@app.tool(
    description="The quintessential hello world tool",
    tags=["hello", "world"],
    name="hello_world",
    annotations={
        "readOnlyHint": True,
    },
)
def hello_world(name: str = None) -> str:
    """
    A simple tool that returns a greeting message.

    Args:
        name (str): The name to greet.

    Returns:
        str: A greeting message.
    """
    suffix = "This is the MCP server to test dynamic composition."
    return f"Hello, {name}! {suffix}" if name else f"Hello World! {suffix}"


def main():
    """
    Main function to run the MCP server.
    """

    def sigint_handler(signal, frame):
        """
        Signal handler to shut down the server gracefully.
        """
        # This is absolutely necessary to exit the program
        sys.exit(0)

    load_dotenv()
    signal.signal(signal.SIGINT, sigint_handler)

    app.mount(prefix=COMPOSITION_PREFIX, server=frankfurtermcp, as_proxy=False)
    transport_type = parse_env(
        EnvironmentVariables.MCP_SERVER_TRANSPORT,
        default_value=EnvironmentVariables.DEFAULT__MCP_SERVER_TRANSPORT,
        allowed_values=EnvironmentVariables.ALLOWED__MCP_SERVER_TRANSPORT,
    )
    (
        app.run(
            transport=transport_type,
            host=parse_env(
                EnvironmentVariables.MCP_SERVER_HOST,
                default_value=EnvironmentVariables.DEFAULT__MCP_SERVER_HOST,
            ),
            port=parse_env(
                EnvironmentVariables.MCP_SERVER_PORT,
                default_value=EnvironmentVariables.DEFAULT__MCP_SERVER_PORT,
                type_cast=int,
            ),
            uvicorn_config={
                "timeout_graceful_shutdown": 5,  # seconds
            },
        )
        if transport_type != "stdio"
        else app.run(transport=transport_type)
    )


if __name__ == "__main__":
    main()
