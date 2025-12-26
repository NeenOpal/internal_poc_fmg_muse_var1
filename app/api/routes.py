import time
import structlog
import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.models.email import (
    EmailGenerationRequest,
    EmailGenerationResponse,
    EmailRefineRequest,
    EmailRefineResponse,
    EmailEvaluationRequest,
    EmailEvaluationResponse,
    MetricScoreResponse,
    ErrorResponse,
)
from app.services.llm_service import get_llm_service
from app.services.email_pipeline import get_email_pipeline
from app.evaluation.evaluation_service import get_evaluation_service
from app.evaluation.test_cases import get_all_test_cases, get_test_case_by_id
from app.evaluation.metrics import EVALUATION_CRITERIA
from app.config import get_settings


logger = structlog.get_logger()

router = APIRouter(prefix="/api", tags=["email"])

# All supported models (backend - kept for future use)
# Pricing per 1M tokens (input/output) from OpenRouter
POPULAR_MODELS = [
    {"id": "openai/gpt-5-nano", "name": "GPT-5 Nano", "provider": "OpenAI", "input_cost": 0.10, "output_cost": 0.40},
    {"id": "meta-llama/llama-3.1-8b-instruct", "name": "Llama 3.1 8B (AWS Bedrock)", "provider": "Meta", "input_cost": 0.02, "output_cost": 0.03},
    {"id": "openai/gpt-4o", "name": "GPT-4o", "provider": "OpenAI", "input_cost": 2.50, "output_cost": 10.0},
    {"id": "openai/gpt-4o-mini", "name": "GPT-4o Mini", "provider": "OpenAI", "input_cost": 0.15, "output_cost": 0.60},
    {"id": "anthropic/claude-opus-4.5", "name": "Claude Opus 4.5", "provider": "Anthropic", "input_cost": 15.0, "output_cost": 75.0},
    {"id": "anthropic/claude-3.5-sonnet", "name": "Claude 3.5 Sonnet", "provider": "Anthropic", "input_cost": 3.0, "output_cost": 15.0},
    {"id": "anthropic/claude-3.5-haiku", "name": "Claude 3.5 Haiku", "provider": "Anthropic", "input_cost": 0.80, "output_cost": 4.0},
    {"id": "amazon/nova-micro-v1", "name": "Amazon Nova Micro", "provider": "Amazon", "input_cost": 0.035, "output_cost": 0.14},
]

# Models visible in UI dropdown (subset of POPULAR_MODELS)
UI_VISIBLE_MODELS = [
    {"id": "openai/gpt-4o", "name": "OpenAI", "provider": "OpenAI", "input_cost": 2.50, "output_cost": 10.0},
    {"id": "meta-llama/llama-3.1-8b-instruct", "name": "Bedrock", "provider": "Meta", "input_cost": 0.02, "output_cost": 0.03},
]

# Model pricing lookup (cost per 1M tokens)
MODEL_PRICING = {model["id"]: {"input": model["input_cost"], "output": model["output_cost"]} for model in POPULAR_MODELS}


@router.post(
    "/generate-email",
    response_model=EmailGenerationResponse,
    responses={
        500: {"model": ErrorResponse, "description": "LLM service error"},
        503: {"model": ErrorResponse, "description": "Service unavailable"},
    },
    summary="Generate an email",
    description="Generate a professional email with automatic quality evaluation and compliance checking.",
)
async def generate_email(request: EmailGenerationRequest) -> EmailGenerationResponse:
    """
    Generate an email with full quality pipeline:
    1. Generate initial email with compliance rules
    2. Evaluate against 10 quality metrics
    3. Auto-refine if below threshold or compliance issues detected
    4. Return final compliant email
    """
    start_time = time.time()

    logger.info(
        "Email generation request received (quality pipeline)",
        purpose=request.purpose.value,
        length=request.length.value,
        tone=request.tone.value if request.tone else None,
        model=request.model,
        details_length=len(request.details),
    )

    try:
        pipeline = get_email_pipeline()
        response = await pipeline.generate_with_quality_check(
            purpose=request.purpose,
            details=request.details,
            length=request.length,
            tone=request.tone,
            model=request.model,
            history=request.history,
        )

        duration = time.time() - start_time
        logger.info(
            "Email generated successfully (quality pipeline)",
            duration_seconds=round(duration, 2),
            total_cost=response.usage.cost if response.usage else 0,
        )

        return response

    except Exception as e:
        logger.error("Email generation failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate email: {str(e)}"
        )


@router.post(
    "/generate-email/quality",
    response_model=EmailGenerationResponse,
    responses={
        500: {"model": ErrorResponse, "description": "Pipeline error"},
    },
    summary="Generate email with quality assurance",
    description="Generate an email with automatic evaluation and refinement. Returns the final polished email.",
)
async def generate_email_with_quality(request: EmailGenerationRequest) -> EmailGenerationResponse:
    """
    Generate an email with full quality pipeline:
    1. Generate initial email
    2. Evaluate against 10 quality metrics (compliance, tone, structure, etc.)
    3. Auto-refine if score below threshold or compliance issues detected
    4. Return final polished email

    The evaluation and refinement happen behind the scenes.
    User only receives the final quality-checked email.
    """
    start_time = time.time()

    logger.info(
        "Quality pipeline request received",
        purpose=request.purpose.value,
        length=request.length.value,
        tone=request.tone.value if request.tone else None,
        model=request.model,
    )

    try:
        pipeline = get_email_pipeline()
        response = await pipeline.generate_with_quality_check(
            purpose=request.purpose,
            details=request.details,
            length=request.length,
            tone=request.tone,
            model=request.model,
            history=request.history,
        )

        duration = time.time() - start_time
        logger.info(
            "Quality pipeline completed",
            duration_seconds=round(duration, 2),
            total_cost=response.usage.cost if response.usage else 0,
        )

        return response

    except Exception as e:
        logger.error("Quality pipeline failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate quality-checked email: {str(e)}"
        )


@router.post(
    "/refine-email",
    response_model=EmailRefineResponse,
    responses={
        500: {"model": ErrorResponse, "description": "LLM service error"},
        503: {"model": ErrorResponse, "description": "Service unavailable"},
    },
    summary="Refine an existing email",
    description="Refine an existing email based on user feedback.",
)
async def refine_email(request: EmailRefineRequest) -> EmailRefineResponse:
    """
    Refine an existing email based on user feedback.
    """
    start_time = time.time()

    logger.info(
        "Email refinement request received",
        feedback_length=len(request.feedback),
        original_subject_length=len(request.original_subject),
    )

    try:
        llm_service = get_llm_service()
        response = await llm_service.refine_email(
            original_subject=request.original_subject,
            original_body=request.original_body,
            feedback=request.feedback,
            model=request.model,
            history=request.history,
        )

        duration = time.time() - start_time
        logger.info("Email refined successfully", duration_seconds=round(duration, 2))

        return response

    except Exception as e:
        logger.error("Email refinement failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to refine email: {str(e)}"
        )


@router.post(
    "/generate-email/stream",
    summary="Generate an email with streaming",
    description="Generate a professional email with real-time streaming output.",
)
async def generate_email_stream(request: EmailGenerationRequest):
    """
    Generate an email with streaming response for real-time output.
    """
    logger.info(
        "Streaming email generation request received",
        purpose=request.purpose.value,
        length=request.length.value,
        tone=request.tone.value if request.tone else None,
        model=request.model,
    )

    async def event_generator():
        try:
            llm_service = get_llm_service()
            async for chunk in llm_service.generate_email_stream(
                purpose=request.purpose,
                details=request.details,
                length=request.length,
                tone=request.tone,
                model=request.model,
                history=request.history,
            ):
                # Send each chunk as SSE data
                yield f"data: {chunk}\n\n"
            # Signal completion
            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.error("Streaming email generation failed", error=str(e))
            yield f"data: [ERROR] {str(e)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.post(
    "/refine-email/stream",
    summary="Refine an email with streaming",
    description="Refine an existing email with real-time streaming output.",
)
async def refine_email_stream(request: EmailRefineRequest):
    """
    Refine an email with streaming response for real-time output.
    """
    logger.info(
        "Streaming email refinement request received",
        feedback_length=len(request.feedback),
    )

    async def event_generator():
        try:
            llm_service = get_llm_service()
            async for chunk in llm_service.refine_email_stream(
                original_subject=request.original_subject,
                original_body=request.original_body,
                feedback=request.feedback,
                model=request.model,
                history=request.history,
            ):
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.error("Streaming email refinement failed", error=str(e))
            yield f"data: [ERROR] {str(e)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.get(
    "/health",
    summary="Health check",
    description="Check if the API is running.",
)
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy", "service": "fmg-muse"}


@router.get(
    "/models",
    summary="Get available models",
    description="Get a list of AI models available for email generation.",
)
async def get_models():
    """
    Get the list of models visible in the UI dropdown.
    """
    return {
        "models": UI_VISIBLE_MODELS,
        "default": "openai/gpt-4o"
    }


@router.get(
    "/models/all",
    summary="Get all OpenRouter models",
    description="Fetch all available models from OpenRouter API.",
)
async def get_all_models():
    """
    Fetch all available models from OpenRouter API dynamically.
    """
    settings = get_settings()

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{settings.openrouter_base_url}/models",
                headers={
                    "Authorization": f"Bearer {settings.openrouter_api_key}",
                    "Content-Type": "application/json",
                }
            )

            if response.status_code != 200:
                logger.warning("Failed to fetch models from OpenRouter, using fallback list")
                return {
                    "models": POPULAR_MODELS,
                    "default": settings.openrouter_model,
                    "source": "fallback"
                }

            data = response.json()
            models = []
            for model in data.get("data", []):
                model_id = model.get("id", "")
                models.append({
                    "id": model_id,
                    "name": model.get("name", model_id),
                    "provider": model_id.split("/")[0].title() if "/" in model_id else "Unknown"
                })

            return {
                "models": models,
                "default": settings.openrouter_model,
                "source": "openrouter"
            }

    except Exception as e:
        logger.error("Error fetching models from OpenRouter", error=str(e))
        return {
            "models": POPULAR_MODELS,
            "default": settings.openrouter_model,
            "source": "fallback"
        }


# ============== Evaluation Endpoints ==============

@router.post(
    "/evaluate-email",
    response_model=EmailEvaluationResponse,
    responses={
        500: {"model": ErrorResponse, "description": "Evaluation service error"},
    },
    summary="Evaluate an email",
    description="Evaluate a generated email against quality and compliance metrics.",
)
async def evaluate_email(request: EmailEvaluationRequest) -> EmailEvaluationResponse:
    """
    Evaluate a generated email and return detailed quality metrics.

    Returns scores (1-10) for:
    - Compliance: FINRA/SEC regulatory compliance
    - Tone Consistency: Match between requested and actual tone
    - Length Accuracy: Adherence to target word count
    - Structure: Proper email structure
    - Purpose Alignment: Achievement of stated purpose
    - Clarity: Clear, readable language
    - Professionalism: Appropriate for financial communications
    - Personalization: Proper use of placeholders
    - Risk Balance: Balanced benefit/risk presentation
    - Disclaimer Accuracy: Appropriate disclaimers present
    """
    start_time = time.time()

    logger.info(
        "Email evaluation request received",
        purpose=request.purpose.value,
        tone=request.tone.value,
        length=request.length.value,
        subject_length=len(request.subject),
    )

    try:
        eval_service = get_evaluation_service()
        metrics = await eval_service.evaluate_email(
            email_subject=request.subject,
            email_body=request.body,
            purpose=request.purpose,
            tone=request.tone,
            length=request.length,
            original_request=request.original_request,
            model=request.model,
        )

        duration = time.time() - start_time
        logger.info(
            "Email evaluation completed",
            duration_seconds=round(duration, 2),
            overall_score=metrics.overall_score,
            pass_threshold=metrics.pass_threshold,
        )

        # Convert to response model
        return EmailEvaluationResponse(
            compliance=MetricScoreResponse(
                score=metrics.compliance.score,
                justification=metrics.compliance.justification,
                suggestions=metrics.compliance.suggestions,
            ),
            tone_consistency=MetricScoreResponse(
                score=metrics.tone_consistency.score,
                justification=metrics.tone_consistency.justification,
                suggestions=metrics.tone_consistency.suggestions,
            ),
            length_accuracy=MetricScoreResponse(
                score=metrics.length_accuracy.score,
                justification=metrics.length_accuracy.justification,
                suggestions=metrics.length_accuracy.suggestions,
            ),
            structure_completeness=MetricScoreResponse(
                score=metrics.structure_completeness.score,
                justification=metrics.structure_completeness.justification,
                suggestions=metrics.structure_completeness.suggestions,
            ),
            purpose_alignment=MetricScoreResponse(
                score=metrics.purpose_alignment.score,
                justification=metrics.purpose_alignment.justification,
                suggestions=metrics.purpose_alignment.suggestions,
            ),
            clarity=MetricScoreResponse(
                score=metrics.clarity.score,
                justification=metrics.clarity.justification,
                suggestions=metrics.clarity.suggestions,
            ),
            professionalism=MetricScoreResponse(
                score=metrics.professionalism.score,
                justification=metrics.professionalism.justification,
                suggestions=metrics.professionalism.suggestions,
            ),
            personalization=MetricScoreResponse(
                score=metrics.personalization.score,
                justification=metrics.personalization.justification,
                suggestions=metrics.personalization.suggestions,
            ),
            risk_balance=MetricScoreResponse(
                score=metrics.risk_balance.score,
                justification=metrics.risk_balance.justification,
                suggestions=metrics.risk_balance.suggestions,
            ),
            disclaimer_accuracy=MetricScoreResponse(
                score=metrics.disclaimer_accuracy.score,
                justification=metrics.disclaimer_accuracy.justification,
                suggestions=metrics.disclaimer_accuracy.suggestions,
            ),
            overall_score=metrics.overall_score,
            pass_threshold=metrics.pass_threshold,
            strengths=metrics.strengths,
            improvements_needed=metrics.improvements_needed,
            rewrite_recommended=metrics.rewrite_recommended,
        )

    except Exception as e:
        logger.error("Email evaluation failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to evaluate email: {str(e)}"
        )


@router.get(
    "/evaluation/test-cases",
    summary="Get evaluation test cases",
    description="Get all ideal test case emails for reference.",
)
async def get_test_cases():
    """
    Get all ideal test case emails that serve as reference examples.
    """
    test_cases = get_all_test_cases()
    return {
        "count": len(test_cases),
        "test_cases": [
            {
                "id": tc["id"],
                "purpose": tc["purpose"].value,
                "tone": tc["tone"].value,
                "length": tc["length"].value,
                "input_details": tc["input_details"],
                "ideal_email": tc["ideal_email"],
                "evaluation_notes": tc["evaluation_notes"],
            }
            for tc in test_cases
        ]
    }


@router.get(
    "/evaluation/test-cases/{case_id}",
    summary="Get specific test case",
    description="Get a specific test case by ID.",
)
async def get_test_case(case_id: str):
    """
    Get a specific test case by its ID.
    """
    test_case = get_test_case_by_id(case_id)
    if not test_case:
        raise HTTPException(status_code=404, detail=f"Test case {case_id} not found")

    return {
        "id": test_case["id"],
        "purpose": test_case["purpose"].value,
        "tone": test_case["tone"].value,
        "length": test_case["length"].value,
        "input_details": test_case["input_details"],
        "ideal_email": test_case["ideal_email"],
        "evaluation_notes": test_case["evaluation_notes"],
    }


@router.get(
    "/evaluation/metrics",
    summary="Get evaluation metrics criteria",
    description="Get the evaluation criteria and scoring rubric.",
)
async def get_evaluation_metrics():
    """
    Get the evaluation criteria, weights, and scoring guides.
    """
    return {
        "metrics": {
            name: {
                "name": criteria["name"],
                "weight": criteria["weight"],
                "description": criteria["description"],
                "scoring_guide": criteria["scoring_guide"],
            }
            for name, criteria in EVALUATION_CRITERIA.items()
        },
        "pass_threshold": 7.0,
        "total_weight": sum(c["weight"] for c in EVALUATION_CRITERIA.values()),
    }
