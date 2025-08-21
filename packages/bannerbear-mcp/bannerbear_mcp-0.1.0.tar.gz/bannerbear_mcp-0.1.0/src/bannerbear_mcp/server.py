import os
import json
import httpx
from fastmcp import FastMCP


BANNERBEAR_API_KEY = os.getenv("BANNERBEAR_API_KEY")
BANNERBEAR_BASE_URL = "https://api.bannerbear.com"

if not BANNERBEAR_API_KEY:
    raise ValueError("BANNERBEAR_API_KEY environment variable is required")

# Create an HTTP client for your API
client = httpx.AsyncClient(
    base_url=BANNERBEAR_BASE_URL,
    headers={
        "Authorization": f"Bearer {BANNERBEAR_API_KEY}"
    }
)

# Load your OpenAPI spec
with open(os.path.join(os.path.dirname(__file__), 'schema.json'), ) as f:
    openapi_spec = json.load(f)

# Create the MCP server
mcp = FastMCP.from_openapi(
    openapi_spec=openapi_spec,
    client=client,
    name="Bannerbear MCP Server"
)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
