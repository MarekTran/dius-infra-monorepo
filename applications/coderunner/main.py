import os
import sys
import subprocess
import tempfile
import uuid
import hashlib
import shutil
import pwd
import grp
import logging
import json
from typing import Dict, Any, Tuple, Generator
from contextlib import contextmanager, asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from azure.storage.blob import BlobServiceClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("coderunner")

# Silence Azure SDK logs (only show warnings and errors)
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)

class Settings(BaseSettings):
    
    azure_storage_connection_string: str = Field(..., description="Azure Storage Connection String")
    code_container_name: str = Field("coderunner", description="Azure Blob Container name for source code")
    sandbox_group_name: str = Field("sandbox_users", description="Linux group name for sandbox users")
    port: int = Field("7900", description="Port for the FastAPI application")
    host: str = Field("0.0.0.0", description="Host for the FastAPI application")
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

# Initialize Blob Client
blob_service_client = None
if settings.azure_storage_connection_string:
    try:
        # Using specific API version for compatibility
        blob_service_client = BlobServiceClient.from_connection_string(
            settings.azure_storage_connection_string, 
            api_version="2021-08-06"
        )
    except Exception as e:
        logger.error(f"Failed to initialize BlobServiceClient: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    
    # 0. Check privileges
    if os.geteuid() != 0:
        logger.warning(
            "Application is not running as root. "
            "Sandbox user creation/management will fail. "
            "Ensure the application has sufficient privileges (e.g., sudo) or capabilities (CAP_SETUID, CAP_SETGID, CAP_CHOWN)."
        )

    # 1. Ensure sandbox group exists
    try:
        try:
            grp.getgrnam(settings.sandbox_group_name)
            logger.info(f"Sandbox group '{settings.sandbox_group_name}' already exists.")
        except KeyError:
            logger.info(f"Sandbox group '{settings.sandbox_group_name}' not found. Creating it.")
            subprocess.run(["groupadd", "-f", settings.sandbox_group_name], check=True)
    except Exception as e:
        logger.error(f"Failed to ensure sandbox group exists: {e}")
        # We might continue, but execution will likely fail later if group is missing

    if blob_service_client:
        try:
            logger.info("Initializing application resources...")
            
            # 1. Ensure container exists
            container_client = blob_service_client.get_container_client(settings.code_container_name)
            if not container_client.exists():
                logger.info(f"Creating container: {settings.code_container_name}")
                container_client.create_container()
            
            # 2. Upload example tools and print hash
            for filename in ["tool.py", "attack.py"]:
                example_path = os.path.join(os.path.dirname(__file__), "examples", filename)
                if os.path.exists(example_path):
                    with open(example_path, "rb") as f:
                        content = f.read()
                        file_hash = hashlib.md5(content).hexdigest()
                    
                    blob_name = filename
                    logger.info(f"Uploading example '{blob_name}' from '{example_path}'")
                    blob_client = container_client.get_blob_client(blob_name)
                    blob_client.upload_blob(content, overwrite=True)
                    
                    logger.info(f"Example '{blob_name}' initialized. Local MD5 Hash: {file_hash}")
                else:
                    logger.warning(f"Example not found at {example_path}")
                
        except Exception as e:
            logger.error(f"Error during startup initialization: {e}")
    
    yield
    # Shutdown logic if needed

app = FastAPI(title="Secure Code Runner", lifespan=lifespan)

class ExecutionRequest(BaseModel):
    blob_name: str = Field(..., description="The name of the blob file to execute", example="hello_world.py")
    file_hash: str = Field(..., description="MD5 hash of the file for integrity verification", example="a1b2c3d4e5f6...")
    arguments: Dict[str, Any] = Field(default={}, description="Key-value arguments to pass to the script", example={"param1": "value1"})

class ExecutionResult(BaseModel):
    return_code: int = Field(..., description="Exit code of the subprocess")
    stdout: str = Field(..., description="Standard output captured from the script")
    stderr: str = Field(..., description="Standard error captured from the script")

# Initialize Blob Client (Moved to top level for access in lifespan, keeping logic consistent)
# Validated in startup/lifespan


def verify_file_hash(file_path: str, expected_hash: str) -> bool:
    """Calculates MD5 hash of file and compares with expected hash."""
    try:
        with open(file_path, "rb") as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        logger.info(f"Calculated hash: {file_hash}, Expected: {expected_hash}")
        return file_hash == expected_hash
    except Exception as e:
        logger.error(f"Error verifying hash: {e}")
        return False

@contextmanager
def temporary_sandbox_user(group_name: str) -> Generator[Tuple[int, int], None, None]:
    """
    Context manager to create a temporary user and delete it afterwards.
    Requires root privileges.
    """
    # Generate unique username
    username = f"sandbox_{uuid.uuid4().hex[:8]}"
    created = False
    try:
        # Create user with no home directory, specific group
        # -M: no home dir, -N: no user group (use -g), -g: group
        cmd = ["useradd", "-M", "-N", "-g", group_name, username]
        
        # Security: Check if group exists first (optional, useradd might fail if not)
        # Assuming group exists as per requirements
        
        logger.info(f"Creating temporary user: {username}")
        subprocess.run(cmd, check=True, capture_output=True)
        created = True
        
        # Get UID/GID
        user_info = pwd.getpwnam(username)
        yield user_info.pw_uid, user_info.pw_gid
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to create temp user {username}: {e.stderr.decode()}")
        # If user creation fails, we cannot proceed with secure execution
        raise HTTPException(status_code=500, detail="Failed to initialize sandbox environment.")
    except KeyError:
        logger.error(f"User {username} created but not found in pwd DB.")
        raise HTTPException(status_code=500, detail="Internal system error.")
    finally:
        if created:
            try:
                logger.info(f"Removing temporary user: {username}")
                # Ensure processes are killed? (subprocess.run waits, so usually fine unless backgrounded)
                subprocess.run(["userdel", "-f", username], check=False, capture_output=True)
            except Exception as e:
                logger.error(f"Failed to remove user {username}: {e}")

@app.post("/runcode/", response_model=ExecutionResult)
async def run_code(request: ExecutionRequest):
    if not blob_service_client:
        raise HTTPException(status_code=500, detail="Storage client not configured.")

    temp_dir = tempfile.mkdtemp()
    script_path = os.path.join(temp_dir, os.path.basename(request.blob_name))
    
    try:
        # 1. Fetch script
        logger.info(f"Fetching blob: {request.blob_name}")
        container_client = blob_service_client.get_container_client(settings.code_container_name)
        blob_client = container_client.get_blob_client(request.blob_name)
        
        if not blob_client.exists():
            raise HTTPException(status_code=404, detail=f"Blob file '{request.blob_name}' not found.")

        with open(script_path, "wb") as f:
            download_stream = blob_client.download_blob()
            f.write(download_stream.readall())
            
        # 2. Verify integrity
        if not verify_file_hash(script_path, request.file_hash):
            raise HTTPException(status_code=400, detail="File integrity check failed. Hash mismatch.")
            
        # 3. Secure Execution
        # We need root privileges to switch users. Assuming the container runs as root.
        # If running locally in non-root devcontainer, this will likely fail conceptually 
        # but we implement as per requirements.
        
        try:
            with temporary_sandbox_user(settings.sandbox_group_name) as (uid, gid):
                # Prepare permissions
                # Change owner of temp directory to the sandbox user so they can write temp files if needed
                # and read the script
                os.chown(temp_dir, uid, gid)
                # Ensure directory is executable/searchable
                os.chmod(temp_dir, 0o755)

                # Change owner of script
                os.chown(script_path, uid, gid)
                # Permissions: Make world readable to avoid user namespace mapping issues
                # (When unsharing user ns without explicit mapping, ownership might look like overflowuid)
                os.chmod(script_path, 0o444)
                
                # Construct command
                # We use bubblewrap (bwrap) to restrict filesystem access
                # This ensures the process only sees what we explicitly bind.
                bwrap_cmd = [
                    "bwrap",
                    "--unshare-all",
                    "--share-net",          # Requirement: Keep network access
                    "--dev", "/dev",
                    "--proc", "/proc",
                    "--tmpfs", "/tmp",      # Fresh tmp
                    
                    # Read-only system paths for Python
                    "--ro-bind", "/usr", "/usr",
                    "--ro-bind", "/bin", "/bin",
                    "--ro-bind", "/lib", "/lib",
                    "--ro-bind", "/sbin", "/sbin",
                    # Python usually lives in /usr/local in Docker images
                    "--ro-bind", "/usr/local", "/usr/local",

                    # Bind the application directory (where venv lives)
                    "--ro-bind", "/app", "/app",
                    
                    # Network configuration files (try bind if they exist)
                    "--ro-bind-try", "/etc/resolv.conf", "/etc/resolv.conf",
                    "--ro-bind-try", "/etc/hosts", "/etc/hosts",
                    "--ro-bind-try", "/etc/ssl", "/etc/ssl",
                    "--ro-bind-try", "/etc/pki", "/etc/pki",
                    "--ro-bind-try", "/etc/ca-certificates", "/etc/ca-certificates",
                    
                    # Bind the working directory (read-write for the script execution)
                    "--bind", temp_dir, temp_dir,
                    "--chdir", temp_dir,
                    
                    # Drop privileges to the sandbox user inside the namespace
                    "--uid", str(uid),
                    "--gid", str(gid),
                    
                    # Command to run
                    sys.executable, script_path
                ]
                
                # Arguments handling: passing as key=value or --key value
                # Using --key value pattern typical for CLI tools
                for k, v in request.arguments.items():
                    bwrap_cmd.append(f"--{k}")
                    bwrap_cmd.append(str(v))
                
                logger.info(f"Executing script as uid={uid} in {temp_dir} using bwrap")
                
                # Run subprocess
                # Note: We run bwrap as root (user=None), and it handles dropping privileges
                result = subprocess.run(
                    bwrap_cmd,
                    # user=uid, # REMOVED: bwrap needs to start as root to set up mounts, then it drops user
                    # group=gid,
                    cwd="/",     # Run from root to avoid issues with host cwd being hidden/masked
                    env={},           # Empty environment variables (Security requirement)
                    capture_output=True,
                    text=True,
                    timeout=60        # Timeout
                )
                
                logger.info(f"Execution finished with return code {result.returncode}")
                
                return ExecutionResult(
                    return_code=result.returncode,
                    stdout=result.stdout,
                    stderr=result.stderr
                )

        except subprocess.TimeoutExpired:
            logger.warning("Script execution timed out.")
            return ExecutionResult(
                return_code=124, # Standard timeout exit code
                stdout="",
                stderr="Execution timed out."
            )
        except PermissionError as e:
            # If we struggle with user switching permissions
            logger.error(f"Permission error during sandbox execution: {e}")
            raise HTTPException(status_code=500, detail="Sandbox permission error.")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error during execution request.")
        # If the failure is internal to the runner (fetching, setup), return 500
        # If the script ran but failed, it's handled above in subprocess.run
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup temp directory
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    uvicorn.run(app, host=settings.host, port=settings.port)
