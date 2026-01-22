# dius-infra-monorepo
# TODO LIST:

### AgenticSwarm

### Code Runner
[README](applications/coderunner/README.md)
FastAPI server executing python code.  

### DataMap MCP Server
FastMCP server. Only need 1 replica as this is basically a proxy. Very lightweight, no need to scale.
- On startup load tool config from Datamap
- dynamic adding of tools
- libs: numpy, pandas, requests
- generating hash of source code for tools
- authorization of agents to tools

Depends on: 
- Object storage

### Redis
- used for pub/sub channels

### VibeCode UI + Tool **CICD pipeline
- Code checker out of scope, add tool directly to Datamap -> update MCP
- can access datamap for data

### MockDataMap
FastAPI server 
Endpoints:
1. /tools/create
2. /tools/update
3. /tools/delete
4. /agents
    - Dynamic creation of tool access rules  

Models:  
Agent
- id

Tools
- id  
Available to: (Many to one) -> Agent
