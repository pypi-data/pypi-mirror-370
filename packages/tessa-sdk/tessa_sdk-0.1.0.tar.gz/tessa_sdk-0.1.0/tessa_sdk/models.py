"""Data models and types for the Tessa SDK."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict


class ActionSelectionModel(str, Enum):
    """Available AI models for action selection."""
    
    CLAUDE_SONNET = "claude-sonnet-4-20250514"
    GEMINI_FLASH = "gemini/gemini-2.5-flash"
    GPT_4O = "gpt-4o"
    
    @classmethod
    def default(cls) -> "ActionSelectionModel":
        """Get the default model."""
        return cls.CLAUDE_SONNET


class JobStatusEnum(str, Enum):
    """Job status values."""
    
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    USER_TAKEN_OVER = "user_taken_over"


class BrowserConfig(BaseModel):
    """Browser configuration options."""
    
    model_config = ConfigDict(extra="forbid")
    
    width: int = Field(default=1920, ge=320, le=4096, description="Browser viewport width")
    height: int = Field(default=1080, ge=320, le=4096, description="Browser viewport height")
    residential_ip: bool = Field(default=False, description="Use residential IP proxy")
    max_duration_minutes: int = Field(
        default=30, ge=1, le=240, description="Maximum session duration in minutes"
    )
    idle_timeout_minutes: int = Field(
        default=2, ge=1, le=60, description="Idle timeout in minutes"
    )


class RunBrowserAgentRequest(BaseModel):
    """Request model for running a browser agent."""
    
    directive: str = Field(..., description="Natural language instruction for the browser agent")
    initial_url: Optional[str] = Field(
        None, description="Starting URL for the browser session"
    )
    cdp_url: Optional[str] = Field(
        None, description="Chrome DevTools Protocol URL for custom browser"
    )
    live_url: Optional[str] = Field(
        None, description="Live view URL for custom browser session"
    )
    action_selection_model: ActionSelectionModel = Field(
        default=ActionSelectionModel.CLAUDE_SONNET,
        description="AI model for action selection"
    )
    browser_config: Optional[BrowserConfig] = Field(
        None, description="Browser configuration options"
    )


class RunBrowserAgentResponse(BaseModel):
    """Response model for starting a browser agent."""
    
    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatusEnum = Field(..., description="Initial job status")
    live_url: Optional[str] = Field(None, description="Direct link to watch live session")
    cdp_url: Optional[str] = Field(None, description="Chrome DevTools Protocol URL")
    history_url: str = Field(..., description="Link to view session history and logs")
    polling_url: str = Field(..., description="API endpoint to poll for status")


class JobStatus(BaseModel):
    """Job status information."""
    
    job_id: str = Field(..., description="Unique job identifier")
    user_id: str = Field(..., description="User who owns this job")
    directive: Optional[str] = Field(None, description="Original instruction")
    status: JobStatusEnum = Field(..., description="Current job status")
    output: Optional[Dict[str, Any]] = Field(None, description="Final output data")
    error: Optional[str] = Field(None, description="Error message if job failed")
    live_url: Optional[str] = Field(None, description="Direct link to watch live session")
    cdp_url: Optional[str] = Field(None, description="Chrome DevTools Protocol URL")
    history_url: Optional[str] = Field(None, description="Link to view session history")
    credits_used: Optional[int] = Field(None, description="Credits consumed by this job")
    credit_balance: Optional[int] = Field(None, description="Current credit balance")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last updated timestamp")


class JobResult(BaseModel):
    """Final result of a completed job."""
    
    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatusEnum = Field(..., description="Final job status")
    output: Optional[Dict[str, Any]] = Field(None, description="Extracted data or results")
    error: Optional[str] = Field(None, description="Error message if job failed")
    credits_used: int = Field(..., description="Total credits consumed")
    duration_seconds: Optional[float] = Field(None, description="Job duration in seconds")
    
    @property
    def is_successful(self) -> bool:
        """Check if the job completed successfully."""
        return self.status == JobStatusEnum.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if the job failed."""
        return self.status == JobStatusEnum.FAILED
    
    def get_output(self, key: Optional[str] = None) -> Any:
        """Get output data, optionally by key."""
        if not self.output:
            return None
        if key:
            return self.output.get(key)
        return self.output
