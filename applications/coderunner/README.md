# Secure Code Runner

A hardened FastAPI application designed to execute arbitrary Python code from Azure Blob Storage in a secure, isolated sandbox environment.

## Features

- **Secure Execution**: Uses `bubblewrap` (bwrap) for container-level isolation (filesystem restrictions, namespace isolation).
- **Ephemeral Sandboxes**: Creates temporary Linux users with restricted permissions for each execution.
- **Integrity Checking**: Verifies MD5 checksums of code blobs before execution.
- **Resource Efficient**: Built on Alpine Linux and optimized with `uv` for minimal footprint.

## Configuration

Copy the example environment file and configure your Azure credentials:

```bash
cp .env.example .env
```

| Variable | Description | Default |
|----------|-------------|---------|
| `AZURE_STORAGE_CONNECTION_STRING` | Connection string for Azure Blob Storage (or Azurite) | (Required) |
| `CODE_CONTAINER_NAME` | Blob container name | `coderunner` |
| `SANDBOX_GROUP_NAME` | Linux group for sandbox users | `sandbox_group` |
| `PORT` | Application port | `7900` |
| `HOST` | Application host | `0.0.0.0` |

---

## Development (VS Code Dev Container)

This project is configured with a Dev Container that includes all necessary dependencies (`uv`, `python 3.13`, `azurite`).

1. **Open in Container**: Open this folder in VS Code and select "Reopen in Container".
2. **Install Dependencies**:
   ```bash
   /workspaces/dius-infra-monorepo/applications/coderunner
   uv sync
   ```
3. **Start services**: Ensure Azurite is running (usually handled by VS Code extension or external container). Verification:
   ```bash
   # Check if port 10000 is open
   nc -zv 127.0.0.1 10000
   ```
4. **Run the Application**:
   Since the application requires root privileges to manage users and namespaces (`useradd`, `bwrap`), it must be run with `sudo`. We explicitly point to the virtual environment's Python to utilize installed dependencies.

   ```bash
   sudo .venv/bin/python main.py
   ```

   The server will start at `http://0.0.0.0:7900`.

---

## Demo (Docker Compose)

For a quick demonstration with pre-configured dependencies and a local Azurite instance:

```bash
docker compose -f compose.demo.yaml up --build
```

This will:
1. Build the `coderunner` image.
2. Start an ephemeral `azurite` instance for Blob Storage.
3. Start the application with `privileged` mode (required for `bubblewrap` isolation).
4. Expose the API at `http://localhost:7900`.

To stop the demo and clean up:
```bash
docker compose -f compose.demo.yaml down
```

---

## API Usage

### Execute Code
**POST** `/runcode/`

**Request Body**:
```json
{
  "blob_name": "script.py",
  "file_hash": "md5_hash_of_file",
  "arguments": {
    "arg1": "value1"
  }
}
```

**Example**:

Read tool hashes from the logs at startup.  
`app-1      | INFO:coderunner:Example 'tool.py' initialized. Local MD5 Hash: 7ae965d5837bf61dc880b71f11d6f344`  
`app-1      | INFO:coderunner:Example 'attack.py' initialized. Local MD5 Hash: 29d989943038b0fcde4836a0e3b447a4`  
Replace `$TOOL_HASH` with corresponding md5 hash.

### Joke Telling Tool
```bash
curl -X POST "http://localhost:7900/runcode/" \
     -H "Content-Type: application/json" \
     -d '{
           "blob_name": "tool.py",
           "file_hash": "$TOOL_HASH",
           "arguments": {
               "age": 25
           }
         }'
```
### Malicious Code
```bash
curl -X POST "http://localhost:7900/runcode/" \
     -H "Content-Type: application/json" \
     -d '{
           "blob_name": "attack.py",
           "file_hash": "$TOOL_HASH",
           "arguments": {}
         }'
```

# TODO:
- Create a separate venv with preload of allowed python packages for the sandboxed code.
- To avoid using privileged/host kernel access, use `runtimeClassName: kata-qemu  # or kata-fc (Firecracker)`, this makes `securityContext.privileged: true` secure.