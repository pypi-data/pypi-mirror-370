import os
import json
import httpx
from fastmcp import FastMCP


APOLLO_API_KEY = os.getenv("APOLLO_API_KEY")
APOLLO_BASE_URL = "https://api.apollo.io/api/v1"

if not APOLLO_API_KEY:
    raise ValueError("APOLLO_API_KEY environment variable is required")

# Create an HTTP client for your API
client = httpx.AsyncClient(
    base_url=APOLLO_BASE_URL,
    headers={
        "X-Api-Key": APOLLO_API_KEY,
        "Content-Type": "application/json",
        "Cache-Control": "no-cache"
    }
)

# Load your OpenAPI spec
with open(os.path.join(os.path.dirname(__file__), 'schema.json'), ) as f:
    openapi_spec = json.load(f)

# Create the MCP server
mcp = FastMCP.from_openapi(
    openapi_spec=openapi_spec,
    client=client,
    name="Apollo.io MCP Server"
)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
