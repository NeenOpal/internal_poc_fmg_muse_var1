from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class PurposeEnum(str, Enum):
    RELATIONSHIP_BUILDER = "relationship_builder"
    EDUCATIONAL_CONTENT = "educational_content"
    FOLLOW_UP = "follow_up"
    FEEDBACK_REQUEST = "feedback_request"
    SCHEDULING = "scheduling"
    OTHER = "other"


class LengthEnum(str, Enum):
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"


class ToneEnum(str, Enum):
    PROFESSIONAL = "professional"
    FORMAL = "formal"
    FRIENDLY = "friendly"
    CASUAL = "casual"


class ChatMessage(BaseModel):
    """Represents a single message in the conversation history."""
    role: str = Field(..., description="Role of the message sender: 'user' or 'assistant'")
    content: str = Field(..., description="The message content")
    email_subject: Optional[str] = Field(None, description="Email subject if this is an email response")
    email_body: Optional[str] = Field(None, description="Email body if this is an email response")


class EmailGenerationRequest(BaseModel):
    purpose: PurposeEnum = Field(..., description="The purpose of the email")
    details: str = Field(
        ...,
        min_length=3,
        max_length=2000,
        description="Details and context for the email (can be brief keywords or full description)"
    )
    length: LengthEnum = Field(..., description="Desired email length")
    tone: ToneEnum = Field(default=ToneEnum.PROFESSIONAL, description="Desired writing tone")
    model: Optional[str] = Field(default=None, description="Model to use for generation (uses default if not specified)")
    history: list[ChatMessage] = Field(default=[], description="Conversation history for context")


class UsageInfo(BaseModel):
    """Token usage and cost information."""
    prompt_tokens: int = Field(0, description="Number of input tokens used")
    completion_tokens: int = Field(0, description="Number of output tokens used")
    total_tokens: int = Field(0, description="Total tokens used")
    cost: float = Field(0.0, description="Cost in USD for this request")


class EmailGenerationResponse(BaseModel):
    subject: str = Field(..., description="Generated email subject line")
    body: str = Field(..., description="Generated email body")
    usage: Optional[UsageInfo] = Field(None, description="Token usage and cost information")


class EmailRefineRequest(BaseModel):
    original_subject: str = Field(..., description="Original email subject")
    original_body: str = Field(..., description="Original email body")
    feedback: str = Field(
        ...,
        min_length=5,
        description="User feedback for refinement"
    )
    model: Optional[str] = Field(default=None, description="Model to use for refinement (uses default if not specified)")
    history: list[ChatMessage] = Field(default=[], description="Conversation history for context")


class EmailRefineResponse(BaseModel):
    subject: str = Field(..., description="Refined email subject line")
    body: str = Field(..., description="Refined email body")
    usage: Optional[UsageInfo] = Field(None, description="Token usage and cost information")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    detail: str | None = Field(None, description="Additional error details")


class EmailEvaluationRequest(BaseModel):
    """Request to evaluate a generated email."""
    subject: str = Field(..., description="Email subject to evaluate")
    body: str = Field(..., description="Email body to evaluate")
    purpose: PurposeEnum = Field(..., description="Original purpose of the email")
    tone: ToneEnum = Field(default=ToneEnum.PROFESSIONAL, description="Requested tone")
    length: LengthEnum = Field(..., description="Requested length")
    original_request: str = Field(..., description="Original user input/details")
    model: Optional[str] = Field(default=None, description="Model to use for evaluation")


class MetricScoreResponse(BaseModel):
    """Individual metric score in response."""
    score: int = Field(..., ge=1, le=10, description="Score from 1-10")
    justification: str = Field(..., description="Explanation for the score")
    suggestions: Optional[str] = Field(None, description="Improvement suggestions")


class EmailEvaluationResponse(BaseModel):
    """Response containing full email evaluation."""
    # Core metrics
    compliance: MetricScoreResponse
    tone_consistency: MetricScoreResponse
    length_accuracy: MetricScoreResponse
    structure_completeness: MetricScoreResponse
    purpose_alignment: MetricScoreResponse
    clarity: MetricScoreResponse
    professionalism: MetricScoreResponse
    personalization: MetricScoreResponse
    risk_balance: MetricScoreResponse
    disclaimer_accuracy: MetricScoreResponse

    # Aggregates
    overall_score: float = Field(..., description="Weighted average score (0-10)")
    pass_threshold: bool = Field(..., description="Whether email meets quality bar (7.0+)")

    # Summary
    strengths: list[str] = Field(default=[], description="Key strengths")
    improvements_needed: list[str] = Field(default=[], description="Priority improvements")
    rewrite_recommended: bool = Field(False, description="Whether rewrite is recommended")

    # Usage info
    usage: Optional[UsageInfo] = Field(None, description="Token usage for evaluation")
