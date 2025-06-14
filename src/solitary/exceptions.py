from __future__ import annotations


class SandboxError(Exception):
    """Base exception for Solitary sandbox errors."""
    pass


class ContainerNotFoundError(SandboxError):
    """Raised when specified container cannot be found."""
    pass


class ExecutionTimeoutError(SandboxError):
    """Raised when code execution times out."""
    pass


class ContainerConnectionError(SandboxError):
    """Raised when connection to container fails."""
    pass
