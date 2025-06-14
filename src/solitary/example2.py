#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "docker>=6.0.0",
#     "pydantic>=2.0.0",
# ]
# ///

"""Example usage of the Solitary library."""

from __future__ import annotations

from solitary import SandboxConfig, Sandbox, ResultType
from solitary.exceptions import ContainerNotFoundError


def main():
    """Demonstrate basic Solitary usage."""

    # Create configuration
    config = SandboxConfig(container="sandbox", workdir="/projects", timeout=10)

    try:
        # Example 1: Basic code execution
        print("=== Basic Code Execution ===")
        with Sandbox(config=config) as sandbox:
            result = sandbox.execute("print('Hello from sandbox!')")
            print(f"Return type: {result.return_value.type}")
            print(f"Content: {result.return_value.content.strip()}")
            print(f"Success: {result.success}")

        # Example 2: Error handling
        print("\n=== Error Handling ===")
        with Sandbox(config=config) as sandbox:
            result = sandbox.execute("1/0")
            print(f"Return type: {result.return_value.type}")
            print(f"Is error: {result.return_value.type == ResultType.ERROR}")
            print(f"Error content: {result.return_value.content}")

        # Example 3: Working directory override
        print("\n=== Working Directory ===")
        with Sandbox(config=config) as sandbox:
            result = sandbox.execute("import os; print(os.getcwd())", workdir="/tmp")
            if result.return_value.type == ResultType.OUTPUT:
                print(f"Working dir: {result.return_value.content.strip()}")

        # Example 4: Shell command execution
        print("\n=== Shell Commands ===")
        with Sandbox(config=config) as sandbox:
            result = sandbox.execute_shell("ls -la")
            if result.return_value.type == ResultType.OUTPUT:
                print("Directory listing received")

            result = sandbox.execute_shell("echo 'Hello from shell'")
            print(f"Echo: {result.return_value.content.strip()}")

        # Example 5: Container info
        print("\n=== Container Info ===")
        with Sandbox(config=config) as sandbox:
            if sandbox.is_healthy():
                info = sandbox.get_container_info()
                print(f"Container: {info.name}")
                print(f"Image: {info.image}")
                print(f"Status: {info.status}")
            else:
                print("Container not healthy")

    except ContainerNotFoundError:
        print(f"Container '{config.container}' not found!")
        print("\nTo create a Python sandbox container, run:")
        print(
            "  docker run -d --name python-sandbox python:3.11-slim tail -f /dev/null"
        )
        print("\nOr use an existing container name in the config.")


if __name__ == "__main__":
    main()
