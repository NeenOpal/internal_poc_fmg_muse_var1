import structlog
import httpx
import json
import asyncio
from typing import Optional, AsyncGenerator

from app.models.email import (
    PurposeEnum,
    LengthEnum,
    ToneEnum,
    EmailGenerationResponse,
    EmailRefineResponse,
    ChatMessage,
    UsageInfo,
)
from app.config import get_settings
from app.services.prompt_service import (
    SYSTEM_PROMPT,
    construct_generation_prompt,
    construct_refinement_prompt,
    parse_llm_response,
)


logger = structlog.get_logger()


class EmptyResponseError(Exception):
    """Raised when the LLM returns an empty response."""
    pass


class OpenRouterLLMService:
    """LLM service optimized for GPT-5 Nano via OpenRouter API."""

    def __init__(self):
        settings = get_settings()
        self.api_key = settings.openrouter_api_key
        self.base_url = settings.openrouter_base_url
        self.model = settings.openrouter_model

        if not self.api_key:
            raise ValueError(
                "OpenRouter API key not configured. "
                "Set OPENROUTER_API_KEY in your .env file."
            )

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://fmg-muse.local",
            "X-Title": "FMG Muse Email Assistant",
        }

    async def _call_openrouter_with_retry(self, messages: list[dict], model: str = None, attempt: int = 1) -> tuple[str, dict]:
        """Make an async call to OpenRouter API with retry logic. Returns (content, usage_info)."""
        max_attempts = 3
        effective_model = model or self.model

        # Optimized parameters - reasoning disabled for faster responses
        payload = {
            "model": effective_model,
            "messages": messages,
            "temperature": 0.3,  # Lower temperature for deterministic, compliance-focused output
            "max_tokens": 2000,  # Sufficient for email generation without reasoning overhead
            "top_p": 0.9,
        }

        # Minimize reasoning for GPT-5 models to speed up responses
        # Note: GPT-5-nano only supports 'minimal', 'low', 'medium', 'high' (not 'none')
        if "gpt-5" in effective_model.lower():
            payload["reasoning"] = {"effort": "minimal"}

        try:
            # Timeout for API calls (reduced since reasoning is disabled)
            timeout = 60.0

            async with httpx.AsyncClient(timeout=timeout) as client:
                logger.info(
                    "Calling OpenRouter API",
                    model=effective_model,
                    attempt=attempt,
                    max_attempts=max_attempts,
                    temperature=payload["temperature"],
                    reasoning_disabled="gpt-5" in effective_model.lower(),
                )

                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                )

                if response.status_code != 200:
                    error_detail = response.text
                    logger.error(
                        "OpenRouter API error",
                        status_code=response.status_code,
                        error=error_detail,
                        attempt=attempt,
                    )
                    raise Exception(f"OpenRouter API error: {response.status_code} - {error_detail}")

                result = response.json()

                # Debug: Log full response structure
                logger.info(
                    "OpenRouter raw response",
                    response_keys=list(result.keys()) if isinstance(result, dict) else "not_dict",
                    full_response=str(result)[:500],  # First 500 chars
                )

                # Check if response has expected structure
                if "choices" not in result or not result["choices"]:
                    logger.error("OpenRouter response missing 'choices'", response=result)
                    raise EmptyResponseError("Invalid response structure - no choices")

                content = result["choices"][0].get("message", {}).get("content", "")

                # Extract usage information
                usage = result.get("usage", {})
                usage_info = {
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0),
                }

                # Check for empty response
                if not content or not content.strip():
                    logger.warning(
                        "OpenRouter returned empty response",
                        model=effective_model,
                        attempt=attempt,
                    )
                    raise EmptyResponseError("LLM returned empty response")

                return content, usage_info

        except (httpx.TimeoutException, httpx.ConnectError) as e:
            logger.warning(
                "OpenRouter API timeout/connection error",
                error=str(e),
                attempt=attempt,
            )
            raise EmptyResponseError(f"API timeout: {str(e)}")

    async def _call_openrouter(self, messages: list[dict], model: str = None) -> tuple[str, dict]:
        """Make an async call to OpenRouter API with automatic retries. Returns (content, usage_info)."""
        max_attempts = 3
        last_error = None

        for attempt in range(1, max_attempts + 1):
            try:
                return await self._call_openrouter_with_retry(messages, model, attempt)
            except EmptyResponseError as e:
                last_error = e
                if attempt < max_attempts:
                    wait_time = 2 ** attempt  # Exponential backoff: 2, 4, 8 seconds
                    logger.info(
                        "Retrying after empty/timeout response",
                        attempt=attempt,
                        wait_seconds=wait_time,
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(
                        "All retry attempts exhausted",
                        total_attempts=max_attempts,
                    )

        # If all retries failed, raise the last error
        raise last_error or EmptyResponseError("Failed after all retry attempts")

    def _calculate_cost(self, usage_info: dict, model: str) -> float:
        """Calculate cost in USD based on token usage and model pricing."""
        from app.api.routes import MODEL_PRICING

        pricing = MODEL_PRICING.get(model, {"input": 0.10, "output": 0.40})  # Default to GPT-5 Nano pricing

        prompt_tokens = usage_info.get("prompt_tokens", 0)
        completion_tokens = usage_info.get("completion_tokens", 0)

        # Cost per 1M tokens, so divide by 1,000,000
        input_cost = (prompt_tokens / 1_000_000) * pricing["input"]
        output_cost = (completion_tokens / 1_000_000) * pricing["output"]

        return round(input_cost + output_cost, 6)

    async def _stream_openrouter(
        self, messages: list[dict], model: str = None
    ) -> AsyncGenerator[str, None]:
        """Stream response from OpenRouter API."""
        effective_model = model or self.model

        # Optimized streaming parameters - reasoning disabled for faster responses
        payload = {
            "model": effective_model,
            "messages": messages,
            "temperature": 0.3,  # Lower temperature for deterministic, compliance-focused output
            "max_tokens": 2000,  # Sufficient for email generation
            "top_p": 0.9,
            "stream": True,
        }

        # Minimize reasoning for GPT-5 models to speed up responses
        # Note: GPT-5-nano only supports 'minimal', 'low', 'medium', 'high' (not 'none')
        if "gpt-5" in effective_model.lower():
            payload["reasoning"] = {"effort": "minimal"}

        logger.info(
            "Starting streaming request to OpenRouter",
            model=effective_model,
            temperature=payload["temperature"],
        )

        # Timeout for streaming
        timeout = 60.0

        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
            ) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    logger.error(
                        "OpenRouter streaming API error",
                        status_code=response.status_code,
                        error=error_text.decode(),
                    )
                    raise Exception(f"OpenRouter API error: {response.status_code}")

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]  # Remove "data: " prefix
                        if data == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                            if chunk["choices"] and chunk["choices"][0].get("delta", {}).get("content"):
                                content = chunk["choices"][0]["delta"]["content"]
                                yield content
                        except json.JSONDecodeError:
                            continue

    async def generate_email_stream(
        self,
        purpose: PurposeEnum,
        details: str,
        length: LengthEnum,
        tone: ToneEnum = None,
        model: str = None,
        history: Optional[list[ChatMessage]] = None,
    ) -> AsyncGenerator[str, None]:
        """Generate an email using streaming for real-time output."""
        history = history or []
        effective_model = model or self.model

        logger.info(
            "Generating email via streaming (GPT-5 Nano optimized)",
            purpose=purpose.value,
            length=length.value,
            tone=tone.value if tone else None,
            model=effective_model,
        )

        # Construct the explicit prompt
        user_prompt = construct_generation_prompt(purpose, details, length, tone)

        # Build messages with history
        messages = self._build_conversation_messages(history, user_prompt)

        # Stream the response
        async for chunk in self._stream_openrouter(messages, effective_model):
            yield chunk

    async def refine_email_stream(
        self,
        original_subject: str,
        original_body: str,
        feedback: str,
        model: str = None,
        history: Optional[list[ChatMessage]] = None,
    ) -> AsyncGenerator[str, None]:
        """Refine an email using streaming for real-time output."""
        history = history or []
        effective_model = model or self.model

        logger.info(
            "Refining email via streaming (GPT-5 Nano optimized)",
            feedback_preview=feedback[:50] if len(feedback) > 50 else feedback,
            model=effective_model,
        )

        # Construct the explicit refinement prompt
        user_prompt = construct_refinement_prompt(original_subject, original_body, feedback)

        # Build messages with history
        messages = self._build_conversation_messages(history, user_prompt)

        # Stream the response
        async for chunk in self._stream_openrouter(messages, effective_model):
            yield chunk

    def _build_conversation_messages(
        self, history: list[ChatMessage], user_prompt: str
    ) -> list[dict]:
        """Build conversation messages from history with explicit structure."""
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Add conversation history with explicit formatting
        for msg in history:
            if msg.role == "user":
                messages.append({"role": "user", "content": msg.content})
            elif msg.role == "assistant":
                # Format assistant messages explicitly
                if msg.email_subject and msg.email_body:
                    # Use the exact format we expect
                    content = f"Subject: {msg.email_subject}\n\n{msg.email_body}"
                else:
                    content = msg.content
                messages.append({"role": "assistant", "content": content})

        # Add current user prompt
        messages.append({"role": "user", "content": user_prompt})

        return messages

    async def generate_email(
        self,
        purpose: PurposeEnum,
        details: str,
        length: LengthEnum,
        tone: ToneEnum = None,
        model: str = None,
        history: Optional[list[ChatMessage]] = None,
    ) -> EmailGenerationResponse:
        """Generate an email using OpenRouter API (GPT-5 Nano optimized)."""
        history = history or []
        effective_model = model or self.model

        logger.info(
            "Generating email via OpenRouter (GPT-5 Nano optimized)",
            purpose=purpose.value,
            length=length.value,
            tone=tone.value if tone else None,
            model=effective_model,
            history_length=len(history),
        )

        # Construct the explicit prompt
        user_prompt = construct_generation_prompt(purpose, details, length, tone)

        # Build messages with history
        messages = self._build_conversation_messages(history, user_prompt)

        # Call OpenRouter
        response_text, usage_info = await self._call_openrouter(messages, effective_model)

        # Calculate cost
        cost = self._calculate_cost(usage_info, effective_model)

        # Log raw response for debugging
        logger.info(
            "Raw LLM response received",
            response_length=len(response_text) if response_text else 0,
            tokens_used=usage_info.get("total_tokens", 0),
            cost_usd=cost,
        )

        # Parse the response with stricter validation
        parsed = parse_llm_response(response_text)

        # Validate parsed output
        if not parsed["subject"] or not parsed["body"]:
            logger.warning(
                "LLM returned incomplete email structure",
                has_subject=bool(parsed["subject"]),
                has_body=bool(parsed["body"]),
            )
            # Provide fallback if parsing failed
            if response_text and response_text.strip():
                lines = response_text.strip().split("\n", 1)
                parsed["subject"] = parsed["subject"] or lines[0].strip()
                parsed["body"] = parsed["body"] or (lines[1].strip() if len(lines) > 1 else lines[0].strip())

        logger.info(
            "Email generated successfully",
            subject_length=len(parsed["subject"]),
            body_length=len(parsed["body"]),
        )

        return EmailGenerationResponse(
            subject=parsed["subject"],
            body=parsed["body"],
            usage=UsageInfo(
                prompt_tokens=usage_info.get("prompt_tokens", 0),
                completion_tokens=usage_info.get("completion_tokens", 0),
                total_tokens=usage_info.get("total_tokens", 0),
                cost=cost,
            ),
        )

    async def refine_email(
        self,
        original_subject: str,
        original_body: str,
        feedback: str,
        model: str = None,
        history: Optional[list[ChatMessage]] = None,
    ) -> EmailRefineResponse:
        """Refine an email based on user feedback (GPT-5 Nano optimized)."""
        history = history or []
        effective_model = model or self.model

        logger.info(
            "Refining email via OpenRouter (GPT-5 Nano optimized)",
            feedback_preview=feedback[:50] if len(feedback) > 50 else feedback,
            model=effective_model,
            history_length=len(history),
        )

        # Construct the explicit refinement prompt
        user_prompt = construct_refinement_prompt(original_subject, original_body, feedback)

        # Build messages with history
        messages = self._build_conversation_messages(history, user_prompt)

        # Call OpenRouter
        response_text, usage_info = await self._call_openrouter(messages, effective_model)

        # Calculate cost
        cost = self._calculate_cost(usage_info, effective_model)

        # Parse the response
        parsed = parse_llm_response(response_text)

        logger.info(
            "Email refined successfully",
            subject_length=len(parsed["subject"]),
            body_length=len(parsed["body"]),
            tokens_used=usage_info.get("total_tokens", 0),
            cost_usd=cost,
        )

        return EmailRefineResponse(
            subject=parsed["subject"],
            body=parsed["body"],
            usage=UsageInfo(
                prompt_tokens=usage_info.get("prompt_tokens", 0),
                completion_tokens=usage_info.get("completion_tokens", 0),
                total_tokens=usage_info.get("total_tokens", 0),
                cost=cost,
            ),
        )


# Singleton instance
_llm_service = None


def get_llm_service() -> OpenRouterLLMService:
    """Get the singleton LLM service instance."""
    global _llm_service
    if _llm_service is None:
        _llm_service = OpenRouterLLMService()
    return _llm_service
