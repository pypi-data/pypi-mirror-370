#!/bin/bash
# Upgrade the dependencies including those from Git sources
uv lock -U
# Export the requirements to a requirements.txt file
uv export --no-hashes --format requirements-txt > requirements.txt
# Run tests using pytest
MCP_SERVER_INCLUDE_METADATA_IN_RESPONSE=true MCP_SERVER_TRANSPORT=streamable-http uv run --group test pytest tests/
