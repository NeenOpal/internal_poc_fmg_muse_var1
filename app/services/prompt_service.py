from pathlib import Path
from app.models.email import PurposeEnum, LengthEnum, ToneEnum
from app.evaluation.test_cases import (
    find_similar_conversations,
    get_conversation_for_refinement,
    format_conversation_for_prompt,
)


def load_compliance_rules() -> str:
    """Load compliance rules from rulebook.md file."""
    rulebook_path = Path(__file__).parent.parent.parent / "rulebook.md"
    try:
        return rulebook_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


# Shorter, more direct system prompt for GPT-5 Nano
SYSTEM_PROMPT = """You are an email writer. Generate emails in this exact format:

Subject: [subject line]

[email body with greeting, content, and sign-off]

Rules:
1. Always include both subject and body
2. Match the specified tone and length exactly
3. Use proper email structure: greeting, body, sign-off
4. Use placeholder brackets like [Recipient Name], [Your Name], [Date], [Company Name], [Time], [Location], etc. for any information not explicitly provided by the user
5. Write emails with clear placeholders that users can easily identify and fill in themselves
6. Output ONLY the email - no explanations or commentary"""


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
        "action": "write an email",
        "focus": "Achieve the communication goal specified in the details",
    },
}


# Explicit word count targets for GPT-5 Nano
LENGTH_SPECS = {
    LengthEnum.SHORT: {
        "target": "50-100 words",
        "sentences": "2-4 sentences in body",
        "instruction": "Keep it brief and direct. One short paragraph maximum.",
    },
    LengthEnum.MEDIUM: {
        "target": "100-200 words",
        "sentences": "5-8 sentences in body",
        "instruction": "Provide moderate detail. 2-3 paragraphs.",
    },
    LengthEnum.LONG: {
        "target": "200-400 words",
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
    },
    ToneEnum.FORMAL: {
        "style": "formal and traditional",
        "greeting": "Use a formal greeting like 'Dear [Recipient Name],' or 'Dear Mr./Ms. [Last Name],'",
        "closing": "Use 'Sincerely,' or 'Respectfully,' followed by '[Your Name]'",
        "language": "Respectful, proper titles, no contractions",
    },
    ToneEnum.FRIENDLY: {
        "style": "warm and personable",
        "greeting": "Use a friendly greeting like 'Hi [Recipient Name],' or 'Hey [Recipient Name],'",
        "closing": "Use 'Best,' or 'Warm regards,' followed by '[Your Name]'",
        "language": "Conversational but professional, show genuine interest",
    },
    ToneEnum.CASUAL: {
        "style": "relaxed and conversational",
        "greeting": "Use a casual greeting like 'Hey [Recipient Name],' or 'Hi there,'",
        "closing": "Use 'Thanks,' or 'Cheers,' followed by '[Your Name]'",
        "language": "Natural, contractions okay, like talking to a colleague",
    },
}


def construct_generation_prompt(
    purpose: PurposeEnum,
    details: str,
    length: LengthEnum,
    tone: ToneEnum = None,
    include_examples: bool = True,
    max_examples: int = 1,
) -> str:
    """
    Construct explicit, structured prompt for GPT-5 Nano.

    Args:
        purpose: Email purpose category
        details: User's input/request details
        length: Target email length
        tone: Target tone (defaults to professional)
        include_examples: Whether to include ideal conversation examples
        max_examples: Maximum number of examples to include (1-2 recommended)
    """
    tone = tone or ToneEnum.PROFESSIONAL

    purpose_spec = PURPOSE_INSTRUCTIONS[purpose]
    length_spec = LENGTH_SPECS[length]
    tone_spec = TONE_SPECS[tone]

    # If user input is very brief (under 20 words), add context inference instruction
    is_brief_input = len(details.split()) < 20

    # Build the example section if enabled
    example_section = ""
    if include_examples:
        similar_convos = find_similar_conversations(
            purpose=purpose,
            tone=tone,
            length=length,
            user_input=details,
            max_results=max_examples,
        )
        if similar_convos:
            example_section = "\n=== REFERENCE EXAMPLES ===\n"
            example_section += "Study these ideal examples to understand the expected quality and style:\n\n"
            for conv in similar_convos:
                example_section += format_conversation_for_prompt(conv, include_notes=True)
                example_section += "\n\n---\n\n"

    prompt = f"""TASK: {purpose_spec["action"]}

USER INPUT:
{details}

REQUIREMENTS:
- Purpose: {purpose_spec["focus"]}
- Tone: {tone_spec["style"]}
- Length: {length_spec["target"]} ({length_spec["sentences"]})
- Greeting: {tone_spec["greeting"]}
- Closing: {tone_spec["closing"]}
- Language style: {tone_spec["language"]}

STRUCTURE:
1. First line: Subject line that summarizes the email purpose
2. Skip a line
3. Greeting (e.g., "Hi [Recipient Name],")
4. Body paragraphs ({length_spec["instruction"]})
5. Closing (e.g., "Best regards,")
6. Sign with [Your Name]

{f'''IMPORTANT: The user input is brief. Use placeholders for missing information:
- Use [Recipient Name] for the recipient if not specified
- Use [Your Name] for the sender signature
- Use [Date], [Time], [Location], [Company Name], etc. for other unspecified details
- Make the email complete with clear placeholders that the user can fill in
- Don't make up specific names, dates, or details - use placeholders instead''' if is_brief_input else ''}

OUTPUT FORMAT (follow exactly):
Subject: [your subject line]

[email body with greeting, content, closing]
{example_section}
---

COMPLIANCE WORKFLOW (you MUST follow this process):

1. GENERATE: First, draft the email based on user input above.

2. CHECK: Review your draft against EACH rule in the compliance rulebook below. Go through every rule.

3. FIX: If ANY rule is violated, rewrite the email to fix the violation.

4. OUTPUT: Only output the final compliant email. No explanations, no compliance notes.

COMPLIANCE RULEBOOK:
{load_compliance_rules()}

---

Now generate a compliant email. Output ONLY the final email, nothing else."""

    return prompt


def construct_refinement_prompt(
    original_subject: str,
    original_body: str,
    feedback: str,
    purpose: PurposeEnum = None,
    include_examples: bool = True,
) -> str:
    """
    Construct explicit refinement prompt for GPT-5 Nano.

    Args:
        original_subject: The original email subject
        original_body: The original email body
        feedback: User's refinement request
        purpose: Email purpose (for finding relevant refinement examples)
        include_examples: Whether to include ideal refinement examples
    """
    # Detect refinement type from feedback
    feedback_lower = feedback.lower()
    refinement_type = None
    if any(word in feedback_lower for word in ["shorter", "brief", "concise"]):
        refinement_type = "shorter"
    elif any(word in feedback_lower for word in ["longer", "more detail", "expand", "elaborate"]):
        refinement_type = "more_detail"
    elif any(word in feedback_lower for word in ["formal", "friendly", "casual", "warm", "tone", "stiff"]):
        refinement_type = "tone_change"

    # Build refinement example section
    example_section = ""
    if include_examples and purpose and refinement_type:
        example_conv = get_conversation_for_refinement(purpose, refinement_type)
        if example_conv:
            example_section = "\n=== REFINEMENT EXAMPLE ===\n"
            example_section += "Here's how a similar refinement was handled:\n\n"
            example_section += format_conversation_for_prompt(example_conv, include_notes=True)
            example_section += "\n\n---\n\n"

    prompt = f"""TASK: Rewrite this email based on user's request

ORIGINAL EMAIL:
Subject: {original_subject}

{original_body}

USER REQUEST: {feedback}

INSTRUCTIONS:
1. Apply the user's requested changes exactly
2. Keep the core message and purpose intact
3. If request is for style change (pirate, Gen Z, Shakespeare, etc.), fully embrace that style
4. If request is for length/tone change, adjust accordingly
5. Maintain email structure: subject, greeting, body, closing

COMMON REQUESTS:
- "shorter" = reduce to 50-100 words, keep key points
- "longer" = expand to 200-300 words, add more detail
- "more formal" = use "Dear," "Sincerely," no contractions
- "more casual" = use "Hey," "Thanks," contractions okay
- "add [detail]" = incorporate the specified information
- Fun styles = use appropriate vocabulary for that style

OUTPUT FORMAT (follow exactly):
Subject: [rewritten subject line]

[rewritten email body]
{example_section}
---

COMPLIANCE WORKFLOW (you MUST follow this process):

1. GENERATE: First, rewrite the email based on user feedback above.

2. CHECK: Review your draft against EACH rule in the compliance rulebook below. Go through every rule.

3. FIX: If ANY rule is violated, rewrite the email to fix the violation.

4. OUTPUT: Only output the final compliant email. No explanations, no compliance notes.

COMPLIANCE RULEBOOK:
{load_compliance_rules()}

---

Now generate a compliant revised email. Output ONLY the final email, nothing else."""

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
