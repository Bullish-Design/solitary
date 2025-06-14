from __future__ import annotations

import time
from pathlib import Path
from typing import Optional

import docker
from docker.errors import NotFound, APIError
from pydantic import BaseModel

from .config import SandboxConfig
from .models import ExecutionResult, ContainerInfo
from .exceptions import (
    ContainerNotFoundError,
    ExecutionTimeoutError,
    ContainerConnectionError,
)


class Sandbox(BaseModel):
    """Sandboxed code execution environment using Docker containers."""

    config: SandboxConfig
    _client: Optional[docker.DockerClient] = None
    _container: Optional[docker.models.containers.Container] = None

    class Config:
        """Pydantic configuration."""

        arbitrary_types_allowed = True

    def __enter__(self) -> Sandbox:
        """Context manager entry."""
        self._connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()

    def _connect(self) -> None:
        """Establish connection to Docker and container."""
        if self._client is None:
            try:
                self._client = docker.from_env()
            except Exception as e:
                raise ContainerConnectionError(
                    f"Failed to connect to Docker: {e}"
                ) from e

        if self._container is None:
            try:
                self._container = self._client.containers.get(self.config.container)
            except NotFound as e:
                raise ContainerNotFoundError(
                    f"Container '{self.config.container}' not found"
                ) from e
            except APIError as e:
                raise ContainerConnectionError(
                    f"Failed to access container: {e}"
                ) from e

    def execute(
        self,
        code: str,
        stdin: Optional[str] = None,
        workdir: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> ExecutionResult:
        """Execute Python code in the sandbox."""
        self._connect()

        execution_workdir = workdir or self.config.workdir
        execution_timeout = timeout or self.config.timeout

        # Create command to execute Python code
        cmd = ["python3", "-c", code]

        # Execute command in container
        start_time = time.time()
        timeout_occurred = False

        try:
            exec_result = self._container.exec_run(
                cmd,
                workdir=execution_workdir,
                stdin=True,
                stdout=True,
                stderr=True,
                demux=True,
                stream=False,
                socket=False,
                environment=None,
            )

            execution_time = time.time() - start_time

            # Handle timeout
            if execution_time > execution_timeout:
                timeout_occurred = True

            # Decode output
            stdout_bytes, stderr_bytes = exec_result.output
            stdout = stdout_bytes.decode() if stdout_bytes else ""
            stderr = stderr_bytes.decode() if stderr_bytes else ""

        except Exception as e:
            execution_time = time.time() - start_time
            return ExecutionResult(
                stdout="",
                stderr=str(e),
                exit_code=-1,
                execution_time=execution_time,
                timeout_occurred=timeout_occurred,
                container_id=self._container.id,
                command=" ".join(cmd),
            )

        return ExecutionResult(
            stdout=stdout,
            stderr=stderr,
            exit_code=exec_result.exit_code,
            execution_time=execution_time,
            timeout_occurred=timeout_occurred,
            container_id=self._container.id,
            command=" ".join(cmd),
        )

    def execute_shell(
        self,
        command: str,
        workdir: Optional[str] = None,
        timeout: Optional[int] = None,
        shell: Optional[str] = None,
    ) -> ExecutionResult:
        """Execute shell command in the sandbox."""
        self._connect()

        execution_workdir = workdir or self.config.workdir
        execution_timeout = timeout or self.config.timeout
        execution_shell = shell or self.config.shell

        # Create shell command
        cmd = [execution_shell, "-c", command]

        # Execute command in container
        start_time = time.time()
        timeout_occurred = False

        try:
            exec_result = self._container.exec_run(
                cmd,
                workdir=execution_workdir,
                stdin=True,
                stdout=True,
                stderr=True,
                demux=True,
                stream=False,
                socket=False,
                environment=None,
            )

            execution_time = time.time() - start_time

            # Handle timeout
            if execution_time > execution_timeout:
                timeout_occurred = True

            # Decode output
            stdout_bytes, stderr_bytes = exec_result.output
            stdout = stdout_bytes.decode() if stdout_bytes else ""
            stderr = stderr_bytes.decode() if stderr_bytes else ""

        except Exception as e:
            execution_time = time.time() - start_time
            return ExecutionResult(
                stdout="",
                stderr=str(e),
                exit_code=-1,
                execution_time=execution_time,
                timeout_occurred=timeout_occurred,
                container_id=self._container.id,
                command=" ".join(cmd),
            )

        return ExecutionResult(
            stdout=stdout,
            stderr=stderr,
            exit_code=exec_result.exit_code,
            execution_time=execution_time,
            timeout_occurred=timeout_occurred,
            container_id=self._container.id,
            command=" ".join(cmd),
        )

    def execute_file(
        self,
        filepath: str,
        args: Optional[list[str]] = None,
        workdir: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> ExecutionResult:
        """Execute a Python file in the sandbox."""
        # Read file content
        try:
            with open(filepath, "r") as f:
                code = f.read()
        except FileNotFoundError:
            return ExecutionResult(
                stdout="",
                stderr=f"File not found: {filepath}",
                exit_code=1,
                execution_time=0.0,
                timeout_occurred=False,
                container_id=self._container.id if self._container else "",
                command=f"python3 {filepath}",
            )

        return self.execute(code, workdir=workdir, timeout=timeout)

    def is_healthy(self) -> bool:
        """Check if container is healthy and responsive."""
        try:
            self._connect()
            # Simple test execution
            result = self.execute("print('health_check')", timeout=5)
            return result.success and "health_check" in result.stdout
        except Exception:
            return False

    def get_container_info(self) -> ContainerInfo:
        """Get information about the connected container."""
        self._connect()

        container_attrs = self._container.attrs

        return ContainerInfo(
            id=self._container.id,
            name=container_attrs["Name"].lstrip("/"),
            image=container_attrs["Config"]["Image"],
            status=container_attrs["State"]["Status"],
            created=container_attrs["Created"],
        )

    def close(self) -> None:
        """Close connections and cleanup resources."""
        if self._client:
            self._client.close()
            self._client = None
        self._container = None
