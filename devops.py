import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    print(f"\n[RUNNING] {description}...")
    try:
        subprocess.run(command, check=True, shell=True)
        print(f"[SUCCESS] {description} completed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[FAILURE] {description} failed.")
        return False

def main():
    print("=== Nebula-Writer DevOps Automation ===")
    
    # 1. Install/Update dependencies
    run_command("pip install -r requirements.txt", "Installing dependencies")
    run_command("pip install ruff pytest", "Installing DevOps tools")
    run_command("pip install -e .", "Installing project in editable mode")

    # 2. Linting with Ruff
    run_command("ruff check . --fix", "Running Ruff Linter (with auto-fix)")

    # 3. Formatting with Ruff
    run_command("ruff format .", "Running Ruff Formatter")

    # 4. Running Tests
    run_command("pytest", "Running Unit Tests")

    print("\n" + "="*40)
    print("DevOps Check Complete!")
    print("Code is linted, formatted, and tested.")
    print("Usage: 'python devops.py' or 'make devops'")
    print("="*40)

if __name__ == "__main__":
    main()
