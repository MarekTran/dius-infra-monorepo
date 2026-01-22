# Do not delete this, this is part of a demo and is preloaded into the blob storage.
import os
import sys
import subprocess
import socket

def print_section(title):
    print(f"\n{'='*20} {title} {'='*20}")

def attempt_env_vars():
    print_section("Attempting to Access Environment Variables")
    try:
        env_vars = os.environ
        if not env_vars:
            print("Environment variables are empty.")
        else:
            print(f"Start of Exfiltration: Found {len(env_vars)} environment variables:")
            for key, value in env_vars.items():
                print(f"{key}: {value}")
    except Exception as e:
        print(f"Error accessing environment variables: {e}")

def attempt_filesystem_access():
    print_section("Attempting Filesystem Access")
    
    # List current directory
    try:
        print(f"Current Directory: {os.getcwd()}")
        print(f"Contents: {os.listdir('.')}")
    except Exception as e:
        print(f"Error listing current directory: {e}")

    # Attempt to read /etc/passwd
    target_file = "/etc/passwd"
    try:
        print(f"\nAttempting to read {target_file}...")
        with open(target_file, "r") as f:
            content = f.read()
            # Print first few lines to prove access without dumping everything
            print(f"Success! First 5 lines:\n{'\n'.join(content.splitlines()[:5])}")
    except Exception as e:
        print(f"Failed to read {target_file}: {e}")

    # Attempt to list root
    try:
        print("\nAttempting to list / ...")
        print(f"Contents of /: {os.listdir('/')}")
    except Exception as e:
        print(f"Error listing /: {e}")

def attempt_network_access():
    print_section("Attempting Network Access (DNS Resolution)")
    target_host = "google.com"
    try:
        ip = socket.gethostbyname(target_host)
        print(f"Success! Resolved {target_host} to {ip}")
    except Exception as e:
        print(f"Failed to resolve {target_host}: {e}")

def attempt_user_info():
    print_section("User Information")
    try:
        print(f"Current User: {os.getlogin()}")
    except Exception:
        # os.getlogin() can fail in some environments
        pass
    print(f"UID: {os.getuid()}")
    print(f"GID: {os.getgid()}")
    
    try:
        print(f"Whoami output: {subprocess.check_output(['whoami']).strip().decode()}")
    except Exception as e:
        print(f"Error running whoami: {e}")

def main():
    print("Starting Security Test Simulation...")
    attempt_user_info()
    attempt_env_vars()
    attempt_filesystem_access()
    attempt_network_access()
    print("\nSecurity Test Simulation Complete.")

if __name__ == "__main__":
    main()
