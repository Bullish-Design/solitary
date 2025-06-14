from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field


class ResultType(str, Enum):
    """Type of execution result."""

    OUTPUT = "output"
    ERROR = "error"


class ResultValue(BaseModel):
    """Structured return value for execution results."""

    type: ResultType = Field(description="Type of result")
    content: str = Field(description="Result content")


class ExecutionResult(BaseModel):
    """Result of code execution in sandbox."""

    stdout: str = Field(default="", description="Standard output")
    stderr: str = Field(default="", description="Standard error")
    exit_code: int = Field(description="Process exit code")
    execution_time: float = Field(ge=0, description="Execution time in seconds")
    timeout_occurred: bool = Field(
        default=False, description="Whether execution timed out"
    )
    container_id: str = Field(description="Container ID used for execution")
    command: str = Field(description="Command that was executed")

    @property
    def success(self) -> bool:
        """True if execution completed successfully."""
        return self.exit_code == 0 and not self.timeout_occurred

    @property
    def return_value(self) -> ResultValue:
        """Structured return value based on execution outcome."""
        if self.success and self.stdout:
            return ResultValue(type=ResultType.OUTPUT, content=self.stdout)
        elif self.stderr:
            return ResultValue(type=ResultType.ERROR, content=self.stderr)
        elif not self.success:
            return ResultValue(
                type=ResultType.ERROR,
                content=f"Command failed with exit code {self.exit_code}",
            )
        else:
            return ResultValue(type=ResultType.OUTPUT, content="")


class ContainerInfo(BaseModel):
    """Result of code execution in sandbox."""

    stdout: str = Field(default="", description="Standard output")
    stderr: str = Field(default="", description="Standard error")
    exit_code: int = Field(description="Process exit code")
    execution_time: float = Field(ge=0, description="Execution time in seconds")
    timeout_occurred: bool = Field(
        default=False, description="Whether execution timed out"
    )
    container_id: str = Field(description="Container ID used for execution")
    command: str = Field(description="Command that was executed")

    @property
    def success(self) -> bool:
        """True if execution completed successfully."""
        return self.exit_code == 0 and not self.timeout_occurred


class ContainerInfo(BaseModel):
    """Information about a Docker container."""

    id: str = Field(description="Container ID")
    name: str = Field(description="Container name")
    image: str = Field(description="Container image")
    status: str = Field(description="Container status")
    created: str = Field(description="Container creation time")
