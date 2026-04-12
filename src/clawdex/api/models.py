"""
Pydantic models for the Clawdex REST API.

Request and response models for all API endpoints.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# =============================================================================
# Solution Models
# =============================================================================


class SolutionSearchRequest(BaseModel):
    """Request body for searching solutions."""
    error_message: str = Field(..., description="The error message to search for")
    language: Optional[str] = Field(None, description="Programming language filter")
    framework: Optional[str] = Field(None, description="Framework filter")
    database: Optional[str] = Field(None, description="Database filter")
    platform: Optional[str] = Field(None, description="Platform filter")
    category: Optional[str] = Field(None, description="Category filter")
    limit: int = Field(5, ge=1, le=50, description="Maximum number of results")


class SolutionResult(BaseModel):
    """A single solution result."""
    id: str
    solution: str
    original_error: str
    context: Dict[str, Any] = Field(default_factory=dict)
    confidence: float
    verified: bool
    source: str = "local"


class SolutionSearchResponse(BaseModel):
    """Response for solution search."""
    found: bool
    message: str
    solutions: List[SolutionResult] = Field(default_factory=list)
    source: str = "local"
    suggestion: Optional[str] = None


class SolutionLogRequest(BaseModel):
    """Request body for logging a solution."""
    error_message: str = Field(..., description="The error message that was encountered")
    solution: str = Field(..., description="Description of how the error was fixed")
    error_type: Optional[str] = Field(None, description="Type of error")
    stack_trace: Optional[str] = Field(None, description="Full stack trace")
    file: Optional[str] = Field(None, description="File where error occurred")
    line: Optional[int] = Field(None, description="Line number")
    code_change: Optional[str] = Field(None, description="Code change made")
    files_modified: Optional[List[str]] = Field(None, description="Files modified")
    project: Optional[str] = Field(None, description="Project name")
    language: Optional[str] = Field(None, description="Programming language")
    framework: Optional[str] = Field(None, description="Framework")
    database: Optional[str] = Field(None, description="Database")
    platform: Optional[str] = Field(None, description="Platform")
    category: Optional[str] = Field(None, description="Category")
    time_to_solve: Optional[str] = Field(None, description="Time to solve")
    verified: bool = Field(False, description="Whether solution is verified")


class SolutionLogResponse(BaseModel):
    """Response for logging a solution."""
    id: str
    success: bool
    message: str
    secrets_redacted: bool = False


class SolutionVerifyRequest(BaseModel):
    """Request body for verifying a solution."""
    id: str = Field(..., description="Solution record ID")
    success: bool = Field(..., description="Whether the solution worked")


class SolutionVerifyResponse(BaseModel):
    """Response for verifying a solution."""
    success: bool
    record_id: str
    verified: bool
    contributed_to_community: bool = False
    message: str


# =============================================================================
# Decision Models
# =============================================================================


class DecisionSearchRequest(BaseModel):
    """Request body for searching decisions."""
    topic: str = Field(..., description="Topic to search for")
    project: Optional[str] = Field(None, description="Project filter")
    component: Optional[str] = Field(None, description="Component filter")
    limit: int = Field(5, ge=1, le=50, description="Maximum number of results")


class DecisionResult(BaseModel):
    """A single decision result."""
    id: str
    title: str
    choice: str
    relevance: float


class DecisionSearchResponse(BaseModel):
    """Response for decision search."""
    found: bool
    message: str
    decisions: List[DecisionResult] = Field(default_factory=list)
    suggestion: Optional[str] = None


class DecisionLogRequest(BaseModel):
    """Request body for logging a decision."""
    title: str = Field(..., description="Short title for the decision")
    choice: str = Field(..., description="What was chosen")
    alternatives: Optional[List[str]] = Field(None, description="Other options considered")
    pros: Optional[List[str]] = Field(None, description="Advantages")
    cons: Optional[List[str]] = Field(None, description="Disadvantages")
    deciding_factor: Optional[str] = Field(None, description="Main reason for choice")
    project: Optional[str] = Field(None, description="Project name")
    component: Optional[str] = Field(None, description="Component affected")
    language: Optional[str] = Field(None, description="Programming language")
    framework: Optional[str] = Field(None, description="Framework")


class DecisionLogResponse(BaseModel):
    """Response for logging a decision."""
    id: str
    success: bool
    message: str


# =============================================================================
# Pattern Models
# =============================================================================


class PatternSearchRequest(BaseModel):
    """Request body for searching patterns."""
    problem: str = Field(..., description="Problem to search for")
    category: Optional[str] = Field(None, description="Category filter")
    language: Optional[str] = Field(None, description="Language filter")
    framework: Optional[str] = Field(None, description="Framework filter")
    limit: int = Field(5, ge=1, le=50, description="Maximum number of results")


class PatternResult(BaseModel):
    """A single pattern result."""
    id: str
    name: str
    category: str
    problem: str
    solution: str
    relevance: float


class PatternSearchResponse(BaseModel):
    """Response for pattern search."""
    found: bool
    message: str
    patterns: List[PatternResult] = Field(default_factory=list)
    suggestion: Optional[str] = None


class PatternLogRequest(BaseModel):
    """Request body for logging a pattern."""
    name: str = Field(..., description="Name for this pattern")
    category: str = Field(..., description="Category")
    problem: str = Field(..., description="Problem this pattern solves")
    solution: str = Field(..., description="How the pattern solves it")
    languages: Optional[List[str]] = Field(None, description="Applicable languages")
    frameworks: Optional[List[str]] = Field(None, description="Applicable frameworks")
    databases: Optional[List[str]] = Field(None, description="Applicable databases")
    scenarios: Optional[List[str]] = Field(None, description="Usage scenarios")
    before_code: Optional[str] = Field(None, description="Code before pattern")
    after_code: Optional[str] = Field(None, description="Code after pattern")
    explanation: Optional[str] = Field(None, description="Detailed explanation")


class PatternLogResponse(BaseModel):
    """Response for logging a pattern."""
    id: str
    success: bool
    message: str


# =============================================================================
# Stats & Health Models
# =============================================================================


class StatsResponse(BaseModel):
    """Response for stats endpoint."""
    total_records: int
    error_fixes: int
    decisions: int
    patterns: int
    data_directory: str


class HealthResponse(BaseModel):
    """Response for health check."""
    status: str
    version: str
    storage_available: bool = True


# =============================================================================
# Error Models
# =============================================================================


class ErrorResponse(BaseModel):
    """Standard error response."""
    detail: str
    error_code: Optional[str] = None
