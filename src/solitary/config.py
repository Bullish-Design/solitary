from __future__ import annotations

from pydantic import BaseModel, Field


class SandboxConfig(BaseModel):
    """Configuration for sandbox execution environment."""
    
    container: str = Field(
        ..., 
        description="Container name or ID to connect to"
    )
    workdir: str = Field(
        default="/workspace",
        description="Working directory for code execution"
    )
    timeout: int = Field(
        default=30,
        ge=1,
        le=3600,
        description="Execution timeout in seconds"
    )
    shell: str = Field(
        default="/bin/bash",
        description="Shell to use for command execution"
    )

    class Config:
        """Pydantic configuration."""

        frozen = True
        validate_assignment = True
