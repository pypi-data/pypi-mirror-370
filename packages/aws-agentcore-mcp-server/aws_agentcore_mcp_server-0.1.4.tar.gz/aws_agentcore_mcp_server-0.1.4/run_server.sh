#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python -m aws_agentcore_mcp_server
