from app.models.email import PurposeEnum, LengthEnum, ToneEnum


# High-risk topics that require mandatory verbatim disclaimers
HIGH_RISK_TOPICS = {
    "crypto": {
        "keywords": ["crypto", "bitcoin", "ethereum", "blockchain", "digital asset", "defi", "cryptocurrency"],
        "required_disclaimers": [
            "Cryptocurrency is highly volatile and speculative.",
            "You could lose some or all of your invested capital.",
            "Digital assets are not suitable for all investors."
        ]
    },
    "tax": {
        "keywords": ["tax", "deduction", "harvesting", "irs", "filing", "capital gains", "tax-loss"],
        "required_disclaimers": [
            "This is not tax advice.",
            "Consult a qualified tax professional for your specific situation.",
            "Tax implications vary based on individual circumstances."
        ]
    },
    "insurance": {
        "keywords": ["insurance", "life insurance", "annuity", "annuities", "policy", "coverage", "premium"],
        "required_disclaimers": [
            "Insurance products vary by state and carrier.",
            "Please review policy documents for complete details.",
            "Recommendations depend on individual suitability analysis."
        ]
    },
    "retirement": {
        "keywords": ["retirement", "401k", "401(k)", "ira", "pension", "social security", "rmd", "retire"],
        "required_disclaimers": [
            "Retirement planning depends on individual circumstances.",
            "Contribution limits and rules may change.",
            "Consult a financial professional for personalized guidance."
        ]
    }
}


def detect_high_risk_topics(details: str) -> list:
    """
    Detect high-risk topics in user input and return required disclaimers.
    Returns a list of dicts with topic name and required disclaimer phrases.
    """
    found_topics = []
    details_lower = details.lower()
    for topic_name, topic_info in HIGH_RISK_TOPICS.items():
        if any(kw in details_lower for kw in topic_info["keywords"]):
            found_topics.append({
                "topic": topic_name,
                "disclaimers": topic_info["required_disclaimers"]
            })
    return found_topics


# System prompt with embedded compliance rules for financial advisor communications
SYSTEM_PROMPT = """You are an email writer for financial advisors. Generate compliant, professional emails.

OUTPUT FORMAT:
Subject: [subject line]

[email body with greeting, content, and sign-off]

GENERAL RULES:
1. Always include both subject and body
2. Match the specified tone and length exactly
3. Use proper email structure: greeting, body, sign-off
4. Use placeholder brackets like [Recipient Name], [Your Name], [Date], [Company Name], [Time], [Location], etc. for any information not explicitly provided by the user
5. Write emails with clear placeholders that users can easily identify and fill in themselves
6. Output ONLY the email - no explanations or commentary

COMPLIANCE RULES (MUST FOLLOW):
You must ensure all generated emails comply with FINRA, SEC, and financial communication regulations:

1. NO GUARANTEES: Never promise or guarantee investment returns. Avoid words like "guaranteed," "risk-free," "certain to," "will definitely."

2. PAST PERFORMANCE: If mentioning historical performance, always include: "Past performance does not guarantee future results." Include time periods and note that principal value may fluctuate.

3. FORWARD-LOOKING: Use qualifying language for any predictions or outlooks: "we believe," "in our opinion," "our outlook suggests." Never state predictions as certainties.

4. NO PRESSURE TACTICS: Avoid false urgency. Don't use "act now," "limited time," "exclusive opportunity" unless there's a genuine, stated deadline with specific reasons.

5. BALANCED RISK: If discussing investment benefits, also mention risks with equal prominence. Don't minimize or hide risks.

6. NO SPECIFIC PREDICTIONS: Never predict specific returns, prices, or numerical outcomes. Avoid "will return X%," "expect Y% gains."

7. DISCLOSURES: If recommending products or services, note that individual circumstances vary and suitability depends on personal financial situation.

8. SUBJECT LINES: Must accurately reflect content. Never use misleading "RE:" or "FWD:" unless genuine. Avoid "guaranteed," "urgent," or "risk-free."

9. TESTIMONIALS: If referencing client experiences, note that results may not be representative of all clients.

10. FEES: If discussing costs, be transparent. Note that complete fee information is available upon request.

BEFORE OUTPUTTING: Mentally verify your email follows all compliance rules above. If any rule is violated, fix it before outputting."""


# Simplified purpose descriptions for clearer instructions
PURPOSE_INSTRUCTIONS = {
    PurposeEnum.RELATIONSHIP_BUILDER: {
        "action": "write a relationship-building email",
        "focus": "Express appreciation, check in warmly, or strengthen the connection",
    },
    PurposeEnum.EDUCATIONAL_CONTENT: {
        "action": "write an educational email",
        "focus": "Explain a concept clearly or share valuable information",
    },
    PurposeEnum.FOLLOW_UP: {
        "action": "write a follow-up email",
        "focus": "Reference previous communication and request an update or action",
    },
    PurposeEnum.FEEDBACK_REQUEST: {
        "action": "write a feedback request email",
        "focus": "Ask for specific input, opinions, or suggestions politely",
    },
    PurposeEnum.SCHEDULING: {
        "action": "write a scheduling email",
        "focus": "Request or confirm meeting time, provide availability, or schedule an appointment",
    },
    PurposeEnum.OTHER: {
        "action": "write a compliant business email",
        "focus": "Achieve the specified goal while maintaining professional standards. Include a clear subject line, proper greeting, well-structured body, and professional closing. When in doubt, use more formal language and include appropriate disclaimers.",
        "structure_emphasis": True,
    },
}


# Explicit word count targets for GPT-5 Nano
# Includes extended targets when disclaimers are required (+25 words)
LENGTH_SPECS = {
    LengthEnum.SHORT: {
        "target": "50-100 words",
        "target_with_disclaimers": "75-125 words",
        "sentences": "2-4 sentences in body",
        "instruction": "Keep it brief and direct. One short paragraph maximum.",
    },
    LengthEnum.MEDIUM: {
        "target": "100-200 words",
        "target_with_disclaimers": "125-225 words",
        "sentences": "5-8 sentences in body",
        "instruction": "Provide moderate detail. 2-3 paragraphs.",
    },
    LengthEnum.LONG: {
        "target": "200-400 words",
        "target_with_disclaimers": "225-425 words",
        "sentences": "9-15 sentences in body",
        "instruction": "Provide comprehensive detail. 3-5 paragraphs.",
    },
}


# Precise tone specifications (use placeholder for recipient name if not provided)
TONE_SPECS = {
    ToneEnum.PROFESSIONAL: {
        "style": "professional and business-appropriate",
        "greeting": "Use a professional greeting like 'Hi [Recipient Name],' or 'Hello [Recipient Name],'",
        "closing": "Use 'Best regards,' or 'Thank you,' followed by '[Your Name]'",
        "language": "Clear, direct, respectful",
        "compliance_note": "",
    },
    ToneEnum.FORMAL: {
        "style": "formal and traditional",
        "greeting": "Use a formal greeting like 'Dear [Recipient Name],' or 'Dear Mr./Ms. [Last Name],'",
        "closing": "Use 'Sincerely,' or 'Respectfully,' followed by '[Your Name]'",
        "language": "Respectful, proper titles, no contractions",
        "compliance_note": "",
    },
    ToneEnum.FRIENDLY: {
        "style": "warm and personable",
        "greeting": "Use a friendly greeting like 'Hi [Recipient Name],' or 'Hey [Recipient Name],'",
        "closing": "Use 'Best,' or 'Warm regards,' followed by '[Your Name]'",
        "language": "Conversational but professional, show genuine interest",
        "compliance_note": "",
    },
    ToneEnum.CASUAL: {
        "style": "relaxed and conversational",
        "greeting": "Use a casual greeting like 'Hey [Recipient Name],' or 'Hi there,'",
        "closing": "Use 'Thanks,' or 'Cheers,' followed by '[Your Name]'",
        "language": "Natural, contractions okay, like talking to a colleague",
        "compliance_note": "IMPORTANT: Even with casual tone, you MUST include all required disclaimers and compliance language exactly as specified. Disclaimers cannot be omitted or softened for casual emails.",
    },
}


def construct_generation_prompt(
    purpose: PurposeEnum,
    details: str,
    length: LengthEnum,
    tone: ToneEnum = None
) -> str:
    """
    Construct explicit, structured prompt with compliance checks.
    Now includes topic detection and mandatory verbatim disclaimers.
    """
    tone = tone or ToneEnum.PROFESSIONAL

    purpose_spec = PURPOSE_INSTRUCTIONS[purpose]
    length_spec = LENGTH_SPECS[length]
    tone_spec = TONE_SPECS[tone]

    # Detect high-risk topics that require mandatory disclaimers
    high_risk_topics = detect_high_risk_topics(details)

    # Use extended word count if disclaimers are required
    if high_risk_topics:
        word_target = length_spec.get("target_with_disclaimers", length_spec["target"])
    else:
        word_target = length_spec["target"]

    # If user input is very brief (under 20 words), add context inference instruction
    is_brief_input = len(details.split()) < 20

    # Build mandatory disclaimers section if high-risk topics detected
    disclaimer_section = ""
    if high_risk_topics:
        disclaimer_section = "\n\nMANDATORY DISCLAIMERS (MUST include these EXACT phrases in the email):\n"
        disclaimer_section += "WARNING: Email will be REJECTED if these disclaimers are missing or paraphrased.\n\n"
        for topic in high_risk_topics:
            disclaimer_section += f"For {topic['topic'].upper()} content, include ALL of these:\n"
            for disc in topic['disclaimers']:
                disclaimer_section += f'  - "{disc}"\n'
            disclaimer_section += "\n"

    # Get compliance note for tone (especially important for casual)
    compliance_note = tone_spec.get("compliance_note", "")
    compliance_note_section = f"\n{compliance_note}\n" if compliance_note else ""

    # Extra structure guidance for "other" category
    structure_emphasis = ""
    if purpose_spec.get("structure_emphasis"):
        structure_emphasis = """
EXTRA STRUCTURE GUIDANCE (for general/administrative emails):
- Ensure the subject line clearly states the email's purpose
- Use a complete greeting with recipient placeholder
- Organize body content logically with clear purpose
- Include all necessary details or placeholders
- End with a clear call-to-action if applicable
- Use a professional closing even for simple notifications
"""

    prompt = f"""TASK: {purpose_spec["action"]}

USER INPUT:
{details}
{disclaimer_section}
REQUIREMENTS:
- Purpose: {purpose_spec["focus"]}
- Tone: {tone_spec["style"]}
- Length: {word_target} ({length_spec["sentences"]})
- Greeting: {tone_spec["greeting"]}
- Closing: {tone_spec["closing"]}
- Language style: {tone_spec["language"]}
{compliance_note_section}
STRUCTURE:
1. First line: Subject line that summarizes the email purpose
2. Skip a line
3. Greeting (e.g., "Hi [Recipient Name],")
4. Body paragraphs ({length_spec["instruction"]})
5. Closing (e.g., "Best regards,")
6. Sign with [Your Name]
{structure_emphasis}
{f'''IMPORTANT: The user input is brief. Use placeholders for missing information:
- Use [Recipient Name] for the recipient if not specified
- Use [Your Name] for the sender signature
- Use [Date], [Time], [Location], [Company Name], etc. for other unspecified details
- Make the email complete with clear placeholders that the user can fill in
- Don't make up specific names, dates, or details - use placeholders instead''' if is_brief_input else ''}

OUTPUT FORMAT (follow exactly):
Subject: [your subject line]

[email body with greeting, content, closing]

COMPLIANCE CHECK (REQUIRED - email will be REJECTED if these fail):
[ ] No words: "guaranteed", "risk-free", "certain", "will definitely", "cannot lose"
[ ] No specific return predictions: "will return X%", "expect Y% gains"
[ ] No false urgency: "act now", "limited time" (unless genuine deadline with reason)
[ ] Forward-looking uses: "we believe", "in our opinion", "may", "could"
[ ] If benefits mentioned, risks mentioned with EQUAL prominence
[ ] All MANDATORY DISCLAIMERS included verbatim (if any listed above)
[ ] Subject line accurately reflects content, no misleading RE:/FWD:

Write the compliant email now. No explanations."""

    return prompt


def construct_refinement_prompt(
    original_subject: str,
    original_body: str,
    feedback: str
) -> str:
    """
    Construct explicit refinement prompt with compliance checks.
    Now includes topic detection for mandatory disclaimers.
    """
    # Detect high-risk topics in the original email content
    combined_content = f"{original_subject} {original_body} {feedback}"
    high_risk_topics = detect_high_risk_topics(combined_content)

    # Build mandatory disclaimers section if high-risk topics detected
    disclaimer_section = ""
    if high_risk_topics:
        disclaimer_section = "\n\nMANDATORY DISCLAIMERS (MUST be preserved or added in refined email):\n"
        for topic in high_risk_topics:
            disclaimer_section += f"For {topic['topic'].upper()} content, include ALL of these:\n"
            for disc in topic['disclaimers']:
                disclaimer_section += f'  - "{disc}"\n'
            disclaimer_section += "\n"

    prompt = f"""TASK: Rewrite this email based on user's request

ORIGINAL EMAIL:
Subject: {original_subject}

{original_body}

USER REQUEST: {feedback}
{disclaimer_section}
INSTRUCTIONS:
1. Apply the user's requested changes exactly
2. Keep the core message and purpose intact
3. If request is for style change (pirate, Gen Z, Shakespeare, etc.), fully embrace that style
4. If request is for length/tone change, adjust accordingly
5. Maintain email structure: subject, greeting, body, closing
6. PRESERVE all compliance disclaimers from the original email
7. If changing to casual tone, keep all disclaimers intact (just use simpler surrounding language)

COMMON REQUESTS:
- "shorter" = reduce to 50-100 words, keep key points AND all disclaimers
- "longer" = expand to 200-300 words, add more detail
- "more formal" = use "Dear," "Sincerely," no contractions
- "more casual" = use "Hey," "Thanks," contractions okay, BUT keep disclaimers
- "add [detail]" = incorporate the specified information
- Fun styles = use appropriate vocabulary for that style

OUTPUT FORMAT (follow exactly):
Subject: [rewritten subject line]

[rewritten email body]

COMPLIANCE CHECK (REQUIRED - email will be REJECTED if these fail):
[ ] No words: "guaranteed", "risk-free", "certain", "will definitely", "cannot lose"
[ ] No specific return predictions: "will return X%", "expect Y% gains"
[ ] No false urgency: "act now", "limited time" (unless genuine deadline with reason)
[ ] Forward-looking uses: "we believe", "in our opinion", "may", "could"
[ ] If benefits mentioned, risks mentioned with EQUAL prominence
[ ] All MANDATORY DISCLAIMERS preserved or included verbatim
[ ] Subject line accurately reflects content, no misleading RE:/FWD:

Write the compliant revised email now. No explanations."""

    return prompt


def parse_llm_response(response: str) -> dict:
    """
    Parse LLM response with stricter validation for GPT-5 Nano output.
    """
    if not response or not response.strip():
        return {"subject": "", "body": ""}

    response = response.strip()

    # Remove any markdown code blocks if present
    if response.startswith("```"):
        lines = response.split("\n")
        # Remove first and last lines if they're markdown fences
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        response = "\n".join(lines).strip()

    subject = ""
    body = ""

    # Try to find "Subject:" line (case-insensitive)
    lines = response.split("\n")
    subject_found = False
    body_lines = []

    for i, line in enumerate(lines):
        line_lower = line.lower().strip()

        # Check if this line contains the subject
        if not subject_found and line_lower.startswith("subject:"):
            # Extract subject
            subject = line.split(":", 1)[1].strip() if ":" in line else line.strip()
            subject_found = True
            # Everything after this is body (skip the next empty line if present)
            body_start = i + 1
            if body_start < len(lines) and not lines[body_start].strip():
                body_start += 1
            body_lines = lines[body_start:]
            break

    # If subject found, join remaining lines as body
    if subject_found:
        body = "\n".join(body_lines).strip()
    else:
        # Fallback: treat first line as subject, rest as body
        if lines:
            subject = lines[0].strip()
            # Remove "Subject:" prefix if it's there
            if subject.lower().startswith("subject:"):
                subject = subject.split(":", 1)[1].strip()
            body = "\n".join(lines[1:]).strip()

    return {
        "subject": subject,
        "body": body
    }
