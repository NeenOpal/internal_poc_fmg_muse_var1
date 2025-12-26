"""
FMG Muse - Full Pipeline Test Suite
=====================================
Tests the complete email generation pipeline with 100 diverse test cases:
- Generation (all purposes, tones, lengths)
- Compliance checking
- Evaluation
- Refinement

Generates a comprehensive markdown report.
"""

import httpx
import json
import time
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum

# API Configuration
BASE_URL = "http://localhost:8000/api"
TIMEOUT = 120.0  # seconds per request


# ============================================================================
# TEST CASE DEFINITIONS - 100 DIVERSE CASES
# ============================================================================

# Categories of test cases
TEST_CASES = [
    # ==========================================================================
    # CATEGORY 1: RELATIONSHIP BUILDER (15 cases)
    # ==========================================================================
    # Professional tone
    {"id": 1, "type": "generate", "purpose": "relationship_builder", "tone": "professional", "length": "short",
     "details": "Thank a client for their continued trust over 5 years of partnership"},
    {"id": 2, "type": "generate", "purpose": "relationship_builder", "tone": "professional", "length": "medium",
     "details": "Congratulate client on their daughter's wedding and wish them well"},
    {"id": 3, "type": "generate", "purpose": "relationship_builder", "tone": "professional", "length": "long",
     "details": "Welcome letter to new high-net-worth client who transferred $2M portfolio"},

    # Formal tone
    {"id": 4, "type": "generate", "purpose": "relationship_builder", "tone": "formal", "length": "medium",
     "details": "Express condolences to client who lost their spouse recently"},
    {"id": 5, "type": "generate", "purpose": "relationship_builder", "tone": "formal", "length": "long",
     "details": "Celebrate 25-year client anniversary with reflection on partnership journey"},

    # Friendly tone
    {"id": 6, "type": "generate", "purpose": "relationship_builder", "tone": "friendly", "length": "short",
     "details": "Wish happy birthday to long-term client turning 70"},
    {"id": 7, "type": "generate", "purpose": "relationship_builder", "tone": "friendly", "length": "medium",
     "details": "Congratulate client on becoming a grandparent for the first time"},
    {"id": 8, "type": "generate", "purpose": "relationship_builder", "tone": "friendly", "length": "short",
     "details": "Thank client for referring their colleague to our services"},

    # Casual tone
    {"id": 9, "type": "generate", "purpose": "relationship_builder", "tone": "casual", "length": "short",
     "details": "Send holiday greetings to clients before Christmas"},
    {"id": 10, "type": "generate", "purpose": "relationship_builder", "tone": "casual", "length": "short",
     "details": "Congratulate client on their retirement after 40 years of work"},

    # Refinement tests for relationship builder
    {"id": 11, "type": "refine", "original_subject": "Happy Anniversary!",
     "original_body": "Dear Client,\n\nCongratulations on 10 years with us.\n\nBest regards",
     "feedback": "Make it more personal and warm, add specific appreciation"},
    {"id": 12, "type": "refine", "original_subject": "Welcome",
     "original_body": "Hi,\n\nWelcome to our firm. We look forward to working with you.\n\nThanks",
     "feedback": "Make it more formal and comprehensive for a high-net-worth client"},
    {"id": 13, "type": "refine", "original_subject": "Thinking of You",
     "original_body": "Dear Mr. Smith,\n\nI was sorry to hear about your loss.\n\nSincerely",
     "feedback": "Make it more compassionate and offer support without discussing business"},
    {"id": 14, "type": "generate", "purpose": "relationship_builder", "tone": "professional", "length": "medium",
     "details": "Congratulate business owner client on their company going public"},
    {"id": 15, "type": "generate", "purpose": "relationship_builder", "tone": "friendly", "length": "short",
     "details": "Check in with client after they mentioned health issues last meeting"},

    # ==========================================================================
    # CATEGORY 2: EDUCATIONAL CONTENT (20 cases)
    # ==========================================================================
    # Basic investment concepts
    {"id": 16, "type": "generate", "purpose": "educational_content", "tone": "professional", "length": "medium",
     "details": "Explain dollar-cost averaging to clients nervous about market volatility"},
    {"id": 17, "type": "generate", "purpose": "educational_content", "tone": "professional", "length": "long",
     "details": "Explain the difference between traditional and Roth IRA contributions"},
    {"id": 18, "type": "generate", "purpose": "educational_content", "tone": "friendly", "length": "medium",
     "details": "Explain what bonds are and how they work for a new investor"},
    {"id": 19, "type": "generate", "purpose": "educational_content", "tone": "formal", "length": "long",
     "details": "Quarterly market commentary discussing current economic conditions"},

    # High-risk topics requiring disclaimers
    {"id": 20, "type": "generate", "purpose": "educational_content", "tone": "professional", "length": "medium",
     "details": "Explain cryptocurrency investment risks and opportunities"},
    {"id": 21, "type": "generate", "purpose": "educational_content", "tone": "formal", "length": "long",
     "details": "Discuss leveraged ETFs and their risks for sophisticated investors"},
    {"id": 22, "type": "generate", "purpose": "educational_content", "tone": "professional", "length": "medium",
     "details": "Explain options trading basics including risks of loss"},
    {"id": 23, "type": "generate", "purpose": "educational_content", "tone": "professional", "length": "long",
     "details": "Discuss alternative investments like private equity and hedge funds"},

    # Tax and retirement
    {"id": 24, "type": "generate", "purpose": "educational_content", "tone": "professional", "length": "medium",
     "details": "Explain tax-loss harvesting strategy before year end"},
    {"id": 25, "type": "generate", "purpose": "educational_content", "tone": "friendly", "length": "medium",
     "details": "Explain Required Minimum Distributions for client turning 73"},
    {"id": 26, "type": "generate", "purpose": "educational_content", "tone": "professional", "length": "long",
     "details": "Explain Social Security claiming strategies and timing considerations"},
    {"id": 27, "type": "generate", "purpose": "educational_content", "tone": "professional", "length": "medium",
     "details": "Discuss Roth conversion ladder strategy for early retirement"},

    # Specialty topics
    {"id": 28, "type": "generate", "purpose": "educational_content", "tone": "friendly", "length": "medium",
     "details": "Explain ESG/sustainable investing options to interested client"},
    {"id": 29, "type": "generate", "purpose": "educational_content", "tone": "professional", "length": "medium",
     "details": "Explain bond laddering strategy for retirement income"},
    {"id": 30, "type": "generate", "purpose": "educational_content", "tone": "formal", "length": "long",
     "details": "Discuss inflation impact on retirement planning and purchasing power"},

    # Edge cases - requests that may trigger compliance concerns
    {"id": 31, "type": "generate", "purpose": "educational_content", "tone": "professional", "length": "medium",
     "details": "Tell client about a fund that returned 25% last year"},
    {"id": 32, "type": "generate", "purpose": "educational_content", "tone": "professional", "length": "short",
     "details": "Explain why now is a good time to invest in the market"},
    {"id": 33, "type": "generate", "purpose": "educational_content", "tone": "casual", "length": "short",
     "details": "Quick tip about tax-loss harvesting before December 31"},

    # Refinement tests for educational content
    {"id": 34, "type": "refine", "original_subject": "Investment Opportunity",
     "original_body": "Hi,\n\nOur fund returned 20% last year and will continue to perform well.\n\nBest",
     "feedback": "Add proper disclaimers and remove forward-looking guarantees"},
    {"id": 35, "type": "refine", "original_subject": "Understanding Bonds",
     "original_body": "Dear Client,\n\nBonds are loans you make to companies. They pay interest.\n\nRegards",
     "feedback": "Make it longer with more detail about risks and benefits"},

    # ==========================================================================
    # CATEGORY 3: FOLLOW-UP (15 cases)
    # ==========================================================================
    {"id": 36, "type": "generate", "purpose": "follow_up", "tone": "professional", "length": "short",
     "details": "Follow up after quarterly portfolio review meeting last week"},
    {"id": 37, "type": "generate", "purpose": "follow_up", "tone": "friendly", "length": "medium",
     "details": "Check in with client during significant market decline"},
    {"id": 38, "type": "generate", "purpose": "follow_up", "tone": "professional", "length": "medium",
     "details": "Follow up after discussing life insurance needs"},
    {"id": 39, "type": "generate", "purpose": "follow_up", "tone": "friendly", "length": "short",
     "details": "Follow up with prospect after initial consultation meeting"},
    {"id": 40, "type": "generate", "purpose": "follow_up", "tone": "professional", "length": "medium",
     "details": "Check in after client mentioned job change affecting their 401k"},
    {"id": 41, "type": "generate", "purpose": "follow_up", "tone": "casual", "length": "short",
     "details": "Quick check-in with client we haven't heard from in 6 months"},
    {"id": 42, "type": "generate", "purpose": "follow_up", "tone": "professional", "length": "medium",
     "details": "Follow up after estate planning discussion about trust setup"},
    {"id": 43, "type": "generate", "purpose": "follow_up", "tone": "friendly", "length": "medium",
     "details": "Follow up with seminar attendee who expressed interest"},
    {"id": 44, "type": "generate", "purpose": "follow_up", "tone": "professional", "length": "short",
     "details": "Remind client about outstanding paperwork for account opening"},
    {"id": 45, "type": "generate", "purpose": "follow_up", "tone": "formal", "length": "medium",
     "details": "Follow up on beneficiary designation changes discussed last month"},

    # Refinement tests
    {"id": 46, "type": "refine", "original_subject": "Checking In",
     "original_body": "Hi,\n\nJust checking in. Let me know if you need anything.\n\nThanks",
     "feedback": "Make it more specific and add value - reference our last conversation"},
    {"id": 47, "type": "refine", "original_subject": "Market Update",
     "original_body": "Dear Client,\n\nMarkets are down. Don't worry, they always recover.\n\nBest",
     "feedback": "Remove the guarantee about recovery and add balanced perspective"},
    {"id": 48, "type": "generate", "purpose": "follow_up", "tone": "professional", "length": "medium",
     "details": "Follow up after implementing portfolio rebalancing strategy"},
    {"id": 49, "type": "generate", "purpose": "follow_up", "tone": "friendly", "length": "short",
     "details": "Check in with client after their child started college"},
    {"id": 50, "type": "generate", "purpose": "follow_up", "tone": "professional", "length": "medium",
     "details": "Follow up on pending account transfer from previous advisor"},

    # ==========================================================================
    # CATEGORY 4: SCHEDULING (15 cases)
    # ==========================================================================
    {"id": 51, "type": "generate", "purpose": "scheduling", "tone": "professional", "length": "short",
     "details": "Schedule annual portfolio review meeting with client"},
    {"id": 52, "type": "generate", "purpose": "scheduling", "tone": "formal", "length": "medium",
     "details": "Schedule comprehensive financial planning session for new client"},
    {"id": 53, "type": "generate", "purpose": "scheduling", "tone": "friendly", "length": "short",
     "details": "Schedule mid-year check-in call with long-term client"},
    {"id": 54, "type": "generate", "purpose": "scheduling", "tone": "professional", "length": "medium",
     "details": "Schedule year-end tax planning meeting before December"},
    {"id": 55, "type": "generate", "purpose": "scheduling", "tone": "friendly", "length": "medium",
     "details": "Schedule retirement planning discussion for client turning 60"},
    {"id": 56, "type": "generate", "purpose": "scheduling", "tone": "professional", "length": "long",
     "details": "Schedule comprehensive estate planning review with complex needs"},
    {"id": 57, "type": "generate", "purpose": "scheduling", "tone": "casual", "length": "short",
     "details": "Schedule quick call to discuss client's question about their account"},
    {"id": 58, "type": "generate", "purpose": "scheduling", "tone": "professional", "length": "medium",
     "details": "Schedule insurance coverage review meeting"},
    {"id": 59, "type": "generate", "purpose": "scheduling", "tone": "friendly", "length": "medium",
     "details": "Schedule onboarding meeting with newly referred client"},
    {"id": 60, "type": "generate", "purpose": "scheduling", "tone": "formal", "length": "short",
     "details": "Schedule annual beneficiary designation review"},

    # Refinement tests
    {"id": 61, "type": "refine", "original_subject": "Meeting Request",
     "original_body": "Hi,\n\nCan we meet?\n\nThanks",
     "feedback": "Add specific purpose, suggested times, and what to prepare"},
    {"id": 62, "type": "refine", "original_subject": "Annual Review",
     "original_body": "Dear Client,\n\nIt's time for your annual review. Please let me know your availability.\n\nBest",
     "feedback": "Add agenda items and make it more engaging"},
    {"id": 63, "type": "generate", "purpose": "scheduling", "tone": "professional", "length": "medium",
     "details": "Schedule Social Security claiming strategy discussion"},
    {"id": 64, "type": "generate", "purpose": "scheduling", "tone": "friendly", "length": "short",
     "details": "Reschedule meeting that was postponed due to weather"},
    {"id": 65, "type": "generate", "purpose": "scheduling", "tone": "professional", "length": "medium",
     "details": "Schedule quarterly business owner client review"},

    # ==========================================================================
    # CATEGORY 5: FEEDBACK REQUEST (10 cases)
    # ==========================================================================
    {"id": 66, "type": "generate", "purpose": "feedback_request", "tone": "professional", "length": "short",
     "details": "Ask for feedback on new client portal experience"},
    {"id": 67, "type": "generate", "purpose": "feedback_request", "tone": "friendly", "length": "medium",
     "details": "Request feedback after annual review meeting"},
    {"id": 68, "type": "generate", "purpose": "feedback_request", "tone": "formal", "length": "long",
     "details": "Formal annual service satisfaction survey request"},
    {"id": 69, "type": "generate", "purpose": "feedback_request", "tone": "casual", "length": "short",
     "details": "Ask client what they think of our new website"},
    {"id": 70, "type": "generate", "purpose": "feedback_request", "tone": "professional", "length": "medium",
     "details": "Request feedback on account setup and onboarding process"},
    {"id": 71, "type": "generate", "purpose": "feedback_request", "tone": "friendly", "length": "short",
     "details": "Ask if client found our recent seminar helpful"},
    {"id": 72, "type": "generate", "purpose": "feedback_request", "tone": "professional", "length": "medium",
     "details": "Request testimonial from satisfied long-term client"},

    # Refinement tests
    {"id": 73, "type": "refine", "original_subject": "Feedback?",
     "original_body": "Hi,\n\nHow are we doing? Let us know.\n\nThanks",
     "feedback": "Add specific questions and make it easier to respond"},
    {"id": 74, "type": "generate", "purpose": "feedback_request", "tone": "casual", "length": "short",
     "details": "Quick check if client received and understood quarterly statement"},
    {"id": 75, "type": "generate", "purpose": "feedback_request", "tone": "professional", "length": "medium",
     "details": "Ask for feedback on new financial planning tools we introduced"},

    # ==========================================================================
    # CATEGORY 6: OTHER/ADMINISTRATIVE (15 cases)
    # ==========================================================================
    {"id": 76, "type": "generate", "purpose": "other", "tone": "professional", "length": "short",
     "details": "Notify client about updated Form CRS availability"},
    {"id": 77, "type": "generate", "purpose": "other", "tone": "formal", "length": "medium",
     "details": "Inform clients about updated privacy policy"},
    {"id": 78, "type": "generate", "purpose": "other", "tone": "professional", "length": "short",
     "details": "Request updated identification documents for compliance"},
    {"id": 79, "type": "generate", "purpose": "other", "tone": "casual", "length": "medium",
     "details": "Notify clients about holiday office closure and emergency contacts"},
    {"id": 80, "type": "generate", "purpose": "other", "tone": "professional", "length": "short",
     "details": "Notify client about secure document available in portal"},
    {"id": 81, "type": "generate", "purpose": "other", "tone": "professional", "length": "medium",
     "details": "Update client on pending account transfer status"},
    {"id": 82, "type": "generate", "purpose": "other", "tone": "formal", "length": "medium",
     "details": "Announce new team member joining our advisory practice"},
    {"id": 83, "type": "generate", "purpose": "other", "tone": "professional", "length": "short",
     "details": "Confirm receipt of signed documents from client"},
    {"id": 84, "type": "generate", "purpose": "other", "tone": "friendly", "length": "medium",
     "details": "Invite clients to upcoming appreciation dinner event"},
    {"id": 85, "type": "generate", "purpose": "other", "tone": "professional", "length": "short",
     "details": "Notify client their automatic contribution was processed"},

    # Refinement tests
    {"id": 86, "type": "refine", "original_subject": "Document Request",
     "original_body": "Hi,\n\nWe need your updated ID.\n\nThanks",
     "feedback": "Add why it's needed, deadline, and how to submit securely"},
    {"id": 87, "type": "refine", "original_subject": "Office Closed",
     "original_body": "We will be closed next week.\n\nRegards",
     "feedback": "Add specific dates, emergency contact, and holiday wishes"},
    {"id": 88, "type": "generate", "purpose": "other", "tone": "formal", "length": "long",
     "details": "Annual disclosure letter with fee schedule and ADV updates"},
    {"id": 89, "type": "generate", "purpose": "other", "tone": "professional", "length": "medium",
     "details": "Notify clients about system maintenance and temporary portal downtime"},
    {"id": 90, "type": "generate", "purpose": "other", "tone": "friendly", "length": "short",
     "details": "Thank client for completing their annual paperwork"},

    # ==========================================================================
    # CATEGORY 7: EDGE CASES & COMPLIANCE CHALLENGES (10 cases)
    # ==========================================================================
    {"id": 91, "type": "generate", "purpose": "educational_content", "tone": "professional", "length": "medium",
     "details": "Client asked about guaranteed returns on annuity products"},
    {"id": 92, "type": "generate", "purpose": "follow_up", "tone": "professional", "length": "short",
     "details": "Tell client now is the perfect time to buy stocks before they go up"},
    {"id": 93, "type": "generate", "purpose": "educational_content", "tone": "professional", "length": "medium",
     "details": "Explain our fund that has never lost money in 10 years"},
    {"id": 94, "type": "generate", "purpose": "scheduling", "tone": "professional", "length": "short",
     "details": "Urgent meeting needed - client must act now on limited opportunity"},
    {"id": 95, "type": "generate", "purpose": "educational_content", "tone": "professional", "length": "long",
     "details": "Explain high-yield junk bonds paying 12% annual interest"},

    # Refinement with compliance challenges
    {"id": 96, "type": "refine", "original_subject": "Great Opportunity",
     "original_body": "Hi,\n\nThis investment will definitely make you money. Act fast!\n\nBest",
     "feedback": "Make it sound more exciting and urgent"},
    {"id": 97, "type": "refine", "original_subject": "Market Prediction",
     "original_body": "Dear Client,\n\nThe market may experience volatility. Consider your risk tolerance.\n\nRegards",
     "feedback": "Add specific predictions about which stocks will go up"},
    {"id": 98, "type": "generate", "purpose": "educational_content", "tone": "casual", "length": "short",
     "details": "Tell client about crypto that will 10x this year"},
    {"id": 99, "type": "generate", "purpose": "relationship_builder", "tone": "professional", "length": "medium",
     "details": "Celebrate that client's portfolio beat the market by 15% last year"},
    {"id": 100, "type": "generate", "purpose": "educational_content", "tone": "professional", "length": "medium",
     "details": "Explain penny stocks and their potential for huge gains"},
]


@dataclass
class EvaluationResult:
    """Evaluation metrics for a generated email."""
    evaluated: bool = False
    eval_time: float = 0.0
    overall_score: float = 0.0
    pass_threshold: bool = False

    # Individual metric scores (1-10)
    compliance_score: int = 0
    tone_consistency_score: int = 0
    length_accuracy_score: int = 0
    structure_completeness_score: int = 0
    purpose_alignment_score: int = 0
    clarity_score: int = 0
    professionalism_score: int = 0
    personalization_score: int = 0
    risk_balance_score: int = 0
    disclaimer_accuracy_score: int = 0

    # Summary
    strengths: List[str] = field(default_factory=list)
    improvements_needed: List[str] = field(default_factory=list)
    rewrite_recommended: bool = False

    # Error
    eval_error: Optional[str] = None


@dataclass
class TestResult:
    """Result of a single test case."""
    test_id: int
    test_type: str  # generate or refine
    purpose: Optional[str]
    tone: Optional[str]
    length: Optional[str]
    details: Optional[str]
    feedback: Optional[str]

    # Results
    status: str  # PASS, FAIL, ERROR
    response_time: float
    subject: Optional[str] = None
    body: Optional[str] = None
    body_preview: Optional[str] = None
    body_word_count: int = 0

    # Token usage
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost: float = 0.0

    # Error info
    error: Optional[str] = None
    http_status: Optional[int] = None

    # Evaluation results (separate call)
    evaluation: Optional[EvaluationResult] = None


def run_evaluation(client: httpx.Client, result: TestResult, test: Dict) -> EvaluationResult:
    """Run separate evaluation on a generated email."""
    eval_result = EvaluationResult()

    if not result.subject or not result.body:
        eval_result.eval_error = "No email to evaluate"
        return eval_result

    start_time = time.time()

    try:
        response = client.post(
            f"{BASE_URL}/evaluate-email",
            json={
                "subject": result.subject,
                "body": result.body,
                "purpose": test["purpose"],
                "tone": test["tone"],
                "length": test["length"],
                "original_request": test["details"],
            },
            timeout=TIMEOUT,
        )

        eval_result.eval_time = round(time.time() - start_time, 2)

        if response.status_code == 200:
            data = response.json()
            eval_result.evaluated = True
            eval_result.overall_score = data.get("overall_score", 0.0)
            eval_result.pass_threshold = data.get("pass_threshold", False)

            # Individual metrics
            eval_result.compliance_score = data.get("compliance", {}).get("score", 0)
            eval_result.tone_consistency_score = data.get("tone_consistency", {}).get("score", 0)
            eval_result.length_accuracy_score = data.get("length_accuracy", {}).get("score", 0)
            eval_result.structure_completeness_score = data.get("structure_completeness", {}).get("score", 0)
            eval_result.purpose_alignment_score = data.get("purpose_alignment", {}).get("score", 0)
            eval_result.clarity_score = data.get("clarity", {}).get("score", 0)
            eval_result.professionalism_score = data.get("professionalism", {}).get("score", 0)
            eval_result.personalization_score = data.get("personalization", {}).get("score", 0)
            eval_result.risk_balance_score = data.get("risk_balance", {}).get("score", 0)
            eval_result.disclaimer_accuracy_score = data.get("disclaimer_accuracy", {}).get("score", 0)

            # Summary
            eval_result.strengths = data.get("strengths", [])
            eval_result.improvements_needed = data.get("improvements_needed", [])
            eval_result.rewrite_recommended = data.get("rewrite_recommended", False)
        else:
            eval_result.eval_error = f"HTTP {response.status_code}"

    except Exception as e:
        eval_result.eval_time = round(time.time() - start_time, 2)
        eval_result.eval_error = str(e)[:100]

    return eval_result


def run_generate_test(client: httpx.Client, test: Dict, run_eval: bool = True) -> TestResult:
    """Run a generation test case."""
    start_time = time.time()

    result = TestResult(
        test_id=test["id"],
        test_type="generate",
        purpose=test["purpose"],
        tone=test["tone"],
        length=test["length"],
        details=test["details"],
        feedback=None,
        status="PENDING",
        response_time=0,
    )

    try:
        response = client.post(
            f"{BASE_URL}/generate-email",
            json={
                "purpose": test["purpose"],
                "tone": test["tone"],
                "length": test["length"],
                "details": test["details"],
            },
            timeout=TIMEOUT,
        )

        result.response_time = round(time.time() - start_time, 2)
        result.http_status = response.status_code

        if response.status_code == 200:
            data = response.json()
            result.subject = data.get("subject", "")
            body = data.get("body", "")
            result.body = body
            result.body_preview = body[:200] + "..." if len(body) > 200 else body
            result.body_word_count = len(body.split())

            # Usage info
            usage = data.get("usage", {})
            result.prompt_tokens = usage.get("prompt_tokens", 0)
            result.completion_tokens = usage.get("completion_tokens", 0)
            result.total_tokens = usage.get("total_tokens", 0)
            result.cost = usage.get("cost", 0.0)

            # Basic validation
            if result.subject and result.body_word_count > 10:
                result.status = "PASS"
            else:
                result.status = "FAIL"
                result.error = "Empty or too short response"

            # Run separate evaluation
            if run_eval and result.status == "PASS":
                result.evaluation = run_evaluation(client, result, test)
        else:
            result.status = "ERROR"
            result.error = f"HTTP {response.status_code}: {response.text[:200]}"

    except Exception as e:
        result.response_time = round(time.time() - start_time, 2)
        result.status = "ERROR"
        result.error = str(e)[:200]

    return result


def run_refine_test(client: httpx.Client, test: Dict) -> TestResult:
    """Run a refinement test case."""
    start_time = time.time()

    result = TestResult(
        test_id=test["id"],
        test_type="refine",
        purpose=None,
        tone=None,
        length=None,
        details=None,
        feedback=test["feedback"],
        status="PENDING",
        response_time=0,
    )

    try:
        response = client.post(
            f"{BASE_URL}/refine-email",
            json={
                "original_subject": test["original_subject"],
                "original_body": test["original_body"],
                "feedback": test["feedback"],
            },
            timeout=TIMEOUT,
        )

        result.response_time = round(time.time() - start_time, 2)
        result.http_status = response.status_code

        if response.status_code == 200:
            data = response.json()
            result.subject = data.get("subject", "")
            body = data.get("body", "")
            result.body_preview = body[:200] + "..." if len(body) > 200 else body
            result.body_word_count = len(body.split())

            # Usage info
            usage = data.get("usage", {})
            result.prompt_tokens = usage.get("prompt_tokens", 0)
            result.completion_tokens = usage.get("completion_tokens", 0)
            result.total_tokens = usage.get("total_tokens", 0)
            result.cost = usage.get("cost", 0.0)

            # Check if refinement actually changed the email
            original_body = test["original_body"]
            if body != original_body and len(body) > len(original_body) * 0.5:
                result.status = "PASS"
            else:
                result.status = "FAIL"
                result.error = "Refinement did not significantly change the email"
        else:
            result.status = "ERROR"
            result.error = f"HTTP {response.status_code}: {response.text[:200]}"

    except Exception as e:
        result.response_time = round(time.time() - start_time, 2)
        result.status = "ERROR"
        result.error = str(e)[:200]

    return result


def run_all_tests() -> List[TestResult]:
    """Run all test cases and return results."""
    results = []

    print("=" * 80)
    print("FMG MUSE - FULL PIPELINE TEST SUITE")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total Test Cases: {len(TEST_CASES)}")
    print("=" * 80)
    print()

    with httpx.Client() as client:
        for i, test in enumerate(TEST_CASES):
            test_id = test["id"]
            test_type = test["type"]

            if test_type == "generate":
                desc = f"{test['purpose']}/{test['tone']}/{test['length']}"
                print(f"[{i+1:3d}/100] Test #{test_id}: GENERATE - {desc}")
                print(f"          Details: {test['details'][:60]}...")
                result = run_generate_test(client, test)
            else:
                print(f"[{i+1:3d}/100] Test #{test_id}: REFINE")
                print(f"          Feedback: {test['feedback'][:60]}...")
                result = run_refine_test(client, test)

            results.append(result)

            # Print result
            if result.status == "PASS":
                eval_info = ""
                if result.evaluation and result.evaluation.evaluated:
                    e = result.evaluation
                    eval_status = "PASS" if e.pass_threshold else "FAIL"
                    eval_info = f" | Eval: {eval_status} ({e.overall_score:.1f}/10, Compliance: {e.compliance_score}/10)"
                print(f"          PASS - {result.response_time}s - {result.body_word_count} words - ${result.cost:.4f}{eval_info}")
            elif result.status == "FAIL":
                print(f"          FAIL - {result.response_time}s - {result.error}")
            else:
                print(f"          ERROR - {result.response_time}s - {result.error}")

            print()

            # Small delay between requests
            time.sleep(0.5)

    return results


def generate_report(results: List[TestResult], start_time: datetime, end_time: datetime) -> str:
    """Generate comprehensive markdown report."""

    total_time = (end_time - start_time).total_seconds()

    # Calculate statistics
    total = len(results)
    passed = sum(1 for r in results if r.status == "PASS")
    failed = sum(1 for r in results if r.status == "FAIL")
    errors = sum(1 for r in results if r.status == "ERROR")

    pass_rate = (passed / total * 100) if total > 0 else 0

    # Token and cost totals
    total_prompt_tokens = sum(r.prompt_tokens for r in results)
    total_completion_tokens = sum(r.completion_tokens for r in results)
    total_tokens = sum(r.total_tokens for r in results)
    total_cost = sum(r.cost for r in results)

    # Response time stats
    response_times = [r.response_time for r in results if r.response_time > 0]
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    min_response_time = min(response_times) if response_times else 0
    max_response_time = max(response_times) if response_times else 0

    # Word count stats
    word_counts = [r.body_word_count for r in results if r.body_word_count > 0]
    avg_word_count = sum(word_counts) / len(word_counts) if word_counts else 0

    # By test type
    generate_results = [r for r in results if r.test_type == "generate"]
    refine_results = [r for r in results if r.test_type == "refine"]

    generate_passed = sum(1 for r in generate_results if r.status == "PASS")
    refine_passed = sum(1 for r in refine_results if r.status == "PASS")

    # By purpose (for generate tests)
    purposes = {}
    for r in generate_results:
        p = r.purpose or "unknown"
        if p not in purposes:
            purposes[p] = {"total": 0, "passed": 0, "failed": 0, "errors": 0, "times": [], "costs": []}
        purposes[p]["total"] += 1
        if r.status == "PASS":
            purposes[p]["passed"] += 1
        elif r.status == "FAIL":
            purposes[p]["failed"] += 1
        else:
            purposes[p]["errors"] += 1
        purposes[p]["times"].append(r.response_time)
        purposes[p]["costs"].append(r.cost)

    # By tone
    tones = {}
    for r in generate_results:
        t = r.tone or "unknown"
        if t not in tones:
            tones[t] = {"total": 0, "passed": 0, "failed": 0, "errors": 0}
        tones[t]["total"] += 1
        if r.status == "PASS":
            tones[t]["passed"] += 1
        elif r.status == "FAIL":
            tones[t]["failed"] += 1
        else:
            tones[t]["errors"] += 1

    # By length
    lengths = {}
    for r in generate_results:
        l = r.length or "unknown"
        if l not in lengths:
            lengths[l] = {"total": 0, "passed": 0, "failed": 0, "errors": 0, "word_counts": []}
        lengths[l]["total"] += 1
        if r.status == "PASS":
            lengths[l]["passed"] += 1
        elif r.status == "FAIL":
            lengths[l]["failed"] += 1
        else:
            lengths[l]["errors"] += 1
        if r.body_word_count > 0:
            lengths[l]["word_counts"].append(r.body_word_count)

    # Build report
    report = f"""# FMG Muse - Full Pipeline Test Report

**Generated:** {end_time.strftime('%Y-%m-%d %H:%M:%S')}

---

## Executive Summary

| Metric | Value |
|--------|-------|
| **Total Test Cases** | {total} |
| **Passed** | {passed} ({pass_rate:.1f}%) |
| **Failed** | {failed} ({failed/total*100:.1f}%) |
| **Errors** | {errors} ({errors/total*100:.1f}%) |
| **Total Duration** | {total_time:.1f} seconds |
| **Average Response Time** | {avg_response_time:.2f} seconds |
| **Total Cost** | ${total_cost:.4f} |

---

## Performance Metrics

### Response Time

| Metric | Value |
|--------|-------|
| Average | {avg_response_time:.2f}s |
| Minimum | {min_response_time:.2f}s |
| Maximum | {max_response_time:.2f}s |
| Total Test Duration | {total_time:.1f}s |

### Token Usage

| Metric | Count |
|--------|-------|
| Prompt Tokens | {total_prompt_tokens:,} |
| Completion Tokens | {total_completion_tokens:,} |
| Total Tokens | {total_tokens:,} |
| Avg Tokens/Request | {total_tokens//total if total > 0 else 0:,} |

### Cost Analysis

| Metric | Value |
|--------|-------|
| Total Cost | ${total_cost:.4f} |
| Average Cost/Request | ${total_cost/total:.6f} |
| Cost/1000 Requests | ${(total_cost/total)*1000:.4f} |

---

## Results by Test Type

| Type | Total | Passed | Failed | Errors | Pass Rate |
|------|-------|--------|--------|--------|-----------|
| Generate | {len(generate_results)} | {generate_passed} | {sum(1 for r in generate_results if r.status=='FAIL')} | {sum(1 for r in generate_results if r.status=='ERROR')} | {generate_passed/len(generate_results)*100:.1f}% |
| Refine | {len(refine_results)} | {refine_passed} | {sum(1 for r in refine_results if r.status=='FAIL')} | {sum(1 for r in refine_results if r.status=='ERROR')} | {refine_passed/len(refine_results)*100 if refine_results else 0:.1f}% |

---

## Results by Purpose (Generation Tests)

| Purpose | Total | Passed | Failed | Errors | Pass Rate | Avg Time | Avg Cost |
|---------|-------|--------|--------|--------|-----------|----------|----------|
"""

    for purpose, stats in sorted(purposes.items()):
        avg_time = sum(stats["times"]) / len(stats["times"]) if stats["times"] else 0
        avg_cost = sum(stats["costs"]) / len(stats["costs"]) if stats["costs"] else 0
        pass_pct = stats["passed"] / stats["total"] * 100 if stats["total"] > 0 else 0
        report += f"| {purpose} | {stats['total']} | {stats['passed']} | {stats['failed']} | {stats['errors']} | {pass_pct:.1f}% | {avg_time:.2f}s | ${avg_cost:.4f} |\n"

    report += """
---

## Results by Tone

| Tone | Total | Passed | Failed | Errors | Pass Rate |
|------|-------|--------|--------|--------|-----------|
"""

    for tone, stats in sorted(tones.items()):
        pass_pct = stats["passed"] / stats["total"] * 100 if stats["total"] > 0 else 0
        report += f"| {tone} | {stats['total']} | {stats['passed']} | {stats['failed']} | {stats['errors']} | {pass_pct:.1f}% |\n"

    report += """
---

## Results by Length

| Length | Total | Passed | Failed | Errors | Pass Rate | Avg Words |
|--------|-------|--------|--------|--------|-----------|-----------|
"""

    for length, stats in sorted(lengths.items()):
        pass_pct = stats["passed"] / stats["total"] * 100 if stats["total"] > 0 else 0
        avg_words = sum(stats["word_counts"]) / len(stats["word_counts"]) if stats["word_counts"] else 0
        report += f"| {length} | {stats['total']} | {stats['passed']} | {stats['failed']} | {stats['errors']} | {pass_pct:.1f}% | {avg_words:.0f} |\n"

    # ==========================================================================
    # EVALUATION RESULTS SECTION
    # ==========================================================================
    evaluated_results = [r for r in results if r.evaluation and r.evaluation.evaluated]

    if evaluated_results:
        eval_passed = sum(1 for r in evaluated_results if r.evaluation.pass_threshold)
        eval_failed = len(evaluated_results) - eval_passed

        # Calculate average scores
        avg_overall = sum(r.evaluation.overall_score for r in evaluated_results) / len(evaluated_results)
        avg_compliance = sum(r.evaluation.compliance_score for r in evaluated_results) / len(evaluated_results)
        avg_tone = sum(r.evaluation.tone_consistency_score for r in evaluated_results) / len(evaluated_results)
        avg_length = sum(r.evaluation.length_accuracy_score for r in evaluated_results) / len(evaluated_results)
        avg_structure = sum(r.evaluation.structure_completeness_score for r in evaluated_results) / len(evaluated_results)
        avg_purpose = sum(r.evaluation.purpose_alignment_score for r in evaluated_results) / len(evaluated_results)
        avg_clarity = sum(r.evaluation.clarity_score for r in evaluated_results) / len(evaluated_results)
        avg_professionalism = sum(r.evaluation.professionalism_score for r in evaluated_results) / len(evaluated_results)
        avg_personalization = sum(r.evaluation.personalization_score for r in evaluated_results) / len(evaluated_results)
        avg_risk = sum(r.evaluation.risk_balance_score for r in evaluated_results) / len(evaluated_results)
        avg_disclaimer = sum(r.evaluation.disclaimer_accuracy_score for r in evaluated_results) / len(evaluated_results)

        avg_eval_time = sum(r.evaluation.eval_time for r in evaluated_results) / len(evaluated_results)

        report += f"""
---

## Evaluation Results (Separate LLM Evaluation)

This section shows results from the **separate evaluation endpoint** that independently assesses generated emails.

### Evaluation Summary

| Metric | Value |
|--------|-------|
| **Emails Evaluated** | {len(evaluated_results)} |
| **Passed Threshold (7.0+)** | {eval_passed} ({eval_passed/len(evaluated_results)*100:.1f}%) |
| **Failed Threshold** | {eval_failed} ({eval_failed/len(evaluated_results)*100:.1f}%) |
| **Average Overall Score** | {avg_overall:.2f}/10 |
| **Average Eval Time** | {avg_eval_time:.2f}s |

### Individual Metric Averages

| Metric | Average Score | Status |
|--------|---------------|--------|
| Compliance | {avg_compliance:.1f}/10 | {"✓" if avg_compliance >= 7 else "⚠"} |
| Tone Consistency | {avg_tone:.1f}/10 | {"✓" if avg_tone >= 7 else "⚠"} |
| Length Accuracy | {avg_length:.1f}/10 | {"✓" if avg_length >= 7 else "⚠"} |
| Structure Completeness | {avg_structure:.1f}/10 | {"✓" if avg_structure >= 7 else "⚠"} |
| Purpose Alignment | {avg_purpose:.1f}/10 | {"✓" if avg_purpose >= 7 else "⚠"} |
| Clarity | {avg_clarity:.1f}/10 | {"✓" if avg_clarity >= 7 else "⚠"} |
| Professionalism | {avg_professionalism:.1f}/10 | {"✓" if avg_professionalism >= 7 else "⚠"} |
| Personalization | {avg_personalization:.1f}/10 | {"✓" if avg_personalization >= 7 else "⚠"} |
| Risk Balance | {avg_risk:.1f}/10 | {"✓" if avg_risk >= 7 else "⚠"} |
| Disclaimer Accuracy | {avg_disclaimer:.1f}/10 | {"✓" if avg_disclaimer >= 7 else "⚠"} |

### Evaluation by Purpose

| Purpose | Evaluated | Passed | Failed | Avg Score | Avg Compliance |
|---------|-----------|--------|--------|-----------|----------------|
"""
        # Evaluation by purpose
        eval_by_purpose = {}
        for r in evaluated_results:
            p = r.purpose or "unknown"
            if p not in eval_by_purpose:
                eval_by_purpose[p] = {"total": 0, "passed": 0, "scores": [], "compliance": []}
            eval_by_purpose[p]["total"] += 1
            if r.evaluation.pass_threshold:
                eval_by_purpose[p]["passed"] += 1
            eval_by_purpose[p]["scores"].append(r.evaluation.overall_score)
            eval_by_purpose[p]["compliance"].append(r.evaluation.compliance_score)

        for purpose, stats in sorted(eval_by_purpose.items()):
            avg_score = sum(stats["scores"]) / len(stats["scores"]) if stats["scores"] else 0
            avg_comp = sum(stats["compliance"]) / len(stats["compliance"]) if stats["compliance"] else 0
            failed = stats["total"] - stats["passed"]
            report += f"| {purpose} | {stats['total']} | {stats['passed']} | {failed} | {avg_score:.1f} | {avg_comp:.1f} |\n"

        # Evaluation failures detail
        eval_failures = [r for r in evaluated_results if not r.evaluation.pass_threshold]
        if eval_failures:
            report += """
### Evaluation Failures Detail

| ID | Purpose | Score | Compliance | Top Issues |
|----|---------|-------|------------|------------|
"""
            for r in eval_failures[:15]:  # Limit to 15
                issues = ", ".join(r.evaluation.improvements_needed[:2]) if r.evaluation.improvements_needed else "N/A"
                issues = issues[:50] + "..." if len(issues) > 50 else issues
                report += f"| {r.test_id} | {r.purpose} | {r.evaluation.overall_score:.1f} | {r.evaluation.compliance_score} | {issues} |\n"

        # Rewrite recommendations
        rewrite_recommended = [r for r in evaluated_results if r.evaluation.rewrite_recommended]
        if rewrite_recommended:
            report += f"""
### Emails Recommended for Rewrite

{len(rewrite_recommended)} emails were flagged as needing a complete rewrite:

"""
            for r in rewrite_recommended[:10]:
                report += f"- Test #{r.test_id}: {r.purpose} - Score: {r.evaluation.overall_score:.1f}\n"

    # Failed tests
    failed_tests = [r for r in results if r.status == "FAIL"]
    if failed_tests:
        report += """
---

## Failed Tests

| ID | Type | Purpose | Tone | Error |
|----|------|---------|------|-------|
"""
        for r in failed_tests:
            purpose = r.purpose or "N/A"
            tone = r.tone or "N/A"
            error = (r.error or "Unknown")[:50]
            report += f"| {r.test_id} | {r.test_type} | {purpose} | {tone} | {error} |\n"

    # Error tests
    error_tests = [r for r in results if r.status == "ERROR"]
    if error_tests:
        report += """
---

## Error Tests

| ID | Type | HTTP Status | Error |
|----|------|-------------|-------|
"""
        for r in error_tests:
            http_status = r.http_status or "N/A"
            error = (r.error or "Unknown")[:60]
            report += f"| {r.test_id} | {r.test_type} | {http_status} | {error} |\n"

    # Sample outputs
    passed_tests = [r for r in results if r.status == "PASS"][:5]
    if passed_tests:
        report += """
---

## Sample Successful Outputs

"""
        for r in passed_tests:
            report += f"""### Test #{r.test_id} - {r.test_type.upper()}

**Subject:** {r.subject}

**Body Preview:**
```
{r.body_preview}
```

**Stats:** {r.body_word_count} words | {r.response_time}s | ${r.cost:.4f}

---

"""

    # Conclusions
    report += f"""
## Conclusions

### Overall Assessment

"""

    if pass_rate >= 90:
        report += "**EXCELLENT:** The pipeline is performing very well with a high pass rate.\n\n"
    elif pass_rate >= 75:
        report += "**GOOD:** The pipeline is functioning well with room for improvement.\n\n"
    elif pass_rate >= 50:
        report += "**NEEDS ATTENTION:** The pipeline has significant issues that should be addressed.\n\n"
    else:
        report += "**CRITICAL:** The pipeline has major issues requiring immediate attention.\n\n"

    report += f"""### Key Findings

1. **Pass Rate:** {pass_rate:.1f}% of tests passed successfully
2. **Performance:** Average response time of {avg_response_time:.2f} seconds per request
3. **Cost Efficiency:** Average cost of ${total_cost/total:.6f} per request
4. **Token Usage:** Average of {total_tokens//total if total > 0 else 0:,} tokens per request

### Recommendations

"""

    if failed + errors > 0:
        report += f"- Investigate the {failed + errors} failed/error tests\n"
    if avg_response_time > 30:
        report += "- Consider optimizing for faster response times\n"
    if any(stats["passed"] / stats["total"] < 0.7 for stats in purposes.values() if stats["total"] > 0):
        report += "- Some purposes have lower pass rates - review generation prompts\n"

    report += f"""
---

*Report generated by FMG Muse Full Pipeline Test Suite*
*Total runtime: {total_time:.1f} seconds*
"""

    return report


def main():
    """Main entry point."""
    start_time = datetime.now()

    # Run all tests
    results = run_all_tests()

    end_time = datetime.now()

    # Generate report
    print("\n" + "=" * 80)
    print("Generating Report...")
    print("=" * 80)

    report = generate_report(results, start_time, end_time)

    # Save report
    report_filename = f"pipeline_test_report_{start_time.strftime('%Y%m%d_%H%M%S')}.md"
    with open(report_filename, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\nReport saved to: {report_filename}")

    # Save raw results as JSON
    json_filename = f"pipeline_test_results_{start_time.strftime('%Y%m%d_%H%M%S')}.json"
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump([asdict(r) for r in results], f, indent=2)

    print(f"Raw results saved to: {json_filename}")

    # Print summary
    total = len(results)
    passed = sum(1 for r in results if r.status == "PASS")
    failed = sum(1 for r in results if r.status == "FAIL")
    errors = sum(1 for r in results if r.status == "ERROR")

    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    print(f"Total Tests:  {total}")
    print(f"Passed:       {passed} ({passed/total*100:.1f}%)")
    print(f"Failed:       {failed} ({failed/total*100:.1f}%)")
    print(f"Errors:       {errors} ({errors/total*100:.1f}%)")
    print(f"Total Time:   {(end_time - start_time).total_seconds():.1f} seconds")
    print(f"Total Cost:   ${sum(r.cost for r in results):.4f}")
    print("=" * 80)


if __name__ == "__main__":
    main()
