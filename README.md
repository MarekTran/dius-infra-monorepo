## AgenticSwarm

## Code Runner
[README](applications/coderunner/README.md)  
Sandboxed python code execution server.  

## DataMap MCP Server
FastMCP server. Only need 1 replica as this is basically a proxy. Very lightweight, no need to scale.
- On startup load tool config from Datamap
- dynamic adding of tools
- libs: numpy, pandas, requests
- generating hash of source code for tools
- authorization of agents to tools

Depends on: 
- Object storage

## Redis
- used for pub/sub channels

## VibeCode UI + Tool **CICD pipeline
- Code checker out of scope, add tool directly to Datamap -> update MCP
- can access datamap for data

## MockDataMap
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


### Hours spent log:  
**Marek**  
21.1.2026  
8 hours - Commits `bcf0b7420f0de8505f830e3fc6c699a406b69ed4` - `7222992a104bafde282bdf854dca98703b19b894`  
22.1.2026  
5 hours - Commits `a395268e3bc00cb097c4109378bde2fade3ec4a9` - `7222992a104bafde282bdf854dca98703b19b894`